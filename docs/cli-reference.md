# CLI Reference

Complete reference for all ARC-Eval command-line interface commands and options.

## Global Options

Available for all commands:

```bash
arc-eval --version          # Show version information
arc-eval --help            # Show general help
arc-eval <command> --help  # Show command-specific help
```

## Core Commands

### `analyze` - Complete Workflow (Recommended Entry Point)

**The unified analysis workflow that chains debug → compliance → improve.**

This is the **recommended entry point** for comprehensive agent evaluation, providing a complete end-to-end analysis in a single command.

```bash
arc-eval analyze --input <file> --domain <domain> [options]
```

**Required Arguments:**
- `--input <file>`: Agent output file (JSON format)
- `--domain <domain>`: Evaluation domain (`finance`, `security`, `ml`)

**Optional Arguments:**
- `--quick`: Quick analysis without agent-judge (faster, offline)
- `--no-interactive`: Skip interactive menu for automation
- `--verbose`: Enable verbose output

**What It Does:**
1. **🔍 Debug Analysis**: Identifies reliability issues and failure patterns
2. **✅ Compliance Check**: Tests against 378 enterprise scenarios
3. **📈 Improvement Plan**: Generates actionable fixes and recommendations
4. **🎯 Unified Menu**: Provides guided next steps and workflow options

**Examples:**
```bash
# Complete analysis workflow (recommended)
arc-eval analyze --input outputs.json --domain finance

# Quick analysis for CI/CD pipelines
arc-eval analyze --input outputs.json --domain security --quick --no-interactive

# Verbose analysis for troubleshooting
arc-eval analyze --input outputs.json --domain ml --verbose
```

**When to Use:**
- **First-time evaluation**: Best starting point for new users
- **Complete assessment**: When you need comprehensive analysis
- **Workflow automation**: Single command for CI/CD integration
- **Regular monitoring**: Periodic agent health checks

### `debug` - Find What's Broken

Analyze agent outputs to identify reliability issues and predict failure patterns.

```bash
arc-eval debug --input <file> [options]
```

**Required Arguments:**
- `--input <file>`: Path to agent output file (JSON format)

**Optional Arguments:**
- `--framework <name>`: Specify framework (auto-detected if not provided)
  - Choices: `langchain`, `langgraph`, `crewai`, `autogen`, `openai`, `anthropic`, `nvidia_aiq`, `generic`
- `--output-format <format>`: Output format (default: `console`)
  - Choices: `console`, `json`, `html`
- `--no-interactive`: Skip interactive menus (for CI/CD)
- `--verbose`: Show detailed technical output
- `--pattern-analysis`: Perform universal failure pattern analysis
- `--root-cause`: Deep root cause analysis with remediation
- `--framework-agnostic`: Show insights from other frameworks
- `--cross-framework-learning`: Show how other frameworks solve similar issues

**Examples:**
```bash
# Basic debug analysis
arc-eval debug --input agent_outputs.json

# Debug with specific framework
arc-eval debug --input outputs.json --framework langchain

# Debug for CI/CD (no interaction)
arc-eval debug --input outputs.json --no-interactive --output-format json

# Verbose debug analysis
arc-eval debug --input outputs.json --verbose

# Advanced pattern analysis
arc-eval debug --input outputs.json --pattern-analysis --root-cause

# Cross-framework learning
arc-eval debug --input outputs.json --framework-agnostic --cross-framework-learning
```

### `compliance` - Validate Requirements

Test agent outputs against domain-specific compliance scenarios.

```bash
arc-eval compliance --domain <domain> [options]
```

**Required Arguments:**
- `--domain <domain>`: Evaluation domain
  - Choices: `finance`, `security`, `ml`

**Optional Arguments:**
- `--input <file>`: Agent output file (required unless using `--quick-start`)
- `--folder-scan`: Auto-find JSON files in current directory
- `--export <format>`: Export report format
  - Choices: `pdf`, `csv`, `json`
- `--no-export`: Skip PDF generation
- `--no-interactive`: Skip interactive menus
- `--quick-start`: Use built-in sample data for instant demo
- `--high`: High accuracy mode (slower, premium models)
- `--provider <name>`: AI provider
  - Choices: `openai`, `anthropic`, `google`
- `--verbose`: Show detailed technical output

**Examples:**
```bash
# Quick demo with sample data
arc-eval compliance --domain finance --quick-start

# Full compliance check
arc-eval compliance --domain finance --input agent_outputs.json

# Export PDF report
arc-eval compliance --domain security --input outputs.json --export pdf

# High accuracy mode with premium models
arc-eval compliance --domain ml --input outputs.json --high

# Use specific AI provider
arc-eval compliance --domain finance --input outputs.json --provider anthropic
```

### `improve` - Get Better

Generate improvement recommendations based on evaluation results.

```bash
arc-eval improve [options]
```

**Optional Arguments:**
- `--from-evaluation <file>`: Evaluation file to generate improvement plan from
- `--baseline <file>`: Baseline evaluation for comparison
- `--current <file>`: Current evaluation for comparison
- `--auto-detect`: Auto-detect latest evaluation file
- `--no-interactive`: Skip interactive menus
- `--verbose`: Enable verbose output
- `--framework-specific`: Generate framework-specific improvements
- `--code-examples`: Include copy-paste ready code examples
- `--cross-framework-solutions`: Show solutions from other frameworks

