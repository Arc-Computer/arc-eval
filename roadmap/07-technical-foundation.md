# 07. Arc-Eval Technical Foundation

## Architecture Overview

Arc-Eval is built with plugins for different industries and uses AI to test agents. It's designed to be fast, reliable, and easy to extend.

### System Architecture

```bash
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Agent Output  │────▶│ Framework Parser │────▶│  Type System    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                           │
                        ┌──────────────────┐               ▼
                        │   Judge Engine   │◀────┌─────────────────┐
                        └──────────────────┘     │ Evaluation Core │
                                │                └─────────────────┘
                                ▼                          │
                        ┌──────────────────┐               ▼
                        │     Results      │     ┌─────────────────┐
                        └──────────────────┘────▶│    Exporters    │
                                                 └─────────────────┘
```

### Core Components

| Component | Purpose | Key Files |
|-----------|---------|-----------|
| **Type System** | Type-safe data models | [`core/types.py`](../../agent_eval/core/types.py) |
| **Framework Detection** | Auto-detect 10+ agent frameworks | [`core/parser_registry.py`](../../agent_eval/core/parser_registry.py) |
| **Evaluation Engine** | Hybrid rule + AI evaluation | [`core/engine.py`](../../agent_eval/core/engine.py) |
| **Judge System** | Agent-as-a-Judge implementation | [`evaluation/judges/`](../../agent_eval/evaluation/judges/) |
| **CLI Interface** | Rich-based command interface | [`cli.py`](../../agent_eval/cli.py) |

## Key Technical Decisions

### 1. Type-Safe Architecture

**Decision**: Use Python dataclasses for data structures

**Rationale**: 
- Type safety with runtime validation
- Self-documenting code structure
- Easy serialization/deserialization
- IDE autocomplete support

**Implementation**: See [`core/types.py`](../../agent_eval/core/types.py) for 20+ core types including:
- `AgentOutput`, `EvaluationScenario`, `EvaluationResult`
- Domain-specific types with compliance mappings
- Enhanced fields for Agent-as-a-Judge integration

### 2. Multi-Framework Support

**Decision**: Plugin-based framework detection with parser registry

**Rationale**:
- Support any agent framework without code changes
- Automatic detection reduces user friction
- Extensible for future frameworks

**Implementation**: [`core/parser_registry.py`](../../agent_eval/core/parser_registry.py)
- 10+ frameworks supported (LangChain, CrewAI, OpenAI, etc.)
- Pattern-based detection with fallback mechanisms
- Preserves framework-specific metadata

### 3. Hybrid Evaluation Architecture

**Decision**: Use rules first, then AI for complex cases

**Rationale**:
- Rules provide fast, deterministic baseline (< 5ms)
- AI judges add nuanced understanding when needed
- Cost-effective with selective AI usage

**Implementation**: 
- Rule engine: [`core/engine.py`](../../agent_eval/core/engine.py)
- Judge system: [`evaluation/judges/base.py`](../../agent_eval/evaluation/judges/base.py)
- Confidence thresholds trigger AI enhancement

### 4. Agent-as-a-Judge Framework

**Decision**: Dual-model architecture (Cerebras + Gemini)

**Rationale**:
- Cerebras: 2600+ tokens/sec for initial evaluation
- Gemini: Quality assurance on low-confidence results
- 92% accuracy vs 70% for traditional methods

**Implementation**: [`evaluation/judges/`](../../agent_eval/evaluation/judges/)
- Domain-specific judges (Finance, Security, ML)
- Workflow judges (Debug, Improve, Compliance)
- Thread-safe API management with cost tracking

### 5. Performance Optimization

**Decision**: Pre-compiled patterns and batch processing

**Rationale**:
- Regex compilation at startup reduces runtime overhead
- Batch API calls minimize latency
- Token counting prevents cost overruns

**Implementation**:
- Pre-compiled patterns in [`core/engine.py`](../../agent_eval/core/engine.py)
- Batch processing in [`evaluation/judges/api_manager.py`](../../agent_eval/evaluation/judges/api_manager.py)
- Cost tracking throughout judge system

### 6. Configuration System

**Decision**: Settings files that can override each other

