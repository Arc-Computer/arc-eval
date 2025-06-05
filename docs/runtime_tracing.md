# ARC-Eval Runtime Tracing

One-line agent monitoring and reliability tracking for any framework.

## Quick Start

```python
from agent_eval.trace import ArcTracer

# One line to add monitoring
tracer = ArcTracer("finance")
agent = tracer.trace_agent(your_agent)

# Your agent is now monitored!
response = agent.run("Process this transaction")
```

## Features

- **🎯 Reliability Scoring**: A+ to F grades based on success rate and performance
- **💰 Cost Tracking**: Real-time API cost monitoring and optimization suggestions
- **🔧 Framework Agnostic**: Works with LangChain, CrewAI, AutoGen, OpenAI, and more
- **📊 Real-time Dashboard**: Live monitoring with interactive visualizations
- **🚀 Zero Configuration**: Works out of the box with any agent
- **📈 Performance Analytics**: Execution timeline, tool calls, and bottleneck detection

## Installation

```bash
# Basic installation
pip install arc-eval

# With API server support
pip install arc-eval[server]
# or
pip install fastapi uvicorn
```

## Usage

### 1. Basic Monitoring

```python
from agent_eval.trace import ArcTracer

# Initialize tracer with domain context
# API key can be provided or read from ARC_API_KEY env var
tracer = ArcTracer(domain="finance", agent_id="my_financial_agent")

# Wrap your agent (works with any framework)
traced_agent = tracer.trace_agent(your_agent)

# Use your agent normally - it's now monitored
result = traced_agent.run("Analyze this transaction")

# Get reliability score
score = tracer.get_reliability_score()
print(f"Reliability: {score.grade} ({score.score}%)")
```

### 2. Framework-Specific Examples

#### LangChain
```python
from langchain.agents import AgentExecutor
from agent_eval.trace import ArcTracer

# Your existing LangChain agent
agent = AgentExecutor.from_agent_and_tools(...)

# Add monitoring
tracer = ArcTracer("finance")
traced_agent = tracer.trace_agent(agent)

# Use normally
result = traced_agent.invoke({"input": "Process payment"})
```

#### CrewAI
```python
from crewai import Agent, Task, Crew
from agent_eval.trace import ArcTracer

# Your CrewAI setup
agent = Agent(role="Financial Analyst", ...)
crew = Crew(agents=[agent], tasks=[...])

# Add monitoring
tracer = ArcTracer("finance")
traced_crew = tracer.trace_agent(crew)

# Execute with monitoring
result = traced_crew.kickoff()
```

#### AutoGen
```python
from autogen import ConversableAgent
from agent_eval.trace import ArcTracer

# Your AutoGen agent
agent = ConversableAgent(name="assistant", ...)

# Add monitoring
tracer = ArcTracer("finance")
traced_agent = tracer.trace_agent(agent)

# Use normally
response = traced_agent.generate_reply(messages)
```

### 3. CLI Commands

```bash
# Test the tracer
arc-eval trace --test

# View agent dashboard
arc-eval trace --agent-id my_agent --dashboard

# Live monitoring
arc-eval trace --agent-id my_agent --live

# Start API server
arc-eval trace --server --port 8000

# Export data
arc-eval trace --agent-id my_agent --export json
```

### 4. Dashboard & API Server

```bash
# Start the API server
arc-eval trace --server

# Access dashboard
open http://localhost:8000/agents/your_agent_id/dashboard
```

The dashboard provides:
- Real-time reliability scoring
- Cost tracking and optimization
- Performance metrics
- Failure analysis
- Interactive charts and trends

## API Reference

### ArcTracer

Main class for agent monitoring.

```python
class ArcTracer:
    def __init__(self, domain: str = "general", agent_id: Optional[str] = None)
    def trace_agent(self, agent: Any) -> TracedAgent
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def get_reliability_score(self) -> ReliabilityScore
    def get_agent_metrics(self) -> Optional[AgentMetrics]
```

### ReliabilityScore

```python
@dataclass
class ReliabilityScore:
    score: float        # 0-100
    grade: str         # A+, A, B+, B, C, D, F
    trend: str         # ↑ improving, ↓ declining, → stable
    confidence: float  # 0-1
    sample_size: int
```

### AgentMetrics

```python
@dataclass
class AgentMetrics:
    agent_id: str
    total_runs: int
    success_rate: float
    avg_duration_ms: float
    total_cost: float
    reliability_score: ReliabilityScore
    recent_failures: List[FailureInfo]
    cost_trend: str
    performance_trend: str
```

## Cost Tracking

### Supported Providers

- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic**: Claude-3.5-Sonnet, Claude-3.5-Haiku, Claude-3-Opus
- **Google**: Gemini-1.5-Pro, Gemini-1.5-Flash
- **Cerebras**: Llama-3.3-70B, Llama-3.1-8B

### Cost Optimization

```python
from agent_eval.trace.cost_tracker import CostTracker

tracker = CostTracker()

# Get optimization suggestions
suggestions = tracker.get_optimization_suggestions(
    current_provider="openai",
    current_model="gpt-4o",
    usage_stats={
        "cost_per_run": 0.15,
        "monthly_runs": 1000
    }
)

for suggestion in suggestions:
    print(f"💡 {suggestion['description']}")
```

## Data Sanitization

ARC-Eval automatically sanitizes sensitive information from traces:

### What's Sanitized
- **PII**: SSN, credit cards, emails, phone numbers, IP addresses
- **Credentials**: API keys, passwords, bearer tokens, secrets
- **Domain-specific**:
  - Finance: Account numbers, routing numbers, IBANs
  - Security: JWTs, private keys
  - ML: Model API tokens (Wandb, HuggingFace)

