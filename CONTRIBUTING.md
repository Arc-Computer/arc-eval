# Contributing to AgentEval

Thank you for your interest in contributing to AgentEval! This guide will help you get started.

## Quick Start for Contributors

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd arc-eval

# Set up development environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"

# Verify installation
agent-eval --help
```

### Running Tests

```bash
# Run basic functionality test
agent-eval --domain finance --input examples/sample_agent_outputs.json

# Test with different frameworks
echo '{"output": "test"}' | agent-eval --domain finance
```

## Project Structure

```
agent-eval/
├── agent_eval/           # Main package
│   ├── cli.py           # CLI entry point
│   ├── core/            # Core evaluation logic
│   │   ├── engine.py    # Evaluation orchestrator
│   │   ├── types.py     # Data structures
│   │   ├── validators.py # Input validation
│   │   └── parser_registry.py # Framework detection
│   ├── domains/         # Evaluation scenarios
│   │   └── finance.yaml # Financial compliance scenarios
│   └── exporters/       # Report generators
├── examples/            # Sample inputs and outputs
├── CLAUDE.md           # Technical specification
├── DX.md              # Developer experience plan
└── README.md          # User documentation
```

## How to Contribute

### 1. Adding New Evaluation Scenarios

To add scenarios to existing domains:

```yaml
# In agent_eval/domains/{domain}.yaml
scenarios:
  - id: "new_scenario_id"
    name: "Descriptive Scenario Name"
    description: "What this scenario tests"
    severity: "critical|high|medium|low"
    compliance: ["REGULATION1", "REGULATION2"]
    test_type: "negative|positive"
    category: "scenario_category"
    input_template: "Template for synthetic input"
    expected_behavior: "expected_response"
    failure_indicators: ["keyword1", "keyword2"]
    remediation: "How to fix this issue"
    regulatory_reference: "Legal/regulatory citation"
```

### 2. Adding New Domain Packs

1. Create `agent_eval/domains/{domain}.yaml`
2. Follow the existing finance.yaml structure
3. Include 15 scenarios across 5 categories (3 scenarios each)
4. Test with sample data from your domain

### 3. Adding Framework Support

To support a new agent framework:

1. Add detection logic to `agent_eval/core/parser_registry.py`:
```python
# In FrameworkDetector.detect_framework()
if "your_framework_key" in data:
    return "your_framework"

# In OutputExtractor._extract_single()
"your_framework": OutputExtractor._extract_your_framework,
```

2. Implement extraction method:
```python
@staticmethod
def _extract_your_framework(data: Dict[str, Any]) -> str:
    """Extract output from YourFramework format."""
    return str(data.get("output_field", ""))
```

3. Add example to `examples/framework_examples.json`
4. Test with your framework's output format

### 4. Code Style Guidelines

- **Python Style**: Follow PEP 8
- **Type Hints**: Use type hints for all functions
- **Docstrings**: Document all classes and functions
- **Error Handling**: Provide helpful error messages
- **CLI Design**: Follow Unix CLI conventions

```python
# Good example
def evaluate_scenario(scenario: EvaluationScenario, output: str) -> EvaluationResult:
    """
    Evaluate a single scenario against agent output.
    
    Args:
        scenario: The scenario to evaluate
        output: Agent output text
        
    Returns:
        Evaluation result with pass/fail status
    """
```

### 5. Testing Guidelines

Before submitting:

```bash
# Test basic functionality
agent-eval --domain finance --input examples/sample_agent_outputs.json

# Test your framework
echo '{"your_format": "test"}' | agent-eval --domain finance --dev

# Test error handling
echo 'invalid json' | agent-eval --domain finance

# Test help documentation
agent-eval --help-input
```

## Pull Request Process

1. **Fork** the repository
2. **Create branch** from main: `git checkout -b feature/your-feature`
3. **Make changes** following our guidelines
4. **Test thoroughly** with multiple input formats
5. **Commit** with clear messages: `git commit -m "Add: new security domain scenarios"`
6. **Push** to your fork: `git push origin feature/your-feature`
7. **Create Pull Request** with description of changes

### PR Requirements

- [ ] All existing tests pass
- [ ] New functionality includes examples
- [ ] Documentation updated if needed
- [ ] Code follows style guidelines
- [ ] Commit messages are clear

## Priority Areas for Contribution

### High Priority
- **Security domain scenarios** (15 scenarios needed)
- **ML/Infrastructure domain scenarios** (15 scenarios needed)
- **Framework support** for emerging agent platforms

### Medium Priority
- **Custom export formats** (HTML, XML)
- **Advanced validation** (schema validation)
- **Performance optimization** for large inputs

### Documentation
- **Framework integration guides** for specific platforms
- **Domain-specific examples** for different industries
- **Troubleshooting guides** for common issues

## Getting Help

- **Documentation**: Check README.md and CLAUDE.md
- **Examples**: See examples/ directory
- **Issues**: Create GitHub issue for bugs/questions
- **Framework Questions**: Use `agent-eval --help-input`

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and contribute
- Maintain professional communication

## Release Process

1. **Semantic Versioning**: We follow semver (0.1.0, 0.2.5, etc.)
2. **Testing**: All changes tested with pilot partners
3. **Documentation**: Updated for each release
4. **Backwards Compatibility**: Maintained within major versions

Thank you for contributing to AgentEval! 🚀