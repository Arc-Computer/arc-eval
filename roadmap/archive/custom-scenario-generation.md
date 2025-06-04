# Custom Scenario Generation Implementation Plan

## Overview

This document outlines the implementation plan for adding custom scenario generation capabilities to ARC-Eval, enabling users to create evaluation scenarios beyond the predefined finance, security, and ML domains. The feature will leverage LLMs to generate rich, domain-specific scenarios with the same depth and quality as the existing domain packs.

## Core Requirements

1. **Custom Domain Support**: Allow scenarios for any domain (healthcare, logistics, retail, etc.)
2. **LLM-Powered Generation**: Use AI to create comprehensive scenarios matching ARC-Eval's quality
3. **Terminal UI Integration**: Beautiful CLI experience consistent with existing interfaces
4. **Scenario Depth**: Match the complexity of existing domain packs (110-148 scenarios per domain)
5. **Runtime Integration**: Scenarios work seamlessly with evaluation engine

## Architecture Design

### 1. Data Model Extensions

```python
# agent_eval/core/types.py additions

@dataclass
class CustomDomain:
    """User-defined evaluation domain."""
    name: str  # e.g., "healthcare", "logistics"
    description: str
    compliance_frameworks: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
@dataclass
class ScenarioTemplate:
    """Template for LLM-based scenario generation."""
    domain: str
    category: str
    complexity_level: str  # "basic", "intermediate", "advanced"
    compliance_focus: Optional[List[str]] = None
    example_context: Optional[str] = None
```

### 2. LLM Scenario Generator

```python
# agent_eval/core/scenario_generator.py (new file)

class LLMScenarioGenerator:
    """Generate evaluation scenarios using LLMs."""
    
    def __init__(self, provider: str = "anthropic"):
        self.provider = provider
        self.api_manager = APIManager(provider)
        
    def generate_domain_pack(
        self, 
        domain_name: str,
        domain_description: str,
        target_scenarios: int = 50,
        compliance_frameworks: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate a complete domain pack using LLM."""
        
        # Step 1: Generate domain categories
        categories = self._generate_categories(domain_name, domain_description)
        
        # Step 2: Generate scenarios per category
        scenarios = []
        for category in categories:
            category_scenarios = self._generate_category_scenarios(
                domain_name, category, 
                scenarios_per_category=target_scenarios // len(categories)
            )
            scenarios.extend(category_scenarios)
            
        # Step 3: Enhance with compliance mappings
        if compliance_frameworks:
            scenarios = self._add_compliance_mappings(scenarios, compliance_frameworks)
            
        return self._format_domain_pack(domain_name, domain_description, categories, scenarios)
        
    def _generate_category_scenarios(self, domain: str, category: str, count: int) -> List[Dict]:
        """Generate scenarios for a specific category."""
        
        prompt = f"""Generate {count} evaluation scenarios for {domain} domain, category: {category}.
        
        Each scenario must include:
        - id: Unique identifier ({domain[:3]}_{category[:3]}_XXX format)
        - name: Descriptive name (max 60 chars)
        - description: Detailed description of what to test
        - severity: critical/high/medium/low
        - test_type: negative/positive/adversarial
        - expected_behavior: What the agent should do
        - failure_indicators: List of 3-5 signs of failure
        - remediation: How to fix if failed
        
        Match the depth and quality of these examples:
        {self._get_example_scenarios()}
        
        Return as JSON array."""
        
        response = self.api_manager.generate(prompt)
        return json.loads(response)
```

### 3. CLI Commands

```python
# agent_eval/cli.py additions

@cli.group()
def scenario():
    """Create and manage custom evaluation scenarios."""
    pass

@scenario.command()
@click.option('--domain', required=True, help='Custom domain name (e.g., healthcare)')
@click.option('--description', help='Domain description')
@click.option('--interactive', is_flag=True, help='Interactive wizard mode')
@click.option('--from-task', help='Generate from task description')
@click.option('--scenarios', default=50, help='Number of scenarios to generate')
def create(domain: str, description: str, interactive: bool, from_task: str, scenarios: int):
    """Create custom evaluation scenarios with LLM assistance."""
    
    if interactive:
        wizard = ScenarioCreationWizard()
        wizard.run()
    elif from_task:
        generator = TaskBasedGenerator()
        generator.create_from_task(from_task, domain)
    else:
        generator = LLMScenarioGenerator()
        pack = generator.generate_domain_pack(domain, description, scenarios)
        save_custom_domain(pack)

@scenario.command()
@click.option('--domain', help='Filter by domain')
def list(domain: Optional[str]):
    """List available custom scenarios."""
    dashboard = ScenarioDashboard()
    dashboard.display_scenarios(domain)

@scenario.command()
@click.option('--file', type=click.Path(exists=True), help='Import scenarios from file')
@click.option('--format', type=click.Choice(['yaml', 'json']), default='yaml')
def import_scenarios(file: Path, format: str):
    """Import scenarios from external file."""
    importer = ScenarioImporter()
    importer.import_from_file(file, format)
```

### 4. Terminal UI Components

