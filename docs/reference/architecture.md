# Architecture

ARC-Eval is built with a modular, extensible architecture designed for reliability, performance, and developer experience. This document provides a comprehensive overview of the system design and component interactions.

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                           ARC-Eval Platform                        │
├─────────────────┬───────────────────┬───────────────────────────────┤
│   CLI Layer     │   Core Engine     │      Prediction System        │
│                 │                   │                               │
│ • Commands      │ • Evaluation      │ • Hybrid Predictor           │
│ • Interactive   │ • Framework       │ • Compliance Rules           │
│ • Streaming     │ • Parsing         │ • LLM Analysis               │
│ • Menus         │ • Types           │ • Risk Scoring               │
└─────────────────┼───────────────────┼───────────────────────────────┤
│   UI Layer      │   Evaluation      │      Domain Knowledge         │
│                 │                   │                               │
│ • Dashboards    │ • Agent-as-Judge  │ • Finance (110 scenarios)    │
│ • Progress      │ • Judges          │ • Security (120 scenarios)   │
│ • Rendering     │ • Verification    │ • ML/AI (148 scenarios)      │
│ • Export        │ • Calibration     │ • Regulatory Frameworks      │
└─────────────────┴───────────────────┴───────────────────────────────┘
```

## Core Components

### 1. CLI Layer (`agent_eval.cli`)

The command-line interface provides the primary user interaction point.

#### Main CLI Module
```python
# agent_eval/cli.py
@click.group(invoke_without_command=True)
def cli(ctx):
    """Main CLI entry point with command routing."""
```

**Key Features:**
- Command routing and argument parsing
- Interactive and non-interactive modes
- Rich console output with progress indicators
- Error handling and user guidance

#### Command Structure
```
agent_eval/commands/
├── __init__.py              # Command registry
├── base.py                  # Base command handler
├── debug_command.py         # Debug workflow
├── compliance_command.py    # Compliance workflow
├── improve_command.py       # Improve workflow
├── analyze_command.py       # Combined workflow
└── reliability_handler.py   # Core reliability logic
```

### 2. Core Engine (`agent_eval.core`)

The evaluation engine orchestrates all evaluation activities.

#### Evaluation Engine
```python
# agent_eval/core/engine.py
class EvaluationEngine:
    """Main engine for running domain-specific evaluations."""
    
    def __init__(self, domain: str, config: Optional[Path] = None):
        self.domain = domain
        self.eval_pack = self._load_evaluation_pack()
        
    def evaluate(self, agent_outputs: List[AgentOutput]) -> List[EvaluationResult]:
        """Run evaluation against loaded scenarios."""
```

**Responsibilities:**
- Domain-specific evaluation pack loading
- Agent output processing and normalization
- Evaluation orchestration and result aggregation
- Performance optimization with compiled patterns

#### Type System
```python
# agent_eval/core/types.py
@dataclass
class AgentOutput:
    """Normalized agent output for evaluation."""
    raw_output: str
    normalized_output: str
    framework: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass  
class EvaluationResult:
    """Result of evaluating an agent output against a scenario."""
    scenario_id: str
    passed: bool
    score: float
    feedback: str
    evidence: List[str]
```

#### Framework Detection
```python
# agent_eval/core/parser_registry.py
class FrameworkDetector:
    """Automatic detection and parsing of agent framework outputs."""
    
    def detect_and_extract(self, raw_data: Any) -> Tuple[str, str]:
        """Detect framework and extract normalized output."""
```

**Supported Frameworks:**
- LangChain (intermediate_steps detection)
- CrewAI (crew_output detection)
- OpenAI (choices/message structure)
- Anthropic (Claude API format)
- Generic (fallback for custom frameworks)

### 3. Prediction System (`agent_eval.prediction`)

The hybrid reliability prediction system combining rules and LLM analysis.

#### Hybrid Predictor
```python
# agent_eval/prediction/hybrid_predictor.py
class HybridReliabilityPredictor:
    """Combines rule-based + LLM scoring with weighted approach."""
    
    def __init__(self, api_manager=None):
        self.compliance_engine = ComplianceRuleEngine()
        self.llm_predictor = LLMReliabilityPredictor(api_manager)
        self.rule_weight = 0.4  # 40% for deterministic compliance
        self.llm_weight = 0.6   # 60% for LLM pattern recognition