### Controlling Sanitization
```bash
# Disable for debugging (not recommended for production)
export ARC_ENABLE_SANITIZATION="false"
```

### Custom Redaction Rules
```python
from agent_eval.trace.sanitizer import RedactionRule
import re

# Add custom patterns
custom_rules = [
    RedactionRule(
        name="internal_id",
        pattern=re.compile(r'INTERNAL-\d{8}'),
        replacement="[REDACTED_INTERNAL_ID]"
    )
]

tracer = ArcTracer(domain="finance", custom_rules=custom_rules)
```

## Storage

Traces are stored locally in SQLite by default:
- Database location: `~/.arc-eval/traces.db`
- Automatic cleanup of old traces
- Postgres-ready schema for production

### Custom Storage

```python
from agent_eval.trace.storage import TraceStorage

# Custom database path
storage = TraceStorage(db_path="/path/to/custom.db")

# Get traces
traces = storage.get_recent_traces("agent_id", limit=10)
metrics = storage.get_agent_metrics("agent_id")
```

## Advanced Configuration

### Domain-Specific Monitoring

```python
# Finance domain with specialized patterns
tracer = ArcTracer(domain="finance")

# Security domain with threat detection
tracer = ArcTracer(domain="security")

# ML domain with bias detection
tracer = ArcTracer(domain="ml")
```

### Custom Framework Detection

```python
from agent_eval.trace.capture import TraceCapture

class CustomCapture(TraceCapture):
    def detect_framework(self, agent):
        if hasattr(agent, 'my_custom_method'):
            return 'my_framework'
        return super().detect_framework(agent)

# Use custom capture
tracer = ArcTracer()
tracer.capture = CustomCapture()
```

## Production Deployment

### Environment Variables

```bash
# Optional: Custom database path
export ARC_EVAL_DB_PATH="/path/to/production.db"

# API server configuration
export ARC_API_HOST="0.0.0.0"
export ARC_API_PORT="8000"

# CORS configuration (comma-separated origins)
export ALLOWED_ORIGINS="http://localhost:3000,https://your-domain.com"

# API authentication (comma-separated API keys)
export ARC_API_KEYS="your-secret-key-1,your-secret-key-2"

# Rate limiting (optional)
export ARC_RATE_LIMIT="100"  # requests per window
export ARC_RATE_WINDOW="60"  # seconds

# Data sanitization (enabled by default)
export ARC_ENABLE_SANITIZATION="true"  # Set to "false" to disable for debugging
```

### Docker Deployment

```dockerfile
FROM python:3.9-slim

RUN pip install arc-eval[server]

EXPOSE 8000

CMD ["arc-eval", "trace", "--server", "--port", "8000"]
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: arc-eval-trace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: arc-eval-trace
  template:
    metadata:
      labels:
        app: arc-eval-trace
    spec:
      containers:
      - name: arc-eval-trace
        image: arc-eval:latest
        ports:
        - containerPort: 8000
        command: ["arc-eval", "trace", "--server"]
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure `arc-eval` is installed
   ```bash
   pip install arc-eval
   ```

2. **FastAPI Missing**: For API server functionality
   ```bash
   pip install fastapi uvicorn
   ```

3. **Database Permissions**: Check write permissions for `~/.arc-eval/`
   ```bash
   mkdir -p ~/.arc-eval
   chmod 755 ~/.arc-eval
   ```

4. **Agent Not Detected**: Ensure your agent has common methods like `run`, `invoke`, or `execute`

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable verbose tracing
tracer = ArcTracer(domain="debug")
```

### Performance Impact

Runtime tracing adds minimal overhead:
- **Latency**: ~1-5ms per agent call
- **Memory**: ~10KB per trace
- **Storage**: ~1KB per trace in database

## Examples

### Complete Integration Example

```python
import time
from agent_eval.trace import ArcTracer

class MyAgent:
    def run(self, prompt):
        # Simulate agent work
        time.sleep(0.1)
        return f"Processed: {prompt}"

# Initialize monitoring
tracer = ArcTracer(domain="testing", agent_id="my_test_agent")
agent = tracer.trace_agent(MyAgent())

# Run some tasks
for i in range(10):
    try:
        result = agent.run(f"Task {i}")
        print(f"✅ {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

# Check results
metrics = tracer.get_agent_metrics()
print(f"Reliability: {metrics.reliability_score.grade}")
print(f"Success Rate: {metrics.success_rate:.1%}")
print(f"Avg Duration: {metrics.avg_duration_ms:.0f}ms")

# Stop monitoring
tracer.stop_monitoring()
```

### Multi-Agent Monitoring

```python
from agent_eval.trace import ArcTracer

# Monitor multiple agents
agents = {
    "financial": FinancialAgent(),
    "security": SecurityAgent(),
    "compliance": ComplianceAgent()
}

tracers = {}
for name, agent in agents.items():
    tracer = ArcTracer(domain=name, agent_id=f"{name}_agent")
    tracers[name] = tracer
    agents[name] = tracer.trace_agent(agent)

# Use agents normally - all are monitored
financial_result = agents["financial"].analyze_transaction(data)
security_result = agents["security"].check_threats(data)
compliance_result = agents["compliance"].verify_rules(data)

# View all metrics
for name, tracer in tracers.items():
    metrics = tracer.get_agent_metrics()
    print(f"{name}: {metrics.reliability_score.grade}")
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup and guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details. 