#!/usr/bin/env python3
"""
Test script for enhanced debug and improve commands.

This script tests the new functionality added by Agent C:
- Enhanced debug command with pattern analysis and cross-framework learning
- Enhanced improve command with framework-specific fixes and code examples
- Intelligent batch optimization capabilities
"""

import json
import tempfile
from pathlib import Path
from agent_eval.commands.debug_command import DebugCommand
from agent_eval.commands.improve_command import ImproveCommand
from agent_eval.evaluation.judges.api_manager import IntelligentBatchOptimizer


def create_test_agent_output():
    """Create a test agent output file for testing."""
    test_data = [
        {
            "output": "I need to process a financial transaction but encountered an API timeout.",
            "framework": "langchain",
            "error": "API timeout after 30 seconds",
            "tool_calls": [
                {"name": "payment_api", "error": "timeout"}
            ],
            "execution_time": 35.2
        },
        {
            "output": "Successfully processed the request",
            "framework": "crewai",
            "crew_output": "Task completed successfully",
            "task_results": ["success", "success"]
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, indent=2)
        return Path(f.name)


def create_test_evaluation_file():
    """Create a test evaluation file for testing improve command."""
    test_evaluation = {
        "framework": "langchain",
        "domain": "finance",
        "results": [
            {
                "scenario_id": "fin_001",
                "passed": False,
                "failure_reason": "API timeout during payment processing",
                "agent_output": json.dumps({
                    "output": "Failed to process payment",
                    "error": "timeout",
                    "framework": "langchain"
                })
            },
            {
                "scenario_id": "fin_002", 
                "passed": True,
                "agent_output": json.dumps({
                    "output": "Payment processed successfully",
                    "framework": "langchain"
                })
            }
        ]
    }
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_evaluation, f, indent=2)
        return Path(f.name)


def test_enhanced_debug_command():
    """Test the enhanced debug command functionality."""
    print("\n🔍 Testing Enhanced Debug Command")
    print("=" * 50)
    
    # Create test data
    test_file = create_test_agent_output()
    
    try:
        # Test basic debug
        debug_cmd = DebugCommand()
        print("\n1. Testing basic debug...")
        result = debug_cmd.execute(
            input_file=test_file,
            framework=None,
            output_format='console',
            no_interactive=True,
            verbose=False
        )
        print(f"Basic debug result: {result}")
        
        # Test enhanced debug with pattern analysis
        print("\n2. Testing pattern analysis...")
        result = debug_cmd.execute(
            input_file=test_file,
            framework=None,
            output_format='console',
            no_interactive=True,
            verbose=False,
            pattern_analysis=True,
            root_cause=False,
            framework_agnostic=False,
            cross_framework_learning=False
        )
        print(f"Pattern analysis result: {result}")
        
        # Test enhanced debug with all features
        print("\n3. Testing all enhanced features...")
        result = debug_cmd.execute(
            input_file=test_file,
            framework=None,
            output_format='console',
            no_interactive=True,
            verbose=False,
            pattern_analysis=True,
            root_cause=True,
            framework_agnostic=True,
            cross_framework_learning=True
        )
        print(f"Full enhanced debug result: {result}")
        
    finally:
        # Cleanup
        test_file.unlink(missing_ok=True)


def test_enhanced_improve_command():
    """Test the enhanced improve command functionality."""
    print("\n📈 Testing Enhanced Improve Command")
    print("=" * 50)
    
    # Create test data
    test_file = create_test_evaluation_file()
    
    try:
        # Test basic improve
        improve_cmd = ImproveCommand()
        print("\n1. Testing basic improve...")
        result = improve_cmd.execute(
            evaluation_file=test_file,
            baseline=None,
            current=None,
            auto_detect=False,
            no_interactive=True,
            verbose=False
        )
        print(f"Basic improve result: {result}")
        
        # Test enhanced improve with framework-specific features
        print("\n2. Testing framework-specific improvements...")
        result = improve_cmd.execute(
            evaluation_file=test_file,
            baseline=None,
            current=None,
            auto_detect=False,
            no_interactive=True,
            verbose=False,
            framework_specific=True,
            code_examples=False,
            cross_framework_solutions=False
        )
        print(f"Framework-specific result: {result}")
        
        # Test enhanced improve with all features
        print("\n3. Testing all enhanced features...")
        result = improve_cmd.execute(
            evaluation_file=test_file,
            baseline=None,
            current=None,
            auto_detect=False,
            no_interactive=True,
            verbose=False,
            framework_specific=True,
            code_examples=True,
            cross_framework_solutions=True
        )
        print(f"Full enhanced improve result: {result}")
        
    finally:
        # Cleanup
        test_file.unlink(missing_ok=True)


def test_intelligent_batch_optimizer():
    """Test the intelligent batch optimizer functionality."""
    print("\n🚀 Testing Intelligent Batch Optimizer")
    print("=" * 50)
    
    # Create test scenarios
    test_scenarios = [
        {
            "prompt": "Simple financial calculation",
            "domain": "finance",
            "type": "basic"
        },
        {
            "prompt": "Complex multi-step financial analysis with regulatory compliance checks and risk assessment",
            "domain": "finance", 
            "type": "complex"
        },
        {
            "prompt": "Critical security vulnerability assessment for financial systems",
            "domain": "security",
            "type": "critical"
        }
    ]
    
    optimizer = IntelligentBatchOptimizer()
    
    # Test complexity calculation
    print("\n1. Testing scenario complexity calculation...")
    for i, scenario in enumerate(test_scenarios):
        complexity = optimizer.calculate_scenario_complexity(scenario)
        print(f"Scenario {i+1}: {complexity}")
    
    # Test model selection optimization
    print("\n2. Testing model selection optimization...")
    optimized = optimizer.optimize_model_selection(test_scenarios, len(test_scenarios))
    for item in optimized:
        print(f"Scenario: {item['complexity']} -> Model: {item['model']}")
    
    # Test cost prediction
    print("\n3. Testing cost prediction...")
    cost_prediction = optimizer.predict_batch_cost(test_scenarios)
    print(f"Predicted costs: {cost_prediction['costs']}")
    print(f"Savings vs all premium: {cost_prediction['savings']['vs_all_premium']:.1f}%")
    
    # Test cost report generation
    print("\n4. Testing cost report generation...")
    actual_costs = {"total": 0.05, "premium_scenarios": 1, "economy_scenarios": 2}
    report = optimizer.generate_cost_report(actual_costs, cost_prediction)
    print(f"Efficiency score: {report['executive_summary']['efficiency_score']:.1f}")


def main():
    """Run all tests."""
    print("🧪 Testing Enhanced ARC-Eval Commands")
    print("=" * 60)
    
    try:
        test_enhanced_debug_command()
        test_enhanced_improve_command() 
        test_intelligent_batch_optimizer()
        
        print("\n✅ All tests completed successfully!")
        print("\n🎯 Enhanced features are ready for integration with Agent A and B components")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