```

#### Compliance Rules Engine
```python
# agent_eval/prediction/compliance_rules.py
class ComplianceRuleEngine:
    """Deterministic compliance rule engine for regulatory requirements."""
    
    def check_pii_compliance(self, config: Dict) -> Dict:
        """GDPR Article 25 privacy by design requirements."""
        
    def check_security_compliance(self, config: Dict) -> Dict:
        """OWASP and security best practices."""
        
    def check_audit_compliance(self, config: Dict) -> Dict:
        """SOX and audit trail requirements."""
```

#### LLM Predictor
```python
# agent_eval/prediction/llm_predictor.py
class LLMReliabilityPredictor:
    """LLM-powered pattern recognition for complex reliability assessment."""
    
    def predict_failure_probability(self, analysis) -> Dict:
        """Use GPT-4.1 to analyze patterns and predict failure probability."""
```

### 4. Evaluation System (`agent_eval.evaluation`)

Agent-as-a-Judge framework with domain-specific judges.

#### Agent Judge Framework
```python
# agent_eval/evaluation/judges/__init__.py
class AgentJudge:
    """Main Agent-as-a-Judge evaluation framework."""
    
    def __init__(self, domain: str = "finance"):
        self.api_manager = APIManager()
        self.domain_judge = self._get_domain_judge(domain)
        
    def evaluate_batch(self, scenarios: List[EvaluationScenario], 
                      agent_outputs: List[AgentOutput]) -> List[JudgmentResult]:
        """Evaluate multiple scenarios using batch processing."""
```

#### Domain-Specific Judges
```python
# agent_eval/evaluation/judges/domain.py
class FinanceJudge(BaseDomainJudge):
    """Finance domain judge for SOX, KYC, AML compliance."""
    
class SecurityJudge(BaseDomainJudge):
    """Security domain judge for OWASP, prompt injection detection."""
    
class MLJudge(BaseDomainJudge):
    """ML domain judge for bias detection, fairness monitoring."""
```

#### Dual-Track Evaluator
```python
# agent_eval/evaluation/judges/dual_track_evaluator.py
class DualTrackEvaluator:
    """Implements Fast Track (≤50 scenarios) and Batch Track (100+ scenarios)."""
    
    def evaluate(self, scenarios: List[EvaluationScenario], 
                agent_outputs: List[AgentOutput]) -> AsyncGenerator[EvaluationResult]:
        """Choose evaluation mode based on scenario count."""
```

### 5. UI System (`agent_eval.ui`)

Rich terminal user interface components.

#### Dashboard Components
```python
# agent_eval/ui/debug_dashboard.py
class DebugDashboard:
    """Specialized dashboard for debug workflow insights."""
    
    def display_reliability_prediction(self, prediction: Dict[str, Any]) -> None:
        """Display reliability prediction prominently."""

# agent_eval/ui/prediction_renderer.py  
class PredictionRenderer:
    """Specialized renderer for reliability predictions."""
    
    def render_prediction_summary(self, prediction: Dict[str, Any]) -> None:
        """Render high-impact prediction summary."""
```

#### Interactive Components
```python
# agent_eval/ui/interactive_menu.py
class InteractiveMenu:
    """Interactive menu system for guided workflows."""
    
    def show_next_steps_menu(self, workflow_state: Dict) -> str:
        """Show context-aware next steps based on workflow state."""
```

### 6. Domain Knowledge (`agent_eval.domains`)

Compliance scenarios and regulatory frameworks.

#### Domain Structure
```
agent_eval/domains/
├── finance.yaml         # 110 finance scenarios (SOX, KYC, AML)
├── security.yaml        # 120 security scenarios (OWASP, NIST)
├── ml.yaml             # 148 ML scenarios (EU AI Act, IEEE)
└── scenario_loader.py   # Dynamic scenario loading
```

#### Scenario Format
```yaml
# Example scenario structure
scenarios:
  - id: "fin_001"
    name: "SOX Financial Reporting Compliance"
    description: "Validate financial data accuracy and audit trails"
    severity: "critical"
    category: "financial_reporting"
    compliance: ["SOX", "GAAP"]
    test_type: "validation"
    expected_behavior: "Accurate financial calculations with audit trail"
    failure_indicators:
      - "mathematical_errors"
      - "missing_audit_trail"
    remediation: "Implement calculation validation and comprehensive logging"
