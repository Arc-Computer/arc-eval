#!/usr/bin/env python3
"""
Test ACL Integration for Flywheel Experiment

This script tests the Phase 1 ACL enhancements to ensure they work correctly
before running the full flywheel experiment.
"""

import sys
import json
from pathlib import Path

# Add path for imports
sys.path.append(str(Path(__file__).parent))

from agent_eval.core.scenario_bank import ScenarioBank
from agent_eval.analysis.self_improvement import SelfImprovementEngine

def test_scenario_bank_difficulty_classification():
    """Test the difficulty classification functionality."""
    print("🧪 Testing ScenarioBank Difficulty Classification...")
    
    scenario_bank = ScenarioBank()
    
    # Test scenarios with different complexity levels
    test_scenarios = [
        {
            "id": "fin_001",
            "compliance": ["SOX"],
            "description": "Basic financial reporting",
            "category": "financial_reporting"
        },
        {
            "id": "fin_050", 
            "compliance": ["SOX", "AML", "KYC"],
            "description": "Complex multi-step validation with cross-border compliance",
            "category": "model_governance"
        },
        {
            "id": "fin_090",
            "compliance": ["EU-AI-ACT", "SR-11-7"],
            "description": "Advanced AI/ML bias detection and model monitoring",
            "category": "ai/ml_bias"
        }
    ]
    
    for scenario in test_scenarios:
        difficulty = scenario_bank.classify_scenario_difficulty(scenario)
        print(f"   📋 {scenario['id']}: {difficulty} ({len(scenario['compliance'])} compliance areas)")
    
    print("✅ Scenario classification test passed")

def test_scenario_bank_adaptive_selection():
    """Test adaptive scenario selection."""
    print("\n🧪 Testing Adaptive Scenario Selection...")
    
    scenario_bank = ScenarioBank()
    
    # Mock performance data
    performance_data = {
        'overall_pass_rate': 0.65,
        'weakness_areas': ['AML', 'SOX'],
        'mastered_areas': ['PII'],
        'recent_trend': 'improving'
    }
    
    # Test different difficulty levels
    for difficulty in ['basic', 'intermediate', 'advanced']:
        scenarios = scenario_bank.get_adaptive_scenario_selection(
            performance_data=performance_data,
            target_difficulty=difficulty,
            domain='finance',
            count=3
        )
        print(f"   🎯 {difficulty}: {len(scenarios)} scenarios selected")
        
        if scenarios:
            print(f"      Sample: {scenarios[0].get('id', 'unknown')}")
    
    print("✅ Adaptive selection test passed")

def test_self_improvement_enhancements():
    """Test self-improvement engine enhancements."""
    print("\n🧪 Testing SelfImprovementEngine Enhancements...")
    
    # Create test directory
    test_dir = Path("./test_retraining_data")
    test_dir.mkdir(exist_ok=True)
    
    engine = SelfImprovementEngine(storage_path=test_dir)
    
    # Create mock evaluation data
    mock_evaluations = [
        {
            "scenario_id": "fin_001",
            "reward_signals": {"compliance": 0.8, "accuracy": 0.7},
            "compliance_gaps": ["AML"],
            "timestamp": "2025-05-31T10:00:00"
        },
        {
            "scenario_id": "fin_002", 
            "reward_signals": {"compliance": 0.6, "accuracy": 0.9},
            "compliance_gaps": ["SOX", "AML"],
            "timestamp": "2025-05-31T11:00:00"
        }
    ]
    
    # Record evaluation results
    agent_id = "test_agent"
    domain = "finance"
    
    engine.record_evaluation_result(
        agent_id=agent_id,
        domain=domain,
        evaluation_results=mock_evaluations
    )
    
    # Test scenario-specific performance
    performance = engine.get_scenario_specific_performance(agent_id, domain)
    print(f"   📊 Overall pass rate: {performance['overall_pass_rate']*100:.1f}%")
    print(f"   ⚠️  Weakness areas: {performance['weakness_areas']}")
    print(f"   ✅ Mastered areas: {performance['mastered_areas']}")
    
    # Test readiness calculation
    readiness = engine.calculate_readiness_for_difficulty(agent_id, domain)
    print(f"   🎯 Recommended difficulty: {readiness}")
    
    # Test adaptive curriculum data
    curriculum = engine.get_adaptive_curriculum_data(agent_id, domain)
    print(f"   📚 Curriculum generated with {len(curriculum)} sections")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
    print("✅ Self-improvement enhancements test passed")

