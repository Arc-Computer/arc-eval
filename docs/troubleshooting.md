# Troubleshooting & FAQ Guide

Common issues, solutions, and optimization strategies for ARC-Eval developers.

## Quick Diagnostics

```bash
# Check installation and basic functionality
arc-eval --version
arc-eval --help

# Test with sample data
arc-eval compliance --domain finance --quick-start

# Validate API connectivity
arc-eval debug --input examples/sample-data/finance_outputs.json --verbose
```

## Common Issues

### 1. Installation & Setup

**❌ Command not found: arc-eval**
```bash
# Solution: Ensure proper installation
pip install arc-eval
# or
pip install -e .  # For development

# Verify installation
which arc-eval
arc-eval --version
```

**❌ API Key Issues**
```bash
Error: ANTHROPIC_API_KEY environment variable not set
```

**Solutions:**
```bash
# Set API key
export ANTHROPIC_API_KEY="your-key-here"

# Or use .env file
cp .env.example .env
# Edit .env with your keys

# Verify API connectivity
arc-eval debug --input examples/sample-data/finance_outputs.json --verbose
```

**❌ Permission Denied**
```bash
# Solution: Fix permissions
chmod +x $(which arc-eval)

# Or reinstall with user permissions
pip install --user arc-eval
```

### 2. Input & File Issues

**❌ File Not Found**
```bash
Error: File not found: agent_outputs.json
```

**Solutions:**
```bash
# Check current directory
pwd
ls -la *.json

# Use absolute path
arc-eval debug --input /full/path/to/file.json

# Use example data for testing
arc-eval debug --input examples/sample-data/finance_outputs.json

# Auto-scan for JSON files
arc-eval compliance --domain finance --folder-scan
```

**❌ Invalid JSON Format**
```bash
Error: Invalid JSON in input file
```

**Solutions:**
```bash
# Validate JSON syntax
python -m json.tool your_file.json

# Check for common issues
cat your_file.json | head -10  # Check first 10 lines
cat your_file.json | tail -10  # Check last 10 lines

# Fix common JSON issues
sed -i 's/,$//' your_file.json  # Remove trailing commas
sed -i 's/"/"/g' your_file.json  # Fix smart quotes
```

**❌ Framework Detection Failed**
```bash
Warning: Could not detect framework, using generic parser
```

**Solutions:**
```bash
# Specify framework explicitly
arc-eval debug --input outputs.json --framework langchain

# Check supported frameworks
arc-eval export-guide

# Validate output format
arc-eval export-guide --framework your_framework
```

### 3. API & Performance Issues

**❌ API Rate Limiting**
```bash
Error: 429 Too Many Requests
```

**Solutions:**
```bash
# Enable batch processing
export AGENT_EVAL_BATCH_MODE="true"

# Set cost threshold for model switching
export AGENT_EVAL_COST_THRESHOLD="5.0"

# Use quick mode (no agent-judge)
arc-eval compliance --domain finance --input outputs.json --quick

# Process in smaller batches
split -l 100 large_file.json batch_
for file in batch_*; do
  arc-eval debug --input $file --no-interactive
  sleep 5  # Rate limiting delay
done
```

**❌ Slow Performance**
```bash
# Large datasets taking too long
```

**Solutions:**
```bash
# Enable batch mode for 608+ scenarios
arc-eval compliance --domain finance --input large_outputs.json
# Automatic batch processing with 50% cost savings

# Use quick mode for faster evaluation
arc-eval analyze --input outputs.json --domain finance --quick

# Process in parallel
parallel -j 4 arc-eval debug --input {} ::: file1.json file2.json file3.json file4.json

# Monitor performance
time arc-eval compliance --domain finance --input outputs.json --verbose
```

**❌ Memory Issues**
```bash
Error: MemoryError or system slowdown
```

**Solutions:**
```bash
# Process smaller batches
split -l 500 large_file.json chunk_
for chunk in chunk_*; do
  arc-eval debug --input $chunk --export json
done

# Use streaming for large datasets
arc-eval compliance --domain finance --input outputs.json --no-interactive

# Monitor memory usage
/usr/bin/time -v arc-eval debug --input outputs.json
```

### 4. Framework-Specific Issues

**LangChain Issues:**
```bash
# Common: Complex chain structures not parsed
# Solution: Ensure intermediate_steps are included
{
  "intermediate_steps": [...],
  "llm_output": {...},
  "output": "final response"
}

# Performance: Abstraction overhead detected
# Solution: Use LCEL for better performance
arc-eval debug --input langchain_outputs.json --framework langchain
```

**CrewAI Issues:**
```bash
# Common: Agent delegation timeouts
# Solution: Implement custom timeouts
{
  "crew_output": {...},
  "task_results": [...],
  "agent_performance": {...}
}

# Performance: >30s response times
# Solution: Optimize agent coordination
arc-eval debug --input crewai_outputs.json --framework crewai
```

**OpenAI Issues:**
```bash
# Common: Function calling not captured
# Solution: Include tool_calls in output
{
  "choices": [{
    "message": {...},
    "tool_calls": [...]
  }]
}

# Cost: High token usage
# Solution: Use GPT-4.1-mini for simple tasks
export OPENAI_MODEL="gpt-4.1-mini-2025-04-14"
```