```

## Data Flow Architecture

### 1. Input Processing Pipeline

```
Raw Agent Outputs → Framework Detection → Normalization → Validation → Evaluation
```

#### Framework Detection
```python
def detect_and_extract(raw_data: Any) -> Tuple[str, str]:
    """Multi-stage framework detection."""
    
    # LangChain detection
    if isinstance(raw_data, dict) and "intermediate_steps" in raw_data:
        return "langchain", extract_langchain_output(raw_data)
    
    # CrewAI detection
    if isinstance(raw_data, dict) and ("crew_output" in raw_data or "tasks_output" in raw_data):
        return "crewai", extract_crewai_output(raw_data)
    
    # OpenAI detection
    if isinstance(raw_data, dict) and "choices" in raw_data:
        return "openai", extract_openai_output(raw_data)
    
    # Generic fallback
    return "generic", extract_generic_output(raw_data)
```

#### Normalization Process
```python
@classmethod
def from_raw(cls, raw_data: Any) -> 'AgentOutput':
    """Create AgentOutput from raw framework data."""
    
    framework, normalized_output = detect_and_extract(raw_data)
    
    return cls(
        raw_output=str(raw_data),
        normalized_output=normalized_output.strip(),
        framework=framework,
        metadata=raw_data if isinstance(raw_data, dict) else None
    )
```

### 2. Evaluation Pipeline

```
Normalized Outputs → Scenario Loading → Judge Evaluation → Result Aggregation → Reporting
```

#### Scenario Loading
```python
def _load_evaluation_pack(self) -> EvaluationPack:
    """Load domain-specific scenarios with caching."""
    
    scenarios_file = DOMAINS_DIR / f"{self.domain}.yaml"
    with open(scenarios_file, 'r') as f:
        data = yaml.safe_load(f)
    
    return EvaluationPack.from_dict(data)
```

#### Judge Evaluation
```python
async def evaluate_scenario_async(self, scenario: EvaluationScenario, 
                                 agent_output: AgentOutput) -> JudgmentResult:
    """Async evaluation with rate limiting and error handling."""
    
    prompt = self._create_evaluation_prompt(scenario, agent_output)
    response = await self.api_manager.call_async(prompt)
    return self._parse_judgment(response, scenario)
```

### 3. Prediction Pipeline

```
Analysis Data → Rules Engine → LLM Analysis → Score Combination → Business Impact
```

#### Rules Engine Processing
```python
def check_all_compliance(self, config: Dict) -> Dict:
    """Run all compliance checks and aggregate results."""
    
    results = {
        'pii': self.check_pii_compliance(config),
        'security': self.check_security_compliance(config),
        'audit': self.check_audit_compliance(config)
    }
    
    return self._aggregate_rule_results(results)
```

#### LLM Analysis Processing
```python
def predict_failure_probability(self, analysis) -> Dict:
    """LLM-powered pattern recognition."""
    
    analysis_data = self._extract_analysis_features(analysis)
    prompt = self._create_prediction_prompt(analysis_data)
    
    response, _ = self.api_manager.call_with_logprobs(prompt)
    return self._parse_prediction_response(response)
```

## Performance Architecture

### 1. Caching Strategy

```python
# Compiled regex patterns for performance
class EvaluationEngine:
    def __init__(self, domain: str):
        self._compiled_pii_patterns = self._compile_pii_patterns()
        self._compiled_bias_patterns = self._compile_bias_patterns()
        self._compiled_weak_control_patterns = self._compile_weak_control_patterns()
```

### 2. Batch Processing

```python
# Automatic batch mode selection
class DualTrackEvaluator:
    def _select_evaluation_mode(self, scenario_count: int) -> EvaluationMode:
        """Select evaluation mode based on scenario count."""
        
        if scenario_count <= 50:
            return EvaluationMode.FAST_TRACK
        else:
            return EvaluationMode.BATCH_TRACK