```python
# agent_eval/ui/scenario_wizard.py (new file)

class ScenarioCreationWizard:
    """Interactive scenario creation wizard."""
    
    def run(self):
        console = Console()
        
        # Step 1: Domain Selection
        domain = self._select_domain()
        
        # Step 2: Compliance Frameworks
        frameworks = self._select_compliance_frameworks()
        
        # Step 3: Scenario Generation Options
        options = self._configure_generation()
        
        # Step 4: LLM Generation with Progress
        with Progress() as progress:
            task = progress.add_task("Generating scenarios...", total=options['count'])
            scenarios = self._generate_with_progress(domain, options, progress, task)
        
        # Step 5: Review and Edit
        self._review_scenarios(scenarios)
        
        # Step 6: Save
        self._save_scenarios(domain, scenarios)
        
    def _select_domain(self) -> str:
        """Interactive domain selection."""
        table = Table(title="Select Domain Type")
        table.add_column("Option", style="cyan")
        table.add_column("Domain", style="green")
        table.add_column("Description")
        
        domains = [
            ("1", "healthcare", "Medical records, HIPAA, patient safety"),
            ("2", "logistics", "Supply chain, tracking, optimization"),
            ("3", "retail", "E-commerce, inventory, customer service"),
            ("4", "education", "Student data, assessments, compliance"),
            ("5", "custom", "Define your own domain")
        ]
        
        for opt, name, desc in domains:
            table.add_row(opt, name, desc)
            
        console.print(table)
        choice = Prompt.ask("Select domain", choices=["1","2","3","4","5"])
        
        if choice == "5":
            return Prompt.ask("Enter custom domain name")
        else:
            return domains[int(choice)-1][1]
```

### 5. Scenario Preview UI

```python
# agent_eval/ui/scenario_preview.py

def display_scenario_preview(scenario: Dict[str, Any]):
    """Display beautiful scenario preview."""
    
    console = Console()
    
    # Create preview panel
    preview = Panel(
        f"""[bold cyan]Scenario: {scenario['name']}[/bold cyan]
        
[yellow]Domain:[/yellow] {scenario.get('domain', 'custom')}
[yellow]Category:[/yellow] {scenario.get('category', 'general')}
[yellow]Severity:[/yellow] {_severity_badge(scenario['severity'])}
[yellow]Type:[/yellow] {scenario['test_type']}

[bold]Description:[/bold]
{scenario['description']}

[bold]Expected Behavior:[/bold]
{scenario['expected_behavior']}

[bold]Failure Indicators:[/bold]
{_format_indicators(scenario['failure_indicators'])}

[bold]Remediation:[/bold]
{scenario['remediation']}

[dim]ID: {scenario['id']}[/dim]""",
        title="Scenario Preview",
        border_style="green"
    )
    
    console.print(preview)
```

### 6. Integration with Existing Systems

```python
# agent_eval/core/engine.py modifications

def _load_eval_pack(self) -> EvaluationPack:
    """Enhanced to support custom domains."""
    
    if self.domain.startswith("custom:"):
        # Load custom domain
        custom_name = self.domain.split(":", 1)[1]
        return self._load_custom_domain(custom_name)
    elif self.config:
        # Existing custom config logic
        ...
    else:
        # Existing built-in domain logic
        ...
        
def _load_custom_domain(self, domain_name: str) -> EvaluationPack:
    """Load user-created custom domain."""
    
    custom_file = Path.home() / ".arc-eval" / "domains" / f"{domain_name}.yaml"
    if not custom_file.exists():
        raise FileNotFoundError(f"Custom domain not found: {domain_name}")
        
    with open(custom_file, 'r') as f:
        data = yaml.safe_load(f)
        
    return EvaluationPack.from_dict(data)
```

## Implementation Timeline

### Week 1: Foundation
- [ ] Extend type system for custom domains
- [ ] Create scenario generator base class
- [ ] Add CLI command structure

### Week 2: LLM Integration
- [ ] Implement LLM scenario generation
- [ ] Create prompt templates for quality
- [ ] Add batch generation with progress

### Week 3: Terminal UI
- [ ] Build interactive wizard
- [ ] Create scenario preview components
- [ ] Add editing capabilities

### Week 4: Polish & Testing
- [ ] Integration testing with engine
- [ ] Performance optimization
- [ ] Documentation and examples

## Usage Examples

### 1. Quick Generation from Task
```bash
arc-eval scenario create --from-task "Evaluate medical chatbot for HIPAA compliance"
# Generates healthcare domain with HIPAA-focused scenarios
```

### 2. Interactive Wizard
```bash
arc-eval scenario create --interactive
# Step-by-step guided creation with previews
```

### 3. Domain Pack Generation
```bash
arc-eval scenario create \
  --domain logistics \
  --description "Supply chain and delivery tracking" \
  --scenarios 100
# Generates complete domain pack with 100 scenarios
```

### 4. Import Existing Scenarios
```bash
arc-eval scenario import --file custom_tests.yaml
# Import scenarios from external source
```

## Quality Assurance

### LLM Prompt Engineering
- Use few-shot examples from existing high-quality scenarios
- Enforce structured output with JSON schema validation
- Quality scoring and filtering of generated scenarios

### Scenario Validation
- Automatic validation against schema
- Duplicate detection and merging
- Compliance framework verification

### User Review Process
- Preview all generated scenarios
- Edit capabilities for refinement
- Approval workflow before saving

## Storage Structure

```
~/.arc-eval/
├── domains/
│   ├── healthcare.yaml      # Custom domain packs
│   ├── logistics.yaml
│   └── retail.yaml
├── scenarios/
│   ├── drafts/             # Work in progress
│   └── templates/          # User templates
└── config/
    └── generator.yaml      # LLM settings
```

## Future Enhancements

1. **Scenario Marketplace**: Share scenarios with community
2. **Learning from Traces**: Auto-generate from runtime failures
3. **Multi-Language Support**: Generate scenarios in different languages
4. **Compliance Mapping AI**: Automatic regulatory mapping
5. **Scenario Versioning**: Track changes over time

## Success Metrics

- Generate 50+ scenarios in <2 minutes
- 90%+ scenarios pass quality validation
- User satisfaction with generated content
- Seamless integration with existing workflows