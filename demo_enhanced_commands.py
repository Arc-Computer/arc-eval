#!/usr/bin/env python3
"""
Demo script showing ARC-Eval's enhanced commands in action.

This demonstrates the competitive advantage of ARC-Eval's cross-framework intelligence
and actionable debugging capabilities.
"""

import json
import tempfile
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def create_demo_langchain_failure():
    """Create a realistic LangChain failure scenario."""
    return [
        {
            "output": "Failed to process financial transaction",
            "framework": "langchain", 
            "error": "API timeout after 30 seconds",
            "tool_calls": [
                {
                    "name": "payment_processor",
                    "parameters": {"amount": 1000, "account": "12345"},
                    "error": "timeout"
                }
            ],
            "intermediate_steps": [
                "Validating transaction parameters",
                "Calling payment API...",
                "Timeout occurred"
            ],
            "execution_time": 32.5,
            "agent_scratchpad": "Need to process payment but API is not responding"
        }
    ]


def create_demo_evaluation_results():
    """Create demo evaluation results for improve command."""
    return {
        "framework": "langchain",
        "domain": "finance", 
        "total_scenarios": 5,
        "passed": 2,
        "failed": 3,
        "results": [
            {
                "scenario_id": "fin_001",
                "scenario_name": "Payment Processing Timeout",
                "passed": False,
                "failure_reason": "API timeout during payment processing - no retry mechanism",
                "agent_output": json.dumps({
                    "output": "Failed to process payment",
                    "error": "timeout",
                    "framework": "langchain"
                }),
                "remediation": "Implement retry logic with exponential backoff"
            },
            {
                "scenario_id": "fin_002", 
                "scenario_name": "Invalid Transaction Format",
                "passed": False,
                "failure_reason": "Agent output malformed JSON",
                "agent_output": "Invalid JSON response",
                "remediation": "Add output validation and schema checking"
            },
            {
                "scenario_id": "fin_003",
                "scenario_name": "Successful Transaction",
                "passed": True,
                "agent_output": json.dumps({
                    "output": "Payment processed successfully",
                    "transaction_id": "tx_12345",
                    "framework": "langchain"
                })
            }
        ]
    }


def demo_enhanced_debug():
    """Demonstrate enhanced debug capabilities."""
    console.print(Panel.fit(
        "[bold blue]🔍 Enhanced Debug Command Demo[/bold blue]\n\n"
        "[yellow]Scenario:[/yellow] LangChain agent failing with API timeouts\n"
        "[yellow]Command:[/yellow] arc-eval debug --input agent_outputs.json --pattern-analysis --root-cause --cross-framework-learning",
        title="Demo 1: Universal Pattern Analysis"
    ))
    
    # Create demo file
    demo_data = create_demo_langchain_failure()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(demo_data, f, indent=2)
        demo_file = Path(f.name)
    
    try:
        # Import and run debug command
        from agent_eval.commands.debug_command import DebugCommand
        
        debug_cmd = DebugCommand()
        result = debug_cmd.execute(
            input_file=demo_file,
            framework=None,
            output_format='console',
            no_interactive=True,
            verbose=False,
            pattern_analysis=True,
            root_cause=True,
            framework_agnostic=True,
            cross_framework_learning=True
        )
        
        console.print(f"\n[green]✅ Debug completed with exit code: {result}[/green]")
        
    finally:
        demo_file.unlink(missing_ok=True)


def demo_enhanced_improve():
    """Demonstrate enhanced improve capabilities."""
    console.print(Panel.fit(
        "[bold green]📈 Enhanced Improve Command Demo[/bold green]\n\n"
        "[yellow]Scenario:[/yellow] Evaluation results showing LangChain failures\n"
        "[yellow]Command:[/yellow] arc-eval improve --from-evaluation results.json --framework-specific --code-examples --cross-framework-solutions",
        title="Demo 2: Framework-Specific Improvements"
    ))
    
    # Create demo evaluation file
    demo_data = create_demo_evaluation_results()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(demo_data, f, indent=2)
        demo_file = Path(f.name)
    
    try:
        # Import and run improve command
        from agent_eval.commands.improve_command import ImproveCommand
        
        improve_cmd = ImproveCommand()
        result = improve_cmd.execute(
            evaluation_file=demo_file,
            baseline=None,
            current=None,
            auto_detect=False,
            no_interactive=True,
            verbose=False,
            framework_specific=True,
            code_examples=True,
            cross_framework_solutions=True
        )
        
        console.print(f"\n[green]✅ Improve completed with exit code: {result}[/green]")
        
    finally:
        demo_file.unlink(missing_ok=True)