```

### 3. Async Processing

```python
# Concurrent evaluation processing
async def evaluate_batch_async(self, scenarios: List[EvaluationScenario],
                              agent_outputs: List[AgentOutput]) -> List[JudgmentResult]:
    """Process evaluations concurrently with rate limiting."""
    
    semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
    
    tasks = [
        self._evaluate_with_semaphore(semaphore, scenario, output)
        for scenario, output in zip(scenarios, agent_outputs)
    ]
    
    return await asyncio.gather(*tasks)
```

## Extension Points

### 1. Custom Frameworks

```python
# Add custom framework support
def register_custom_framework(name: str, detector: Callable, extractor: Callable):
    """Register custom framework detection and extraction."""
    
    FRAMEWORK_DETECTORS[name] = detector
    FRAMEWORK_EXTRACTORS[name] = extractor
```

### 2. Custom Domains

```python
# Add custom domain scenarios
def register_custom_domain(name: str, scenarios_file: Path):
    """Register custom domain with scenarios."""
    
    DOMAIN_CONFIGS[name] = {
        'scenarios_file': scenarios_file,
        'judge_class': CustomDomainJudge
    }
```

### 3. Custom Judges

```python
# Implement custom domain judge
class CustomDomainJudge(BaseDomainJudge):
    """Custom domain-specific judge implementation."""
    
    def create_evaluation_prompt(self, scenario: EvaluationScenario, 
                               agent_output: AgentOutput) -> str:
        """Create domain-specific evaluation prompt."""
        return f"Evaluate {agent_output.normalized_output} against {scenario.description}"
```

## Security Architecture

### 1. API Key Management

```python
# Secure API key handling
class APIManager:
    def __init__(self):
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        self.openai_key = os.getenv('OPENAI_API_KEY')
        
        if not any([self.anthropic_key, self.openai_key]):
            logger.warning("No API keys found - Agent-as-Judge evaluation disabled")
```

### 2. Input Validation

```python
# Comprehensive input validation
class InputValidator:
    def validate_agent_outputs(self, outputs: List[Dict]) -> List[str]:
        """Validate agent outputs for security and format compliance."""
        
        errors = []
        for i, output in enumerate(outputs):
            if not self._is_safe_content(output):
                errors.append(f"Unsafe content detected in output {i}")
                
        return errors
```

### 3. Output Sanitization

```python
# Sanitize outputs for security
def sanitize_output(self, content: str) -> str:
    """Sanitize content for safe display and processing."""
    
    # Remove potential injection patterns
    sanitized = re.sub(r'<script.*?</script>', '', content, flags=re.IGNORECASE)
    
    # Escape special characters
    sanitized = html.escape(sanitized)
    
    return sanitized
```

## Deployment Architecture

### 1. Package Structure

```
arc-eval/
├── agent_eval/              # Main package
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── core/               # Core evaluation engine
│   ├── prediction/         # Prediction system
│   ├── evaluation/         # Agent-as-Judge framework
│   ├── ui/                 # User interface components
│   ├── commands/           # CLI commands
│   └── domains/            # Domain scenarios
├── examples/               # Usage examples
├── tests/                  # Test suite
├── docs/                   # Documentation
└── setup.py               # Package configuration
```

### 2. Distribution

```python
# setup.py configuration
setup(
    name="arc-eval",
    version="0.2.9",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "arc-eval=agent_eval.cli:main",
        ],
    },
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0", 
        "anthropic>=0.18.0",
        "openai>=1.0.0",
        # ... other dependencies
    ]
)
```

### 3. Configuration Management

```yaml
# ~/.arc-eval/config.yaml
default_domain: finance
interactive_mode: true

api:
  anthropic:
    model: claude-3-5-haiku-20241022
  openai:
    model: gpt-4o-mini

prediction:
  rule_weight: 0.4
  llm_weight: 0.6
  confidence_threshold: 0.6
```

## Next Steps

- [API Reference](../api/) - Complete SDK documentation
- [Framework Integration](../frameworks/) - Framework-specific guides
- [Configuration](configuration.md) - Advanced configuration options
- [Troubleshooting](troubleshooting.md) - Common issues and solutions
