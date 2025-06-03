# CI/CD Integration

Integrate ARC-Eval into your continuous integration and deployment pipelines to ensure agent reliability at every stage of development.

## Overview

ARC-Eval provides multiple integration patterns for CI/CD systems:

- **Reliability Gates**: Block deployments based on risk assessment
- **Automated Testing**: Run compliance checks on every commit
- **Progressive Deployment**: Gradual rollout based on reliability scores
- **Monitoring Integration**: Continuous reliability monitoring in production

## GitHub Actions

### Basic Reliability Check

```yaml
name: Agent Reliability Check
on: [push, pull_request]

jobs:
  reliability-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install ARC-Eval
        run: pip install arc-eval
        
      - name: Run Reliability Analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          arc-eval debug --input agent_outputs.json --no-interactive --output-format json > results.json
          
      - name: Check Risk Level
        run: |
          risk_level=$(jq -r '.reliability_prediction.risk_level' results.json)
          if [ "$risk_level" = "HIGH" ]; then
            echo "High reliability risk detected - blocking deployment"
            exit 1
          fi
          echo "Reliability check passed: $risk_level risk"
```

### Advanced Pipeline with Compliance

```yaml
name: Comprehensive Agent Testing
on: [push, pull_request]

jobs:
  agent-testing:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        domain: [finance, security, ml]
        
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install Dependencies
        run: |
          pip install arc-eval
          pip install -r requirements.txt
          
      - name: Generate Agent Outputs
        run: python scripts/generate_test_outputs.py --domain ${{ matrix.domain }}
        
      - name: Run Debug Analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          arc-eval debug --input outputs_${{ matrix.domain }}.json \
            --no-interactive --output-format json > debug_results_${{ matrix.domain }}.json
            
      - name: Run Compliance Check
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          arc-eval compliance --domain ${{ matrix.domain }} \
            --input outputs_${{ matrix.domain }}.json \
            --no-interactive --export json > compliance_results_${{ matrix.domain }}.json
            
      - name: Evaluate Results
        run: |
          python scripts/evaluate_results.py \
            --debug debug_results_${{ matrix.domain }}.json \
            --compliance compliance_results_${{ matrix.domain }}.json \
            --domain ${{ matrix.domain }}
            
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: reliability-results-${{ matrix.domain }}
          path: |
            debug_results_${{ matrix.domain }}.json
            compliance_results_${{ matrix.domain }}.json
```

### Deployment Gate

```yaml
name: Production Deployment
on:
  push:
    branches: [main]

jobs:
  reliability-gate:
    runs-on: ubuntu-latest
    outputs:
      deploy-approved: ${{ steps.gate.outputs.approved }}
      risk-level: ${{ steps.gate.outputs.risk_level }}
      
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install ARC-Eval
        run: pip install arc-eval
        
      - name: Generate Production Test Data
        run: python scripts/generate_production_test_data.py
        
      - name: Comprehensive Reliability Check
        id: gate
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # Run complete analysis
          arc-eval analyze --input production_test_outputs.json \
            --domain finance --no-interactive --output-format json > analysis.json
            
          # Extract key metrics
          risk_level=$(jq -r '.reliability_prediction.risk_level' analysis.json)
          confidence=$(jq -r '.reliability_prediction.confidence' analysis.json)
          pass_rate=$(jq -r '.compliance_summary.pass_rate' analysis.json)
          
          echo "risk_level=$risk_level" >> $GITHUB_OUTPUT
          echo "confidence=$confidence" >> $GITHUB_OUTPUT
          echo "pass_rate=$pass_rate" >> $GITHUB_OUTPUT
          
          # Deployment approval logic
          if [ "$risk_level" = "LOW" ] && [ "$(echo "$pass_rate > 0.9" | bc)" = "1" ]; then
            echo "approved=true" >> $GITHUB_OUTPUT
            echo "✅ Deployment approved: LOW risk, ${pass_rate}% pass rate"
          else
            echo "approved=false" >> $GITHUB_OUTPUT
            echo "❌ Deployment blocked: $risk_level risk, ${pass_rate}% pass rate"
            exit 1
          fi

  deploy:
    needs: reliability-gate
    if: needs.reliability-gate.outputs.deploy-approved == 'true'
    runs-on: ubuntu-latest
    
    steps:
      - name: Deploy to Production
        run: |
          echo "Deploying with reliability approval"
          echo "Risk Level: ${{ needs.reliability-gate.outputs.risk-level }}"
          # Your deployment commands here
```