### 5. Prediction & Evaluation Issues

**❌ Low Confidence Predictions**
```bash
Warning: Prediction confidence < 60%
```

**Solutions:**
```bash
# Add more configuration details
{
  "agent": {"type": "finance_assistant", "version": "1.0"},
  "validation": {"enabled": true, "pii_detection": true},
  "security": {"encryption": true, "access_control": true},
  "compliance": {"frameworks": ["SOX", "GDPR"]}
}

# Use supported frameworks
arc-eval debug --input outputs.json --framework langchain

# Check API connectivity
arc-eval debug --input outputs.json --verbose
```

**❌ Inconsistent Predictions**
```bash
# High variance across repeated runs
```

**Solutions:**
```bash
# Use deterministic settings
export ANTHROPIC_MODEL="claude-3-5-haiku-20241022"  # Consistent model
export LLM_TEMPERATURE="0"  # Deterministic responses

# Add more specific configuration
# Test during stable periods
# Validate with domain experts
```

**❌ Unexpected Risk Levels**
```bash
# Risk level doesn't match expectations
```

**Solutions:**
```bash
# Review expected outcomes
cat examples/prediction-testing/expected-outcomes.json

# Validate configuration completeness
arc-eval debug --input config.json --verbose

# Check against reference configurations
diff config.json examples/prediction-testing/good-configs/finance-compliant.json
```

## Performance Optimization

### 1. Cost Optimization

```bash
# Enable automatic model switching
export AGENT_EVAL_COST_THRESHOLD="10.0"  # Switch after $10

# Use batch processing for large datasets
export AGENT_EVAL_BATCH_MODE="true"  # 50% cost savings

# Use faster models for simple tasks
export ANTHROPIC_MODEL="claude-3-5-haiku-20241022"  # Fast default
export OPENAI_MODEL="gpt-4.1-mini-2025-04-14"      # Fast default

# Monitor costs
arc-eval compliance --domain finance --input outputs.json --verbose
```

### 2. Speed Optimization

```bash
# Use quick mode (no agent-judge)
arc-eval compliance --domain finance --input outputs.json --quick

# Process in parallel
parallel -j 4 arc-eval debug --input {} ::: *.json

# Enable caching
export AGENT_EVAL_CACHE_TTL="3600"  # 1 hour cache

# Use targeted scenarios
arc-eval compliance --domain finance --input outputs.json --scenarios fin_001,fin_002
```

### 3. Memory Optimization

```bash
# Process smaller batches
split -l 1000 large_file.json batch_

# Use streaming evaluation
arc-eval compliance --domain finance --input outputs.json --no-interactive

# Clear cache periodically
rm -rf ~/.arc-eval/cache/*
```

## CI/CD Integration Issues

### 1. GitHub Actions

**❌ Authentication Failures**
```yaml
# Solution: Set repository secrets
- name: ARC-Eval Compliance
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: arc-eval compliance --domain finance --input outputs.json
```

**❌ Large Output Truncation**
```yaml
# Solution: Use artifacts for large reports
- name: Upload Reports
  uses: actions/upload-artifact@v4
  with:
    name: compliance-reports
    path: "*.pdf"
```

### 2. Exit Code Handling

```bash
# Handle exit codes properly
arc-eval analyze --input outputs.json --domain finance --no-interactive
exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo "✅ Compliance check passed"
elif [ $exit_code -eq 1 ]; then
  echo "❌ Critical failures detected"
  exit 1
else
  echo "⚠️ Evaluation error"
  exit $exit_code
fi
```

## Debug Mode & Logging

### 1. Enable Verbose Output

```bash
# Detailed logging
arc-eval debug --input outputs.json --verbose

# Timing information
arc-eval compliance --domain finance --input outputs.json --verbose --timing

# Framework detection details
arc-eval debug --input outputs.json --framework-agnostic --verbose
```

### 2. Log Analysis

```bash
# Check evaluation logs
tail -f ~/.arc-eval/logs/evaluation.log

# Monitor API usage
grep "API_CALL" ~/.arc-eval/logs/evaluation.log

# Track performance metrics
grep "TIMING" ~/.arc-eval/logs/evaluation.log
```

## Getting Help

### 1. Built-in Help

```bash
# Command-specific help
arc-eval debug --help
arc-eval compliance --help
arc-eval improve --help

# Framework-specific guidance
arc-eval export-guide --framework langchain
arc-eval export-guide --framework crewai
```

### 2. Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Complete guides in `docs/`
- **Examples**: Sample configurations in `examples/`
- **Tests**: Reference implementations in `tests/`

### 3. Enterprise Support

For enterprise deployments:
- Custom domain scenarios
- Advanced CI/CD integration
- Performance optimization
- Priority support

## Next Steps

- [Testing Guide](testing/) - Comprehensive testing methodology
- [Performance Guide](performance/) - Advanced optimization techniques
- [API Reference](api/) - Programmatic usage patterns
- [Enterprise Integration](enterprise/) - Production deployment guides