**Examples:**
```bash
# Auto-detect latest evaluation
arc-eval improve --auto-detect

# Improve from specific results file
arc-eval improve --from-evaluation results.json

# Compare baseline vs current
arc-eval improve --baseline v1.json --current v2.json

# Verbose improvement analysis
arc-eval improve --from-evaluation results.json --verbose

# Framework-specific improvements with code examples
arc-eval improve --from-evaluation results.json --framework-specific --code-examples

# Cross-framework solutions
arc-eval improve --from-evaluation results.json --cross-framework-solutions
```



## Utility Commands

### `export-guide` - Learn Output Formats

Get help creating agent outputs in the correct format.

```bash
arc-eval export-guide [options]
```

**Optional Arguments:**
- `--framework <name>`: Show examples for specific framework
  - Choices: `openai`, `openai_agents`, `anthropic`, `langchain`, `crewai`, `google_adk`, `agno`, `nvidia_aiq`, `generic`

**Examples:**
```bash
# General export guide
arc-eval export-guide

# Framework-specific examples
arc-eval export-guide --framework langchain
arc-eval export-guide --framework crewai
arc-eval export-guide --framework openai
```



## Configuration Options

### Environment Variables

Set these environment variables for enhanced functionality:

```bash
# API keys for Agent-as-Judge evaluation
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Configuration options
export ARC_EVAL_CONFIG_PATH="/path/to/config.yaml"
export ARC_EVAL_CACHE_DIR="/path/to/cache"
export ARC_EVAL_LOG_LEVEL="INFO"
```

### Configuration File

Create `~/.arc-eval/config.yaml` for persistent settings:

```yaml
# Default settings
default_domain: finance
default_output_format: console
interactive_mode: true

# API configuration
api:
  anthropic:
    model: claude-3-5-haiku-20241022
    max_tokens: 4000
  openai:
    model: gpt-4o-mini
    max_tokens: 4000

# Export settings
export:
  pdf_template: default
  include_raw_data: false
  
# Performance settings
performance:
  batch_threshold: 5
  cache_enabled: true
  parallel_evaluation: true
```

## Input File Formats

### Supported JSON Structures

ARC-Eval automatically detects and parses various input formats:

#### Generic Format
```json
[
  {
    "output": "Agent response text",
    "scenario_id": "optional_scenario_id",
    "metadata": {"key": "value"}
  }
]
```

#### LangChain Format
```json
[
  {
    "input": "User input",
    "output": "Agent output", 
    "intermediate_steps": [
      [{"tool": "tool_name", "tool_input": "input"}, "result"]
    ]
  }
]
```

#### OpenAI Format
```json
[
  {
    "choices": [
      {
        "message": {
          "role": "assistant",
          "content": "Response content"
        }
      }
    ],
    "usage": {"prompt_tokens": 50, "completion_tokens": 10}
  }
]
```

### Input Validation

ARC-Eval validates input files and provides helpful error messages:

```bash
# Check file format
arc-eval debug --input invalid.json
# Error: Invalid JSON format at line 5
# Suggestion: Use 'python -m json.tool invalid.json' to validate

# Check required fields
arc-eval compliance --domain finance --input missing_output.json  
# Error: Missing 'output' field in entry 3
# Suggestion: Ensure all entries have an 'output' field
```

## Output Formats

### Console Output (Default)

Rich, interactive console output with:
- Color-coded risk levels
- Progress indicators
- Interactive menus
- Formatted tables and charts

### JSON Output

Machine-readable JSON for programmatic processing:

```bash
arc-eval debug --input outputs.json --output-format json > results.json
```

### HTML Output

Web-friendly HTML reports:

```bash
arc-eval compliance --domain finance --input outputs.json --output-format html
```

### Export Formats

Professional reports for stakeholders:

```bash
# PDF report
arc-eval compliance --domain finance --input outputs.json --export pdf

# CSV data export
arc-eval debug --input outputs.json --export csv

# JSON export with metadata
arc-eval analyze --input outputs.json --domain security --export json
```

## Exit Codes

ARC-Eval uses standard exit codes for CI/CD integration:

- `0`: Success - no critical issues found
- `1`: Error - command failed or critical issues found
- `2`: Invalid arguments or configuration
- `3`: File not found or permission error

## Performance Tips

### Optimize Evaluation Speed

1. **Use scenario targeting:**
   ```json
   {"output": "response", "scenario_id": "fin_001"}
   ```

2. **Enable batch processing:**
   ```bash
   # Automatically enabled for 5+ scenarios
   arc-eval compliance --domain finance --input large_dataset.json
   ```

3. **Skip interactive mode for automation:**
   ```bash
   arc-eval debug --input outputs.json --no-interactive
   ```

### Memory and Resource Usage

- **Large files**: ARC-Eval streams large JSON files to minimize memory usage
- **Parallel processing**: Evaluation runs in parallel when possible
- **Caching**: Results are cached to speed up repeated evaluations

## Troubleshooting

### Common Issues

1. **File not found:**
   ```bash
   ls -la *.json  # Check file exists
   ```

2. **Invalid JSON:**
   ```bash
   python -m json.tool your_file.json  # Validate JSON
   ```

3. **Missing API key:**
   ```bash
   export ANTHROPIC_API_KEY="your-key"  # Set API key
   ```

4. **Permission errors:**
   ```bash
   chmod +r your_file.json  # Fix file permissions
   ```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
export ARC_EVAL_LOG_LEVEL=DEBUG
arc-eval debug --input outputs.json --verbose
```

## Next Steps

- [Workflows Guide](workflows/) - Deep dive into each workflow
- [Framework Integration](frameworks/) - Framework-specific usage
- [API Reference](api/) - Python SDK documentation
- [Examples](../examples/) - Complete usage examples