## GitLab CI

### Basic Pipeline

```yaml
# .gitlab-ci.yml
stages:
  - test
  - reliability
  - deploy

variables:
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip/

reliability-check:
  stage: reliability
  image: python:3.9
  before_script:
    - pip install arc-eval
  script:
    - arc-eval debug --input agent_outputs.json --no-interactive --output-format json > results.json
    - |
      risk_level=$(jq -r '.reliability_prediction.risk_level' results.json)
      if [ "$risk_level" = "HIGH" ]; then
        echo "High reliability risk detected"
        exit 1
      fi
  artifacts:
    reports:
      junit: results.json
    paths:
      - results.json
    expire_in: 1 week
  only:
    - merge_requests
    - main
```

### Multi-Domain Testing

```yaml
.reliability-template: &reliability-template
  stage: reliability
  image: python:3.9
  before_script:
    - pip install arc-eval
  script:
    - arc-eval compliance --domain $DOMAIN --input outputs.json --no-interactive --export json > compliance_$DOMAIN.json
    - python scripts/check_compliance.py --domain $DOMAIN --results compliance_$DOMAIN.json
  artifacts:
    paths:
      - compliance_$DOMAIN.json
    expire_in: 1 week

reliability-finance:
  <<: *reliability-template
  variables:
    DOMAIN: finance

reliability-security:
  <<: *reliability-template
  variables:
    DOMAIN: security

reliability-ml:
  <<: *reliability-template
  variables:
    DOMAIN: ml
```

## Jenkins

### Declarative Pipeline

```groovy
pipeline {
    agent any
    
    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install arc-eval'
            }
        }
        
        stage('Generate Test Data') {
            steps {
                sh 'python scripts/generate_agent_outputs.py'
            }
        }
        
        stage('Reliability Analysis') {
            parallel {
                stage('Debug Analysis') {
                    steps {
                        sh '''
                            arc-eval debug --input agent_outputs.json \
                                --no-interactive --output-format json > debug_results.json
                        '''
                    }
                }
                
                stage('Compliance Check') {
                    steps {
                        sh '''
                            arc-eval compliance --domain finance \
                                --input agent_outputs.json \
                                --no-interactive --export json > compliance_results.json
                        '''
                    }
                }
            }
        }
        
        stage('Evaluate Results') {
            steps {
                script {
                    def debugResults = readJSON file: 'debug_results.json'
                    def riskLevel = debugResults.reliability_prediction.risk_level
                    
                    if (riskLevel == 'HIGH') {
                        error("High reliability risk detected - blocking deployment")
                    }
                    
                    echo "Reliability check passed: ${riskLevel} risk"
                }
            }
        }
        
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'echo "Deploying to production..."'
                // Your deployment commands
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.json', fingerprint: true
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: '.',
                reportFiles: 'compliance_results.json',
                reportName: 'Reliability Report'
            ])
        }
    }
}
```

## Azure DevOps

### Pipeline YAML

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.9'

stages:
- stage: ReliabilityCheck
  displayName: 'Agent Reliability Check'
  jobs:
  - job: ReliabilityAnalysis
    displayName: 'Run Reliability Analysis'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Use Python $(pythonVersion)'
      
    - script: |
        pip install arc-eval
      displayName: 'Install ARC-Eval'
      
    - script: |
        arc-eval debug --input agent_outputs.json --no-interactive --output-format json > debug_results.json
      env:
        ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
      displayName: 'Run Debug Analysis'
      
    - script: |
        arc-eval compliance --domain finance --input agent_outputs.json --no-interactive --export json > compliance_results.json
      env:
        ANTHROPIC_API_KEY: $(ANTHROPIC_API_KEY)
      displayName: 'Run Compliance Check'
      
    - task: PowerShell@2
      inputs:
        targetType: 'inline'
        script: |
          $results = Get-Content debug_results.json | ConvertFrom-Json
          $riskLevel = $results.reliability_prediction.risk_level
          
          if ($riskLevel -eq "HIGH") {
            Write-Host "##vso[task.logissue type=error]High reliability risk detected"
            exit 1
          }
          
          Write-Host "Reliability check passed: $riskLevel risk"
      displayName: 'Evaluate Results'
      
    - task: PublishTestResults@2
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'compliance_results.json'
      displayName: 'Publish Results'
```

## Docker Integration

### Dockerfile for CI

```dockerfile
FROM python:3.9-slim

# Install ARC-Eval
RUN pip install arc-eval

# Copy agent outputs
COPY agent_outputs.json /app/
WORKDIR /app