**Rationale**:
- User preferences without code changes
- Project-specific overrides
- Environment variable support

**Implementation**: [`core/config.py`](../../agent_eval/core/config.py)
- User: `~/.arc-eval/config.yaml`
- Project: `.arc-eval-config.yaml`
- Environment: `.env` file support

## Data Flow

### 1. Input Processing
```python
# Framework detection and normalization
raw_output → parser_registry.detect() → AgentOutput
```

### 2. Evaluation Pipeline
```python
# Hybrid evaluation with confidence-based enhancement
scenario + output → evaluate() → confidence_check → judge_enhance → result
```

### 3. Export Pipeline
```python
# Multi-format export with compliance features
results → summarize() → format() → export(pdf|csv|json)
```

## Technology Stack

### Core Technologies
- **Python 3.8+**: Type hints, dataclasses, async support
- **Click**: Powerful CLI framework
- **Rich**: Enhanced terminal UI
- **YAML**: Human-readable configuration

### AI/LLM Providers
- **Primary**: Anthropic (Claude) via [`evaluation/judges/api_manager.py`](../../agent_eval/evaluation/judges/api_manager.py)
- **Speed**: Cerebras (2600+ tokens/sec)
- **QA**: Google Gemini
- **Fallback**: OpenAI support

### Export & Reporting
- **PDF**: ReportLab for audit-ready reports
- **Data**: CSV/JSON for integration
- **UI**: Rich for interactive dashboards

## Extension Points

### 1. Custom Domains
Add new evaluation domains in [`domains/`](../../agent_eval/domains/):
```yaml
# domains/custom.yaml
name: custom
version: 1.0
scenarios:
  - category: specific_check
    items:
      - id: CUSTOM-001
        description: "Custom evaluation"
```

### 2. Framework Support
Register new frameworks in [`core/parser_registry.py`](../../agent_eval/core/parser_registry.py):
```python
@FrameworkParserRegistry.register("custom_framework")
class CustomParser(FrameworkParser):
    def detect(self, data: Dict) -> bool:
        # Detection logic
    def extract_output(self, data: Dict) -> str:
        # Extraction logic
```

### 3. Custom Judges
Extend [`evaluation/judges/base.py`](../../agent_eval/evaluation/judges/base.py):
```python
class CustomJudge(BaseJudge):
    def build_prompt(self, scenario, output):
        # Custom evaluation logic
```

## Performance Characteristics

### Current Benchmarks
- **Rule evaluation**: < 5ms per scenario
- **AI evaluation**: 100-500ms per scenario
- **Batch processing**: 50+ evaluations/sec
- **Token throughput**: 2600+ tokens/sec (Cerebras)

### Resource Usage
- **Memory**: ~200MB base + 50MB per 1000 evaluations
- **CPU**: Single-threaded rule eval, multi-threaded AI calls
- **Network**: Async API calls with connection pooling

## Security & Privacy

### Local-First Design
- All evaluation happens locally by default
- No data leaves environment without explicit config
- Audit trails stored locally

### Compliance Features
- PII detection via regex patterns
- Regulatory mapping in scenarios
- Audit-ready PDF exports
- Configurable data retention

## Development Workflow

### Local Setup
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy agent_eval/
```

### Testing Strategy
- Unit tests for core components
- Integration tests for judges
- Mock API responses for CI/CD
- Performance benchmarks

## Future Architecture (Phases 1-3)

### Phase 1: Runtime Tracing
- Add [`trace/`](../../agent_eval/trace/) module
- Implement ArcTracer decorator
- Real-time streaming via WebSockets

### Phase 2: Web Interface
- FastAPI backend in [`web/`](../../agent_eval/web/)
- React frontend for dashboards
- PostgreSQL for trace storage

### Phase 3: Custom Scenarios
- LLM-powered scenario generation
- Industry-specific templates
- Community scenario marketplace

## Summary

Arc-Eval's technical foundation provides:
1. **Extensible architecture** for new frameworks and domains
2. **Performance optimization** for real-time evaluation
3. **Enterprise features** for compliance and audit
4. **Clear extension points** for future development

The codebase is structured for the BYOA vision while maintaining backward compatibility and performance at scale.