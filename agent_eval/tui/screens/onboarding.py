"""
Onboarding Screen for ARC-Eval TUI.

Provides first-time user onboarding with welcome message,
quick tutorial, and persona selection for optimal experience.
"""

from textual import on
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Static, Select


class OnboardingScreen(Screen):
    """Onboarding screen for first-time users."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_persona = None
    
    def compose(self):
        """Create the onboarding screen layout."""
        with Vertical():
            # Welcome header
            yield Static("🚀 Welcome to ARC-Eval Interactive!", classes="onboarding-welcome")
            yield Static("The definitive agent safety workbench for compliance evaluation", classes="onboarding-welcome")
            
            # Introduction
            with Container(classes="onboarding-step"):
                yield Static("🛡️ What is ARC-Eval?", classes="section-title")
                yield Static("""
ARC-Eval helps you evaluate AI agents for safety, reliability, and compliance.
• Domain-specific evaluations (Finance, Security, ML)
• Real-time progress monitoring
• Audit-ready reports (PDF, CSV, JSON)
• Framework auto-detection (OpenAI, Anthropic, LangChain, etc.)
                """)
            
            # Persona selection
            with Container(classes="onboarding-step"):
                yield Static("👥 Select Your Use Case", classes="section-title")
                yield Static("Choose the option that best describes your role:")
                yield Select(
                    [
                        ("🏦 Finance/Compliance Team - Regulatory compliance evaluation", "finance"),
                        ("🔒 Security/Red Team - Vulnerability assessment and testing", "security"),
                        ("🤖 ML/Research Team - Model safety and bias detection", "research"),
                        ("🏢 General Use - Explore all capabilities", "general")
                    ],
                    value="general",
                    id="persona-select"
                )
            
            # Quick start guide
            with Container(classes="onboarding-step"):
                yield Static("🚀 Quick Start", classes="section-title")
                yield Static("""
Getting started is easy:
1. Select your agent output files (.json, .csv, .jsonl)
2. Choose an evaluation domain (Finance, Security, ML)
3. Run evaluation and see real-time progress
4. Review results and export reports

Keyboard shortcuts:
• Ctrl+O - Open files
• Ctrl+R - Run evaluation
• Ctrl+S - Save session
• F1 - Help
                """)
            
            # Action buttons
            with Horizontal(classes="action-buttons"):
                yield Button("📚 Take Tutorial", id="tutorial-btn", variant="secondary")
                yield Button("🎯 Start Evaluating", id="start-btn", variant="primary")
                yield Button("⏭️ Skip Onboarding", id="skip-btn", variant="secondary")
    
    @on(Select.Changed, "#persona-select")
    def handle_persona_change(self, event: Select.Changed):
        """Handle persona selection change."""
        if event.value:
            self.selected_persona = event.value
            
            # Update tutorial button text based on persona
            tutorial_btn = self.query_one("#tutorial-btn", Button)
            persona_tutorials = {
                "finance": "📚 Finance Tutorial",
                "security": "📚 Security Tutorial", 
                "research": "📚 Research Tutorial",
                "general": "📚 General Tutorial"
            }
            tutorial_btn.label = persona_tutorials.get(event.value, "📚 Take Tutorial")
    
    @on(Button.Pressed, "#start-btn")
    def handle_start_button(self):
        """Handle start button press."""
        # Mark onboarding as completed
        if hasattr(self.app, 'app_state') and self.app.app_state:
            self.app.app_state.user_preferences["first_launch"] = False
        
        # Navigate to main screen
        from .main import MainScreen
        self.app.push_screen(MainScreen())
        
        # Show welcome message based on persona
        persona_messages = {
            "finance": "Welcome! Ready to evaluate financial compliance.",
            "security": "Welcome! Ready to run security assessments.",
            "research": "Welcome! Ready to analyze ML model safety.",
            "general": "Welcome! Explore all ARC-Eval capabilities."
        }
        message = persona_messages.get(self.selected_persona, "Welcome to ARC-Eval!")
        self.app.notify(message, severity="success")
    
    @on(Button.Pressed, "#skip-btn")
    def handle_skip_button(self):
        """Handle skip button press."""
        # Mark onboarding as completed
        if hasattr(self.app, 'app_state') and self.app.app_state:
            self.app.app_state.user_preferences["first_launch"] = False
        
        # Navigate to main screen
        from .main import MainScreen
        self.app.push_screen(MainScreen())
        
        self.app.notify("Onboarding skipped. Press F1 for help anytime.", severity="information")
    
    @on(Button.Pressed, "#tutorial-btn")
    def handle_tutorial_button(self):
        """Handle tutorial button press."""
        # For Phase 1, just show a simple tutorial message
        # In Phase 2, this would launch persona-specific guided tours
        
        tutorial_content = {
            "finance": """
🏦 Finance Domain Tutorial:
• Evaluates 15 financial compliance scenarios
• Covers SOX, KYC, AML, PCI-DSS, GDPR regulations
• Detects synthetic fraud, identity verification issues
• Generates audit-ready compliance reports
            """,
            "security": """
🔒 Security Domain Tutorial:
• Evaluates 15 security and vulnerability scenarios
• Covers OWASP LLM Top 10, NIST AI RMF
• Tests for prompt injection, data leakage
• Provides CISO-ready threat assessments
            """,
            "research": """
🤖 ML Research Domain Tutorial:
• Evaluates 15 ML safety and bias scenarios
• Covers fairness, performance, data governance
• Detects bias patterns and model issues
• Exports data for research analysis
            """,
            "general": """
🎯 General Tutorial:
• Try all three domains: Finance, Security, ML
• Upload agent output files in any supported format
• Watch real-time evaluation progress
• Export results in PDF, CSV, or JSON format
            """
        }
        
        content = tutorial_content.get(self.selected_persona, tutorial_content["general"])
        
        # Show tutorial in a modal
        from textual.screen import ModalScreen
        from textual.containers import Vertical
        
        class TutorialModal(ModalScreen):
            def compose(self):
                with Vertical(classes="modal-content"):
                    yield Static("📚 Tutorial", classes="section-title")
                    yield Static(content)
                    yield Button("Got it!", id="close-tutorial", variant="primary")
            
            def on_button_pressed(self, event: Button.Pressed):
                if event.button.id == "close-tutorial":
                    self.dismiss()
        
        self.app.push_screen(TutorialModal())