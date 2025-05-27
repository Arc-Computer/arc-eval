"""
Interactive menu system for the ARC-Eval CLI.
"""

from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns


console = Console()


class InteractiveMenu:
    """Interactive menu system for domain selection and user context."""
    
    def __init__(self):
        self.domain_info = self._get_domain_info()
        self.use_case_mapping = self._get_use_case_mapping()
    
    def _get_domain_info(self) -> Dict[str, Dict[str, any]]:
        """Get detailed domain information for interactive selection."""
        return {
            "finance": {
                "name": "Financial Services & Compliance",
                "icon": "💰",
                "description": "Banking, fintech, payments, insurance, investment compliance",
                "frameworks": ["SOX", "KYC", "AML", "PCI-DSS", "GDPR", "OFAC"],
                "scenarios": 110,
                "use_cases": [
                    "Transaction approval systems",
                    "KYC/identity verification",
                    "Fraud detection models",
                    "Credit scoring algorithms",
                    "Trading compliance bots",
                    "Financial document analysis"
                ],
                "business_value": "Ensure regulatory compliance, avoid fines, build customer trust",
                "typical_users": ["Compliance officers", "Risk managers", "Fintech developers", "Banking AI teams"]
            },
            "security": {
                "name": "Cybersecurity & AI Safety",
                "icon": "🔒",
                "description": "AI agents, chatbots, code generation, security tool evaluation",
                "frameworks": ["OWASP", "NIST-AI-RMF", "ISO-27001", "SOC2", "MITRE"],
                "scenarios": 120,
                "use_cases": [
                    "AI chatbot security testing",
                    "Code generation safety",
                    "Prompt injection detection",
                    "Data leakage prevention",
                    "Agent access control",
                    "Security tool validation"
                ],
                "business_value": "Prevent security breaches, protect sensitive data, ensure AI safety",
                "typical_users": ["Security engineers", "AI safety teams", "DevSecOps", "Cybersecurity analysts"]
            },
            "ml": {
                "name": "ML Infrastructure & Ethics",
                "icon": "🤖",
                "description": "MLOps, model deployment, bias detection, AI governance",
                "frameworks": ["EU-AI-ACT", "IEEE-ETHICS", "MODEL-CARDS", "NIST-AI-RMF"],
                "scenarios": 107,
                "use_cases": [
                    "Model bias detection",
                    "ML pipeline governance",
                    "Data quality validation",
                    "Model drift monitoring",
                    "Fairness assessment",
                    "AI ethics compliance"
                ],
                "business_value": "Build trustworthy AI, ensure fairness, meet regulatory requirements",
                "typical_users": ["ML engineers", "Data scientists", "AI ethics officers", "MLOps teams"]
            }
        }
    
    def _get_use_case_mapping(self) -> Dict[str, str]:
        """Map user descriptions to domains."""
        return {
            # Finance keywords
            "banking": "finance",
            "financial": "finance", 
            "payment": "finance",
            "transaction": "finance",
            "compliance": "finance",
            "fraud": "finance",
            "credit": "finance",
            "loan": "finance",
            "investment": "finance",
            "trading": "finance",
            "kyc": "finance",
            "aml": "finance",
            
            # Security keywords
            "security": "security",
            "cybersecurity": "security",
            "chatbot": "security",
            "ai agent": "security",
            "prompt": "security",
            "injection": "security",
            "safety": "security",
            "penetration": "security",
            "vulnerability": "security",
            "data protection": "security",
            
            # ML keywords
            "machine learning": "ml",
            "model": "ml",
            "bias": "ml",
            "fairness": "ml",
            "mlops": "ml",
            "data science": "ml",
            "algorithm": "ml",
            "prediction": "ml",
            "classification": "ml",
            "ethics": "ml"
        }
    
    def domain_selection_menu(self) -> str:
        """Present interactive domain selection menu."""
        console.print("\n[bold blue]🎯 Welcome to ARC-Eval![/bold blue]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        console.print("[bold]Let's find the right evaluation domain for your AI system...[/bold]\n")
        
        # Option 1: Quick AI system description
        console.print("[bold blue]Option 1: Describe Your AI System[/bold blue]")
        console.print("[dim]Tell us what your AI system does, and we'll recommend the best domain[/dim]\n")
        
        # Show examples to guide user
        console.print("[bold]Examples:[/bold]")
        console.print("• 'We have a chatbot that helps with customer banking questions'")
        console.print("• 'Our AI generates code and we need security testing'") 
        console.print("• 'We built a fraud detection model for credit cards'")
        console.print("• 'Our system processes loan applications automatically'\n")
        
        use_description = Confirm.ask("Would you like to describe your AI system?", default=True)
        
        if use_description:
            description = Prompt.ask("[bold]Describe your AI system")
            recommended_domain = self._recommend_domain_from_description(description)
            
            if recommended_domain:
                domain_info = self.domain_info[recommended_domain]
                console.print(f"\n[green]✨ Recommended Domain: {domain_info['icon']} {domain_info['name']}[/green]")
                console.print(f"[dim]Based on your description, this domain covers: {domain_info['description']}[/dim]")
                
                use_recommendation = Confirm.ask(f"Use {recommended_domain} domain?", default=True)
                if use_recommendation:
                    return recommended_domain
        
        # Option 2: Browse domains
        console.print("\n[bold blue]Option 2: Browse Available Domains[/bold blue]")
        console.print("[dim]Explore all domains and choose the one that fits your needs[/dim]\n")
        
        return self._display_domain_browser()
    
    def _recommend_domain_from_description(self, description: str) -> Optional[str]:
        """Recommend domain based on user description."""
        description_lower = description.lower()
        
        # Score each domain based on keyword matches
        domain_scores = {"finance": 0, "security": 0, "ml": 0}
        
        for keyword, domain in self.use_case_mapping.items():
            if keyword in description_lower:
                domain_scores[domain] += 1
        
        # Return domain with highest score, if any
        max_score = max(domain_scores.values())
        if max_score > 0:
            return max(domain_scores, key=domain_scores.get)
        
        return None
    
    def _display_domain_browser(self) -> str:
        """Display interactive domain browser."""
        
        # Create domain overview table
        table = Table(show_header=True, header_style="bold blue", border_style="blue")
        table.add_column("Domain", style="bold", width=12)
        table.add_column("Focus Area", width=25)
        table.add_column("Scenarios", justify="center", width=10)
        table.add_column("Key Use Cases", width=35)
        
        domain_choices = []
        for key, info in self.domain_info.items():
            table.add_row(
                f"{info['icon']} {key.upper()}",
                info['name'],
                str(info['scenarios']),
                ", ".join(info['use_cases'][:3]) + "..."
            )
            domain_choices.append(key)
        
        console.print(table)
        console.print()
        
        # Get user selection
        while True:
            choice = Prompt.ask(
                "[bold]Select domain[/bold]",
                choices=domain_choices + ["details"],
                default=domain_choices[0]
            )
            
            if choice == "details":
                selected_domain = self._show_domain_details()
                if selected_domain:
                    return selected_domain
            else:
                return choice
    
    def _show_domain_details(self) -> Optional[str]:
        """Show detailed information for each domain."""
        console.print("\n[bold blue]📋 Detailed Domain Information[/bold blue]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        
        panels = []
        for key, info in self.domain_info.items():
            content = []
            content.append(f"[bold]{info['description']}[/bold]\n")
            
            content.append("[yellow]🎯 Key Use Cases:[/yellow]")
            for use_case in info['use_cases'][:4]:
                content.append(f"  • {use_case}")
            
            content.append(f"\n[yellow]⚖️ Compliance Frameworks:[/yellow]")
            content.append(f"  • {', '.join(info['frameworks'][:4])}")
            
            content.append(f"\n[yellow]👥 Typical Users:[/yellow]")
            content.append(f"  • {', '.join(info['typical_users'][:2])}")
            
            content.append(f"\n[yellow]💼 Business Value:[/yellow]")
            content.append(f"  • {info['business_value']}")
            
            content.append(f"\n[green]📊 {info['scenarios']} evaluation scenarios available[/green]")
            
            panel = Panel(
                "\n".join(content),
                title=f"{info['icon']} {info['name']}",
                border_style="blue"
            )
            panels.append(panel)
        
        console.print(Columns(panels, equal=True, expand=True))
        console.print()
        
        # Get selection after showing details
        domain_choices = list(self.domain_info.keys())
        choice = Prompt.ask(
            "[bold]Select domain[/bold]",
            choices=domain_choices + ["back"],
            default=domain_choices[0]
        )
        
        return choice if choice != "back" else None
    
    def get_user_context(self, domain: str) -> Dict[str, any]:
        """Gather user context for personalized experience."""
        console.print(f"\n[bold blue]🎯 Personalizing Your {domain.title()} Demo[/bold blue]")
        console.print("[blue]═══════════════════════════════════════════════════════════════════════[/blue]")
        
        domain_info = self.domain_info[domain]
        
        # Role selection
        console.print("[bold]What's your role?[/bold]")
        role_choices = domain_info['typical_users'] + ["Other"]
        
        role = Prompt.ask(
            "Select your role",
            choices=[r.lower().replace(" ", "_") for r in role_choices] + ["other"],
            default=role_choices[0].lower().replace(" ", "_")
        )
        
        # Experience level
        experience = Prompt.ask(
            "[bold]How experienced are you with AI evaluation?[/bold]",
            choices=["beginner", "intermediate", "expert"],
            default="intermediate"
        )
        
        # Primary goal
        console.print(f"\n[bold]What's your primary goal with {domain} evaluation?[/bold]")
        if domain == "finance":
            goal_choices = ["compliance_audit", "risk_assessment", "model_validation", "regulatory_reporting"]
        elif domain == "security":
            goal_choices = ["security_testing", "vulnerability_assessment", "ai_safety", "penetration_testing"]
        else:  # ml
            goal_choices = ["bias_detection", "model_governance", "fairness_assessment", "ethics_compliance"]
        
        goal = Prompt.ask(
            "Select primary goal",
            choices=goal_choices,
            default=goal_choices[0]
        )
        
        return {
            "domain": domain,
            "role": role,
            "experience": experience,
            "goal": goal,
            "show_technical_details": experience in ["intermediate", "expert"],
            "show_business_context": role in ["compliance_officers", "risk_managers", "other"]
        }