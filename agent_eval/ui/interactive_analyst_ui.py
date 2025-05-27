"""UI components for interactive analyst."""

from rich.panel import Panel
from rich.text import Text
from rich.console import Console


def create_question_examples_panel(domain: str) -> Panel:
    """Create domain-specific question examples panel."""
    
    domain_examples = {
        "finance": [
            "'Why did my KYC scenarios fail?'",
            "'How can I improve AML compliance?'",
            "'Show me PCI-DSS violation patterns'"
        ],
        "security": [
            "'Which prompt injection tests failed?'",
            "'How severe are my data leakage risks?'",
            "'What OWASP violations need immediate attention?'"
        ],
        "ml": [
            "'Why did my bias detection fail?'",
            "'How can I improve fairness scores?'",
            "'Show me demographic parity issues'"
        ]
    }
    
    examples = domain_examples.get(domain, [
        "'Why did scenario X fail?'",
        "'How can I improve my scores?'",
        "'What should I focus on first?'"
    ])
    
    example_text = Text()
    for example in examples:
        example_text.append(f"• {example}\n")
    
    return Panel(
        example_text,
        title=f"💡 {domain.title()} Question Ideas",
        border_style="dim"
    )


def create_analysis_response_panel(content: str, title: str = "Analysis") -> Panel:
    """Create a formatted panel for AI analysis responses."""
    return Panel(
        Text.from_markup(content),
        title=title,
        border_style="green",
        padding=(0, 1)
    )


def create_concise_recommendations_display(recommendations: list, max_items: int = 3) -> Text:
    """Create concise recommendations display with truncation."""
    text = Text()
    
    for i, rec in enumerate(recommendations[:max_items], 1):
        # Truncate to first sentence or 80 characters
        short_rec = rec.split('.')[0] if '.' in rec else rec[:80]
        truncated = len(rec) > len(short_rec)
        text.append(f"  {i}. {short_rec}{'...' if truncated else ''}\n")
    
    if len(recommendations) > max_items:
        text.append(f"  [dim]+ {len(recommendations) - max_items} more recommendations[/dim]\n")
    
    return text


def create_query_options_panel(domain: str, examples: list = None) -> Panel:
    """Create the query options panel with domain-specific examples."""
    
    if examples is None:
        domain_examples = {
            "ml": [
                "Why did the bias detection fail?",
                "How can I fix the algorithmic fairness issues?", 
                "What's blocking my IEEE Ethics compliance?"
            ],
            "finance": [
                "Why did my KYC scenarios fail?",
                "How can I improve AML compliance?",
                "What PCI-DSS violations need immediate attention?"
            ],
            "security": [
                "Which prompt injection tests failed?",
                "How severe are my data leakage risks?",
                "What OWASP violations are critical?"
            ]
        }
        
        examples = domain_examples.get(domain, [
            "Why did specific scenarios fail?",
            "What should I prioritize first?",
            "How can I improve my scores?"
        ])
    
    return Panel(
        Text.from_markup(
            "Examples:\n" + 
            "\n".join([f"  {example}" for example in examples[:3]]) +
            f"\n\n[dim]Or query anything about your {domain} evaluation[/dim]"
        ),
        title="Query options",
        border_style="blue",
        padding=(1, 2)
    )


def format_context_summary(improvement_report: dict, domain: str) -> str:
    """Format a brief context summary for display."""
    summary = improvement_report.get("summary", {})
    
    parts = [
        f"Domain: {domain.title()}",
        f"Scenarios: {summary.get('total_scenarios', 0)}",
        f"Pass Rate: {summary.get('pass_rate', 0):.1%}",
        f"Confidence: {summary.get('average_confidence', 0):.2f}"
    ]
    
    return " | ".join(parts)


def create_interactive_header() -> Text:
    """Create header text for interactive session."""
    header = Text()
    header.append("Query evaluation results:", style="bold cyan")
    return header


def create_exit_message() -> Text:
    """Create standardized exit message."""
    return Text("Analysis complete", style="dim")


def create_interrupt_message() -> Text:
    """Create standardized interrupt message."""
    return Text("Analysis interrupted", style="dim")