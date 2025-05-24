# ARC-Eval CI/CD Integration Templates

This directory contains pre-built CI/CD pipeline templates for integrating ARC-Eval into your development workflow.

## 🚀 Quick Setup

### GitHub Actions

1. **Copy the template:**
   ```bash
   mkdir -p .github/workflows
   cp ci-templates/github-actions.yml .github/workflows/arc-eval.yml
   ```

2. **Configure for your project:**
   - Replace sample data generation with your actual agent output collection
   - Set up required secrets (see Configuration section below)
   - Customize domains and evaluation criteria

3. **Commit and push:**
   ```bash
   git add .github/workflows/arc-eval.yml
   git commit -m "Add ARC-Eval compliance checking"
   git push
   ```

## 📋 Features

### Automated Compliance Checking
- **Multi-domain evaluation**: Tests finance, security, and ML compliance simultaneously
- **Pull request integration**: Automatically evaluates changes and comments on PRs
- **Artifact preservation**: Saves detailed reports for audit trails
- **Critical failure detection**: Fails CI/CD pipeline on compliance violations

### Reporting & Notifications
- **Detailed logs**: Verbose output with timing metrics
- **Multiple formats**: JSON, PDF, and CSV exports
- **PR comments**: Inline compliance status updates
- **Compliance summary**: Aggregated results across all domains

### Flexible Triggers
- **Push events**: Automatic evaluation on main/develop branches
- **Pull requests**: Pre-merge compliance validation
- **Manual triggers**: On-demand evaluation via workflow_dispatch
- **Scheduled monitoring**: Optional weekly compliance audits

## ⚙️ Configuration

### Required Secrets (Optional)

If you're integrating with external agent APIs, set these in your repository settings:

```bash
# GitHub Settings > Secrets and Variables > Actions
AGENT_API_TOKEN=your_agent_api_token_here
AGENT_API_URL=https://your-agent-api.com
PROD_API_TOKEN=production_api_token
PROD_API_URL=https://prod-agent-api.com
```

### Customization Options

#### 1. Input Data Sources

**Option A: Static Files**
```yaml
- name: Prepare agent outputs
  run: |
    # Use committed output files
    cp test-data/agent_outputs_finance.json ./
```

**Option B: API Integration**
```yaml
- name: Fetch agent outputs
  run: |
    curl -H "Authorization: Bearer ${{ secrets.AGENT_API_TOKEN }}" \
         "${{ secrets.AGENT_API_URL }}/outputs?domain=finance" \
         -o agent_outputs_finance.json
```

**Option C: Generated During CI**
```yaml
- name: Run agent and capture outputs
  run: |
    python scripts/run_agent.py --output agent_outputs_finance.json
```

#### 2. Domain Selection

Customize which domains to evaluate:

```yaml
strategy:
  matrix:
    domain: [finance]  # Only finance
    # domain: [finance, security, ml]  # All domains
    # domain: [security]  # Only security
```

#### 3. Failure Tolerance

**Strict Mode (Fail on Any Critical Issue):**
```yaml
- name: Fail on critical compliance violations
  if: steps.arc-eval.outputs.critical_failures != '0'
  run: exit 1
```

**Warning Mode (Allow Critical Issues):**
```yaml
- name: Warn on critical compliance violations
  if: steps.arc-eval.outputs.critical_failures != '0'
  run: echo "::warning::Critical compliance issues detected"
```

#### 4. Scheduled Monitoring

Enable weekly compliance checks:

```yaml
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
```

## 📊 Understanding Results

### Exit Codes
- `0`: All evaluations passed
- `1`: Critical compliance failures detected
- `2`: Configuration or input errors

### Artifacts Generated
- `agent_eval_{domain}_{timestamp}.json` - Detailed results
- `agent_eval_{domain}_{timestamp}.pdf` - Audit report
- `agent_eval_{domain}_{timestamp}.csv` - Data analysis format
- `arc_eval_output.log` - Complete execution logs

### PR Comments
The workflow automatically adds comments to pull requests showing:
- ✅ Compliance status per domain
- ❌ Critical failure counts
- 📊 Links to detailed reports
- 🔍 Truncated evaluation output

## 🎯 Example Workflows

### 1. Pre-Merge Validation
```yaml
# Runs on every PR to main
# Blocks merge if critical failures found
on:
  pull_request:
    branches: [ main ]
```

### 2. Production Monitoring
```yaml
# Weekly check of production agent outputs
on:
  schedule:
    - cron: '0 2 * * 0'  # Sunday 2 AM
```

### 3. Release Gate
```yaml
# Required check before creating releases
on:
  push:
    tags: [ 'v*' ]
```

## 🛠️ Troubleshooting

### Common Issues

**1. No agent outputs found**
```bash
Error: File not found: agent_outputs_finance.json
```
**Solution:** Ensure your data preparation step creates the required files.

**2. Authentication failures**
```bash
Error: 401 Unauthorized
```
**Solution:** Verify API tokens are correctly set in repository secrets.

**3. Large output truncation**
```bash
Warning: Large input detected (>10MB)
```
**Solution:** Consider processing outputs in smaller batches or using streaming.

### Debug Mode

Enable verbose output for troubleshooting:

```yaml
- name: Debug ARC-Eval
  run: |
    arc-eval --domain finance --input outputs.json --verbose --timing
```

## 📈 Advanced Integrations

### Slack Notifications
```yaml
- name: Notify Slack on failures
  if: failure()
  uses: 8398a7/action-slack@v3
  with:
    status: failure
    text: "ARC-Eval compliance check failed"
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Teams Integration
```yaml
- name: Notify Microsoft Teams
  if: failure()
  uses: aliencube/microsoft-teams-actions@v0.8.0
  with:
    webhook_uri: ${{ secrets.MS_TEAMS_WEBHOOK }}
    title: "Compliance Failure"
    text: "Critical compliance violations detected"
```

### Jira Issue Creation
```yaml
- name: Create Jira Issue
  if: steps.arc-eval.outputs.critical_failures != '0'
  uses: atlassian/gajira-create@master
  with:
    project: COMPLIANCE
    issuetype: Bug
    summary: "Critical compliance failures in ${{ matrix.domain }}"
```

## 📚 Best Practices

1. **Start Simple**: Begin with basic file-based evaluation
2. **Gradual Integration**: Add domains incrementally
3. **Monitor Performance**: Use `--timing` flag to track evaluation speed
4. **Archive Reports**: Preserve compliance reports for audit trails
5. **Team Training**: Ensure team understands compliance requirements
6. **Regular Updates**: Keep ARC-Eval package updated for latest scenarios

## 🔄 Maintenance

### Updating ARC-Eval
```yaml
- name: Install latest ARC-Eval
  run: |
    pip install --upgrade arc-eval
    arc-eval --version
```

### Version Pinning (Recommended)
```yaml
- name: Install specific ARC-Eval version
  run: |
    pip install arc-eval==0.1.0
```

---

For more information, see the [ARC-Eval documentation](https://github.com/arc-computer/arc-eval) or run `arc-eval --help`.