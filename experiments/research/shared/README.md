# Shared Utilities & Helpers

**Purpose**: Common functionality used across all experiment phases

## Shared Components

### Core Utilities
- **Configuration Management**: Experiment settings and parameters
- **Logging System**: Consistent logging across all phases  
- **Data Helpers**: Common data processing and formatting
- **Validation Tools**: Shared validation and verification functions

### Integration Helpers
- **ARC-Eval Interface**: Wrapper functions for existing components
- **Metrics Collection**: Standardized performance tracking
- **Chart Generation**: Common visualization utilities
- **Export Functions**: Consistent output formatting

## Files to Create

### Configuration & Setup
- `config.py` - Experiment configuration management
- `logger.py` - Standardized logging setup
- `constants.py` - Shared constants and parameters

### Data Processing
- `data_helpers.py` - Common data processing functions
- `validation.py` - Shared validation utilities
- `formatters.py` - Output formatting helpers

### ARC-Eval Integration
- `arc_eval_wrapper.py` - Interface to existing components
- `scenario_loader.py` - 378 scenario management
- `evaluation_runner.py` - Consistent evaluation execution

### Analysis & Visualization
- `metrics_collector.py` - Performance tracking utilities
- `chart_generator.py` - Visualization helper functions
- `report_builder.py` - Report generation utilities

## Design Principles

### Leverage Existing Infrastructure
- Use existing `agent_eval/` components wherever possible
- Minimal new development, maximum reuse
- Maintain compatibility with current CLI workflows

### Academic Research Integration
- Support for curriculum learning methodology
- Skill-based targeting implementation helpers
- Scenario-based improvement tracking

### Reproducibility Focus
- Consistent data formats across phases
- Standardized metrics collection
- Repeatable experimental procedures

## Usage Pattern

```python
# Example usage across phases
from shared.config import ExperimentConfig
from shared.arc_eval_wrapper import run_evaluation
from shared.metrics_collector import track_performance

config = ExperimentConfig()
results = run_evaluation(agent_outputs, config.domain)
metrics = track_performance(results, iteration=1)
```

This ensures consistency and reproducibility across all experiment phases.