def demo_batch_optimizer():
    """Demonstrate intelligent batch optimization."""
    console.print(Panel.fit(
        "[bold cyan]🚀 Intelligent Batch Optimizer Demo[/bold cyan]\n\n"
        "[yellow]Scenario:[/yellow] Mixed complexity scenarios for cost optimization\n"
        "[yellow]Feature:[/yellow] Smart model selection and cost prediction",
        title="Demo 3: Cost Optimization"
    ))
    
    # Import batch optimizer
    from agent_eval.evaluation.judges.api_manager import IntelligentBatchOptimizer
    
    # Create mixed complexity scenarios
    scenarios = [
        {
            "prompt": "Simple calculation: What is 2+2?",
            "domain": "basic",
            "type": "simple"
        },
        {
            "prompt": "Complex financial analysis: Perform multi-step risk assessment with regulatory compliance checks for a $10M transaction involving international transfers, currency conversion, and AML screening.",
            "domain": "finance",
            "type": "complex"
        },
        {
            "prompt": "Critical security assessment: Analyze potential vulnerabilities in financial API endpoints and provide comprehensive security recommendations.",
            "domain": "security", 
            "type": "critical"
        }
    ]
    
    optimizer = IntelligentBatchOptimizer()
    
    # Show complexity analysis
    console.print("\n[bold]📊 Scenario Complexity Analysis:[/bold]")
    for i, scenario in enumerate(scenarios, 1):
        complexity = optimizer.calculate_scenario_complexity(scenario)
        console.print(f"  {i}. {complexity.upper()}: {scenario['prompt'][:50]}...")
    
    # Show model optimization
    console.print("\n[bold]🎯 Optimized Model Selection:[/bold]")
    optimized = optimizer.optimize_model_selection(scenarios, len(scenarios))
    for item in optimized:
        console.print(f"  • {item['complexity']} → {item['model']}")
    
    # Show cost prediction
    console.print("\n[bold]💰 Cost Prediction & Savings:[/bold]")
    cost_prediction = optimizer.predict_batch_cost(scenarios)
    
    console.print(f"  • All Premium Models: ${cost_prediction['costs']['all_premium']:.4f}")
    console.print(f"  • All Economy Models: ${cost_prediction['costs']['all_economy']:.4f}")
    console.print(f"  • Intelligent Optimization: ${cost_prediction['costs']['optimized']:.4f}")
    console.print(f"  • Savings vs Premium: {cost_prediction['savings']['vs_all_premium']:.1f}%")
    
    # Generate executive report
    actual_costs = {"total": cost_prediction['costs']['optimized'], "premium_scenarios": 2, "economy_scenarios": 1}
    report = optimizer.generate_cost_report(actual_costs, cost_prediction)
    
    console.print(f"\n[bold]📋 Executive Summary:[/bold]")
    console.print(f"  • Efficiency Score: {report['executive_summary']['efficiency_score']:.1f}/100")
    console.print(f"  • Cost Accuracy: {report['executive_summary']['cost_accuracy']}")


def main():
    """Run the complete demo."""
    console.print(Panel.fit(
        "[bold blue]🎯 ARC-Eval Enhanced Commands Demo[/bold blue]\n\n"
        "Demonstrating competitive advantages:\n"
        "• Universal pattern analysis across frameworks\n"
        "• Cross-framework learning and solutions\n" 
        "• Framework-specific code examples\n"
        "• Intelligent cost optimization\n\n"
        "[dim]This showcases why ARC-Eval is superior to framework-specific tools[/dim]",
        title="ARC-Eval Competitive Demo"
    ))
    
    try:
        demo_enhanced_debug()
        console.print("\n" + "="*60 + "\n")
        
        demo_enhanced_improve()
        console.print("\n" + "="*60 + "\n")
        
        demo_batch_optimizer()
        
        console.print(Panel.fit(
            "[bold green]🎉 Demo Complete![/bold green]\n\n"
            "[yellow]Key Differentiators Demonstrated:[/yellow]\n"
            "✅ Universal failure pattern detection\n"
            "✅ Cross-framework learning and solutions\n"
            "✅ Production-ready code examples\n"
            "✅ Intelligent cost optimization\n"
            "✅ Executive reporting and insights\n\n"
            "[bold]This is intelligence you can't get anywhere else![/bold]",
            title="Competitive Advantage Proven"
        ))
        
    except Exception as e:
        console.print(f"[red]❌ Demo failed: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