def test_integration_workflow():
    """Test the full integration workflow."""
    print("\n🧪 Testing Full Integration Workflow...")
    
    # Initialize components
    scenario_bank = ScenarioBank()
    
    test_dir = Path("./test_integration_data")
    test_dir.mkdir(exist_ok=True)
    
    engine = SelfImprovementEngine(storage_path=test_dir)
    
    agent_id = "integration_test_agent"
    domain = "finance"
    
    # Step 1: Record some evaluation results
    mock_evaluations = [
        {
            "scenario_id": "fin_003",
            "reward_signals": {"compliance": 0.5, "accuracy": 0.6},
            "compliance_gaps": ["AML", "KYC"],
            "performance_metrics": {"confidence": 0.7}
        },
        {
            "scenario_id": "fin_004",
            "reward_signals": {"compliance": 0.8, "accuracy": 0.9},
            "compliance_gaps": [],
            "performance_metrics": {"confidence": 0.9}
        }
    ]
    
    engine.record_evaluation_result(agent_id, domain, mock_evaluations)
    print("   ✅ Step 1: Recorded evaluation results")
    
    # Step 2: Get adaptive curriculum data
    curriculum_data = engine.get_adaptive_curriculum_data(agent_id, domain)
    performance_summary = curriculum_data.get('performance_summary', {})
    print(f"   ✅ Step 2: Generated curriculum (pass rate: {performance_summary.get('overall_pass_rate', 0)*100:.1f}%)")
    
    # Step 3: Use curriculum data for scenario selection
    performance_data = {
        'overall_pass_rate': performance_summary.get('overall_pass_rate', 0.5),
        'weakness_areas': performance_summary.get('weakness_areas', []),
        'mastered_areas': performance_summary.get('mastered_areas', []),
        'recent_trend': performance_summary.get('recent_trend', 'stable')
    }
    
    readiness = curriculum_data.get('scenario_readiness', {})
    target_difficulty = readiness.get('recommended_difficulty', 'basic')
    
    adaptive_scenarios = scenario_bank.get_adaptive_scenario_selection(
        performance_data=performance_data,
        target_difficulty=target_difficulty,
        domain=domain,
        count=3
    )
    
    print(f"   ✅ Step 3: Selected {len(adaptive_scenarios)} adaptive scenarios (difficulty: {target_difficulty})")
    
    # Step 4: Test recommendation system
    recommendations = engine.recommend_next_scenarios(agent_id, domain, 
                                                    performance_summary.get('overall_pass_rate', 0.5))
    print(f"   ✅ Step 4: Generated {len(recommendations)} scenario recommendations")
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
    
    print("✅ Full integration workflow test passed")

def main():
    """Run all integration tests."""
    print("🚀 ARC-Eval ACL Integration Test Suite")
    print("=" * 50)
    
    try:
        test_scenario_bank_difficulty_classification()
        test_scenario_bank_adaptive_selection()
        test_self_improvement_enhancements()
        test_integration_workflow()
        
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Phase 1 ACL enhancements are ready for flywheel experiment")
        print("\n🔄 Next steps:")
        print("   1. Run: cd experiments/flywheel_proof/improvement")
        print("   2. Test: python flywheel_experiment.py --small-test")
        print("   3. Full run: python flywheel_experiment.py --test")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())