# Run reliability check
CMD ["arc-eval", "debug", "--input", "agent_outputs.json", "--no-interactive"]
```

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  reliability-test:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    volumes:
      - ./agent_outputs.json:/app/agent_outputs.json
      - ./results:/app/results
    command: >
      sh -c "
        arc-eval debug --input agent_outputs.json --no-interactive --output-format json > results/debug.json &&
        arc-eval compliance --domain finance --input agent_outputs.json --no-interactive --export json > results/compliance.json
      "
```

## Kubernetes Integration

### Job for Reliability Testing

```yaml
# reliability-check-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: agent-reliability-check
spec:
  template:
    spec:
      containers:
      - name: reliability-checker
        image: your-registry/arc-eval:latest
        env:
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: anthropic-key
        command:
        - /bin/sh
        - -c
        - |
          arc-eval analyze --input /data/agent_outputs.json --domain finance --no-interactive --output-format json > /results/analysis.json
          if [ "$(jq -r '.reliability_prediction.risk_level' /results/analysis.json)" = "HIGH" ]; then
            exit 1
          fi
        volumeMounts:
        - name: agent-data
          mountPath: /data
        - name: results
          mountPath: /results
      volumes:
      - name: agent-data
        configMap:
          name: agent-test-data
      - name: results
        emptyDir: {}
      restartPolicy: Never
  backoffLimit: 3
```

## Monitoring and Alerting

### Prometheus Metrics

```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import json

# Define metrics
reliability_checks_total = Counter('arc_eval_reliability_checks_total', 'Total reliability checks', ['risk_level'])
reliability_check_duration = Histogram('arc_eval_reliability_check_duration_seconds', 'Time spent on reliability checks')
current_risk_score = Gauge('arc_eval_current_risk_score', 'Current agent risk score')

def record_reliability_check(results_file):
    """Record reliability check metrics."""
    with open(results_file) as f:
        results = json.load(f)
    
    risk_level = results['reliability_prediction']['risk_level']
    risk_score = results['reliability_prediction']['combined_risk_score']
    
    reliability_checks_total.labels(risk_level=risk_level).inc()
    current_risk_score.set(risk_score)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Agent Reliability Monitoring",
    "panels": [
      {
        "title": "Risk Level Distribution",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (risk_level) (arc_eval_reliability_checks_total)"
          }
        ]
      },
      {
        "title": "Risk Score Over Time",
        "type": "graph",
        "targets": [
          {
            "expr": "arc_eval_current_risk_score"
          }
        ]
      }
    ]
  }
}
```

## Best Practices

### 1. Environment-Specific Configuration

```yaml
# config/ci.yaml
default_domain: finance
interactive_mode: false
output_format: json

api:
  anthropic:
    model: claude-3-5-haiku-20241022  # Faster model for CI
  
performance:
  batch_threshold: 10
  timeout: 300
```

### 2. Result Caching

```bash
# Cache results to speed up repeated runs
export ARC_EVAL_CACHE_DIR="/tmp/arc-eval-cache"
arc-eval debug --input outputs.json --no-interactive
```

### 3. Parallel Testing

```yaml
# Run multiple domains in parallel
strategy:
  matrix:
    domain: [finance, security, ml]
  max-parallel: 3
```

### 4. Failure Handling

```bash
# Graceful failure handling
set +e  # Don't exit on error
arc-eval debug --input outputs.json --no-interactive --output-format json > results.json
exit_code=$?

if [ $exit_code -ne 0 ]; then
  echo "Reliability check failed with exit code $exit_code"
  # Send notification, create issue, etc.
fi
```

### 5. Security

```yaml
# Use secrets for API keys
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

# Limit permissions
permissions:
  contents: read
  checks: write
```

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Use batch processing and appropriate delays
2. **Timeout Issues**: Increase timeout values for large datasets
3. **Memory Issues**: Process outputs in smaller batches
4. **Network Issues**: Implement retry logic with exponential backoff

### Debug Commands

```bash
# Enable verbose logging
export ARC_EVAL_LOG_LEVEL=DEBUG
arc-eval debug --input outputs.json --verbose

# Check configuration
arc-eval --help

# Validate input format
python -m json.tool agent_outputs.json
```

## Next Steps

- [Compliance Guide](compliance.md) - Regulatory framework integration
- [Monitoring Guide](monitoring.md) - Production monitoring setup
- [API Reference](../api/) - Programmatic integration
- [Examples](../../examples/integration/) - Complete integration examples
