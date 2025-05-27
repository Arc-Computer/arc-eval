"""
Guided next steps system for enhanced user onboarding and engagement.
"""

from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text


console = Console()


class NextStepsGuide:
    """Generate personalized next steps and guidance for users."""
    
    def __init__(self):
        self.integration_templates = self._get_integration_templates()
        self.learning_paths = self._get_learning_paths()
    
    def _get_integration_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get integration templates for different platforms."""
        return {
            "github_actions": {
                "name": "GitHub Actions CI/CD",
                "description": "Automated compliance checking in your CI pipeline",
                "command": "# Add to .github/workflows/compliance.yml\n- run: arc-eval --domain {domain} --input ${{{{ github.workspace }}}}/outputs.json",
                "benefits": ["Continuous compliance monitoring", "Block non-compliant deployments", "Automated audit reports"]
            },
            "docker": {
                "name": "Docker Container",
                "description": "Containerized evaluation for consistent environments",
                "command": "docker run -v $(pwd):/data arc-eval:latest --domain {domain} --input /data/outputs.json",
                "benefits": ["Consistent evaluation environment", "Easy deployment", "Scalable processing"]
            },
            "python_script": {
                "name": "Python Script Integration",
                "description": "Programmatic evaluation in your Python applications",
                "command": "# In your Python code\nfrom agent_eval.core.engine import EvaluationEngine\nengine = EvaluationEngine(domain='{domain}')",
                "benefits": ["Programmatic control", "Custom workflows", "Integration with existing tools"]
            },
            "api_endpoint": {
                "name": "API Endpoint Monitoring",
                "description": "Monitor live API endpoints for compliance",
                "command": "arc-eval --domain {domain} --endpoint https://your-api.com/evaluate",
                "benefits": ["Live monitoring", "Real-time alerts", "Production compliance tracking"]
            }
        }
    
    def _get_learning_paths(self) -> Dict[str, Dict[str, Any]]:
        """Get learning paths for different user types."""
        return {
            "beginner": {
                "name": "Getting Started Path",
                "description": "Learn the basics of AI evaluation with ARC-Eval",
                "steps": [
                    {"title": "Try all domains", "command": "arc-eval --list-domains", "description": "Explore finance, security, and ML domains"},
                    {"title": "Learn input formats", "command": "arc-eval --help-input", "description": "Understand supported data formats"},
                    {"title": "Validate your data", "command": "arc-eval --validate --input your_file.json", "description": "Check if your data is compatible"},
                    {"title": "Generate your first report", "command": "arc-eval --domain {domain} --input your_file.json --export pdf", "description": "Create a professional audit report"}
                ]
            },
            "intermediate": {
                "name": "Advanced Features Path", 
                "description": "Explore advanced evaluation features and integrations",
                "steps": [
                    {"title": "Try Agent-as-a-Judge", "command": "arc-eval --domain {domain} --input your_file.json --agent-judge", "description": "Use AI-powered evaluation with continuous feedback"},
                    {"title": "Enable verification", "command": "arc-eval --domain {domain} --input your_file.json --agent-judge --verify", "description": "Add verification layer for improved reliability"},
                    {"title": "Benchmark evaluation", "command": "arc-eval --benchmark mmlu --subset anatomy --limit 20", "description": "Test against academic benchmarks"},
                    {"title": "CI/CD integration", "command": "# Setup continuous compliance monitoring", "description": "Integrate into your development workflow"}
                ]
            },
            "expert": {
                "name": "Enterprise Integration Path",
                "description": "Advanced enterprise features and customization",
                "steps": [
                    {"title": "Custom scenarios", "command": "arc-eval --config custom_scenarios.yaml --input your_file.json", "description": "Create domain-specific evaluation scenarios"},
                    {"title": "Batch processing", "command": "arc-eval --domain {domain} --input large_dataset.json --summary-only", "description": "Process large datasets efficiently"},
                    {"title": "Cost optimization", "command": "arc-eval --domain {domain} --agent-judge --judge-model claude-3-5-haiku-latest", "description": "Optimize evaluation costs"},
                    {"title": "API integration", "command": "# Build custom evaluation pipelines", "description": "Programmatic integration for enterprise workflows"}
                ]
            }
        }
    
    def generate_personalized_guide(self, user_context: Dict[str, Any], evaluation_results: Optional[List[Any]] = None) -> None:
        """Generate and display personalized next steps guide."""
        
        domain = user_context.get("domain", "finance")
        role = user_context.get("role", "user")
        experience = user_context.get("experience", "intermediate")
        goal = user_context.get("goal", "compliance_audit")
        
        console.print(f"\n[bold blue]🎯 Your Personalized ARC-Eval Journey[/bold blue]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        
        # Show immediate next steps based on evaluation results
        if evaluation_results:
            self._show_immediate_actions(evaluation_results, domain, role)
        
        # Show learning path
        self._show_learning_path(experience, domain)
        
        # Show integration options
        self._show_integration_options(role, domain, goal)
        
        # Show domain expansion opportunities
        self._show_domain_expansion(domain)
        
        # Show community and support resources
        self._show_resources(experience)
    
    def _show_immediate_actions(self, results: List[Any], domain: str, role: str) -> None:
        """Show immediate actions based on evaluation results."""
        
        # Calculate basic stats (assuming results have passed/failed attributes)
        total = len(results)
        passed = sum(1 for r in results if getattr(r, 'passed', True))
        failed = total - passed
        critical_failures = sum(1 for r in results if getattr(r, 'severity', '') == 'critical' and not getattr(r, 'passed', True))
        
        console.print("\n[bold green]✅ Immediate Next Steps[/bold green]")
        
        if critical_failures > 0:
            console.print(f"[bold red]🚨 URGENT: {critical_failures} critical issues require immediate attention[/bold red]")
            console.print("\n[bold]Next step - evaluate your real system:[/bold]")
            console.print(f"[green]arc-eval --domain {domain} --input path/to/your/outputs.json --agent-judge --export pdf[/green]")
            console.print("[dim]Replace path/to/your/outputs.json with your actual agent output file[/dim]")
            
        elif failed > 0:
            console.print(f"[yellow]⚠️ {failed} scenarios failed - review recommended[/yellow]")
            console.print("\n[bold]Next step - evaluate your real system:[/bold]")
            console.print(f"[green]arc-eval --domain {domain} --input path/to/your/outputs.json --export pdf --workflow[/green]")
            
        else:
            console.print(f"[green]🎉 Demo passed! Now test with your real {domain} system:[/green]")
            console.print(f"[green]arc-eval --domain {domain} --input path/to/your/outputs.json[/green]")
        
        console.print()
    
    def _show_learning_path(self, experience: str, domain: str) -> None:
        """Show personalized learning path."""
        
        path = self.learning_paths.get(experience, self.learning_paths["intermediate"])
        
        console.print(f"[bold blue]📚 {path['name']}[/bold blue]")
        console.print(f"[dim]{path['description']}[/dim]\n")
        
        # Create learning steps table
        table = Table(show_header=True, header_style="bold blue", border_style="blue")
        table.add_column("Step", style="bold", width=8)
        table.add_column("Action", width=25)
        table.add_column("Command", style="green", width=45)
        
        for i, step in enumerate(path['steps'], 1):
            command = step['command'].format(domain=domain)
            table.add_row(
                f"Step {i}",
                step['title'],
                command
            )
        
        console.print(table)
        console.print()
    
    def _show_integration_options(self, role: str, domain: str, goal: str) -> None:
        """Show relevant integration options."""
        
        console.print("[bold blue]🔧 Integration Options[/bold blue]")
        console.print("[dim]Choose the integration that fits your workflow[/dim]\n")
        
        # Filter integrations based on role and goal
        relevant_integrations = []
        
        if role in ["compliance_officers", "risk_managers"]:
            relevant_integrations = ["api_endpoint", "github_actions"]
        elif role in ["developers", "engineers"]:
            relevant_integrations = ["github_actions", "docker", "python_script"]
        else:
            relevant_integrations = ["github_actions", "python_script"]
        
        # Create integration panels
        panels = []
        for integration_key in relevant_integrations:
            integration = self.integration_templates[integration_key]
            
            content = f"[bold]{integration['description']}[/bold]\n\n"
            content += "[yellow]Command:[/yellow]\n"
            content += f"[green]{integration['command'].format(domain=domain)}[/green]\n\n"
            content += "[yellow]Benefits:[/yellow]\n"
            for benefit in integration['benefits']:
                content += f"• {benefit}\n"
            
            panel = Panel(
                content.rstrip(),
                title=f"🔧 {integration['name']}",
                border_style="blue"
            )
            panels.append(panel)
        
        console.print(Columns(panels, equal=True, expand=True))
        console.print()
    
    def _show_domain_expansion(self, current_domain: str) -> None:
        """Show opportunities to explore other domains."""
        
        other_domains = {"finance", "security", "ml"} - {current_domain}
        
        console.print("[bold blue]🌐 Explore Other Domains[/bold blue]")
        console.print("[dim]Expand your evaluation coverage across different AI systems[/dim]\n")
        
        domain_info = {
            "finance": {"icon": "💰", "desc": "Banking, payments, trading compliance"},
            "security": {"icon": "🔒", "desc": "AI safety, prompt injection, data protection"},
            "ml": {"icon": "🤖", "desc": "Bias detection, model governance, ethics"}
        }
        
        for domain in other_domains:
            info = domain_info[domain]
            console.print(f"{info['icon']} [bold]{domain.title()}:[/bold] {info['desc']}")
            console.print(f"   [green]arc-eval --quick-start --domain {domain}[/green]")
        
        console.print()
    
    def _show_resources(self, experience: str) -> None:
        """Show community and support resources."""
        
        console.print("[bold blue]🎓 Resources & Support[/bold blue]")
        
        resources = []
        
        if experience == "beginner":
            resources = [
                {"title": "📖 Documentation", "desc": "Complete guide to ARC-Eval features", "action": "Visit examples/ directory"},
                {"title": "💬 Community", "desc": "Join discussions and get help", "action": "GitHub Discussions"},
                {"title": "🎥 Tutorials", "desc": "Video walkthroughs and examples", "action": "Check README for links"},
            ]
        else:
            resources = [
                {"title": "🔧 Advanced Config", "desc": "Custom scenarios and templates", "action": "See config/ directory"},
                {"title": "📊 Benchmarks", "desc": "Academic evaluation datasets", "action": "Try --benchmark mmlu/humeval/gsm8k"},
                {"title": "🤝 Enterprise", "desc": "Custom domains and enterprise features", "action": "Contact for enterprise support"},
            ]
        
        for resource in resources:
            console.print(f"{resource['title']}: {resource['desc']}")
            console.print(f"   [dim]{resource['action']}[/dim]")
        
        console.print()
    
    def generate_copy_paste_commands(self, user_context: Dict[str, Any]) -> List[str]:
        """Generate ready-to-use commands based on user context."""
        
        domain = user_context.get("domain", "finance")
        experience = user_context.get("experience", "intermediate")
        goal = user_context.get("goal", "compliance_audit")
        
        commands = []
        
        # Basic evaluation
        commands.append(f"# Evaluate your {domain} system")
        commands.append(f"arc-eval --domain {domain} --input path/to/your/outputs.json")
        
        # Advanced features
        if experience in ["intermediate", "expert"]:
            commands.append(f"\n# With AI-powered evaluation")
            commands.append(f"arc-eval --domain {domain} --input path/to/your/outputs.json --agent-judge")
        
        # Goal-specific commands
        if goal == "compliance_audit":
            commands.append(f"\n# Generate compliance report")
            commands.append(f"arc-eval --domain {domain} --input path/to/your/outputs.json --export pdf --workflow")
        elif goal == "model_validation":
            commands.append(f"\n# Validate with verification")
            commands.append(f"arc-eval --domain {domain} --input path/to/your/outputs.json --agent-judge --verify")
        
        # Enterprise features
        if experience == "expert":
            commands.append(f"\n# CI/CD integration (GitHub Actions)")
            commands.append(f"# Add to .github/workflows/compliance.yml:")
            commands.append(f"- run: arc-eval --domain {domain} --input outputs.json --export json")
        
        return commands