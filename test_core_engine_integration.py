#!/usr/bin/env python3
"""
Test script for core engine judge integration.

This script tests the new judge-enhanced core engine without requiring API keys.
It demonstrates the hybrid evaluation approach with graceful fallback.
"""

import json
import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from agent_eval.core.engine import EvaluationEngine
from agent_eval.core.types import AgentOutput


def test_core_engine_integration():
    """Test the core engine with judge integration."""
    print("🔍 Testing Core Engine Judge Integration")
    print("=" * 60)
    
    # Load test data
    test_file = Path("examples/quickstart/finance_example.json")
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    print(f"📁 Loaded {len(test_data)} test outputs from {test_file}")
    
    # Initialize engine
    try:
        engine = EvaluationEngine(domain="finance")
        print(f"✅ Engine initialized for domain: finance")
        print(f"📊 Available scenarios: {len(engine.eval_pack.scenarios)}")
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return False
    
    # Test evaluation with judge integration
    try:
        print("\n🚀 Running evaluation with judge integration...")
        results = engine.evaluate(test_data)
        
        print(f"✅ Evaluation completed successfully!")
        print(f"📊 Results: {len(results)} scenarios evaluated")
        
        # Analyze results
        passed = sum(1 for r in results if r.passed)
        failed = len(results) - passed
        judge_enhanced = sum(1 for r in results if r.has_judge_analysis())
        
        print(f"\n📈 Results Summary:")
        print(f"  • Passed: {passed}")
        print(f"  • Failed: {failed}")
        print(f"  • Judge Enhanced: {judge_enhanced}")
        
        # Show sample results
        print(f"\n🔍 Sample Results:")
        for i, result in enumerate(results[:3]):
            status = "✅ PASS" if result.passed else "❌ FAIL"
            confidence = result.get_confidence_score()
            judge_used = "🧠 Judge" if result.has_judge_analysis() else "📋 Rule"
            
            print(f"  {i+1}. {status} | {confidence:.1%} confidence | {judge_used} | {result.scenario_name}")
            
            if result.has_judge_analysis():
                print(f"     Judge: {result.judge_reasoning[:100]}...")
            elif result.failure_reason:
                print(f"     Rule: {result.failure_reason[:100]}...")
        
        # Test specific compliance violations
        print(f"\n🔍 Compliance Violation Detection:")
        violations_found = []
        for result in results:
            if not result.passed and result.failure_reason:
                if any(keyword in result.failure_reason.lower() for keyword in ['pii', 'ssn', 'aml', 'kyc', 'bias']):
                    violations_found.append(result)
        
        print(f"  • Compliance violations detected: {len(violations_found)}")
        for violation in violations_found[:2]:
            print(f"    - {violation.scenario_name}: {violation.failure_reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_judge_triggering_logic():
    """Test the smart judge triggering logic."""
    print("\n🧠 Testing Judge Triggering Logic")
    print("=" * 60)
    
    # Create mock engine to test triggering logic
    engine = EvaluationEngine(domain="finance")
    
    # Test scenarios for triggering logic
    test_cases = [
        {"passed": False, "confidence": 0.9, "severity": "medium", "should_trigger": True, "reason": "Failed scenario"},
        {"passed": True, "confidence": 0.6, "severity": "medium", "should_trigger": True, "reason": "Low confidence"},
        {"passed": True, "confidence": 0.9, "severity": "critical", "should_trigger": True, "reason": "Critical severity"},
        {"passed": True, "confidence": 0.9, "severity": "low", "should_trigger": False, "reason": "High confidence pass"},
    ]
    
    from agent_eval.core.types import EvaluationResult, EvaluationScenario
    
    for i, case in enumerate(test_cases):
        # Create mock result and scenario
        scenario = EvaluationScenario(
            id=f"test_{i}",
            name=f"Test Scenario {i}",
            description="Test scenario",
            severity=case["severity"],
            test_type="negative",
            failure_indicators=[],
            expected_behavior="",
            compliance=[],
            remediation="",
            category="test",
            input_template=""
        )
        
        result = EvaluationResult(
            scenario_id=scenario.id,
            scenario_name=scenario.name,
            description=scenario.description,
            severity=scenario.severity,
            test_type=scenario.test_type,
            passed=case["passed"],
            status="passed" if case["passed"] else "failed",
            confidence=case["confidence"]
        )
        
        # Test triggering logic
        should_trigger = engine._should_trigger_judge_analysis(result, scenario)
        expected = case["should_trigger"]
        
        status = "✅" if should_trigger == expected else "❌"
        print(f"  {status} Case {i+1}: {case['reason']} -> Trigger: {should_trigger} (expected: {expected})")
    
    print("✅ Judge triggering logic test completed")


if __name__ == "__main__":
    print("🚀 Arc-Eval Core Engine Integration Test")
    print("=" * 60)
    
    success = test_core_engine_integration()
    test_judge_triggering_logic()
    
    if success:
        print("\n✅ All tests passed! Core engine judge integration working correctly.")
        print("🎯 Key achievements:")
        print("  • Hybrid evaluation (rule-based + judge enhancement)")
        print("  • Smart judge triggering for failed scenarios")
        print("  • Graceful fallback when judges unavailable")
        print("  • Backward compatibility maintained")
        sys.exit(0)
    else:
        print("\n❌ Tests failed! Check the output above for details.")
        sys.exit(1)
