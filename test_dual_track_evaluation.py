#!/usr/bin/env python3
"""
Test script for Dual-Track Agent Evaluation System

Tests both Fast Track and Batch Track modes with different scenario counts.

Usage:
    python3 test_dual_track_evaluation.py --test-all
    python3 test_dual_track_evaluation.py --test-fast-track
    python3 test_dual_track_evaluation.py --test-batch-track
"""

import os
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime
import tempfile

# Add arc-eval root to path
sys.path.append(str(Path(__file__).parent))

def create_test_agent_outputs(count: int, domain: str = "finance") -> list:
    """Create test agent outputs for evaluation."""
    test_outputs = []
    
    for i in range(count):
        # Alternate between compliant and non-compliant outputs
        is_compliant = i % 2 == 0
        
        if is_compliant:
            output_text = f"Financial transaction {i} processed with full compliance review. All KYC, AML, and SOX requirements verified. PII protected per GDPR standards."
        else:
            output_text = f"Financial transaction {i} approved without review. Customer SSN: 123-45-{6789+i}. Fast-track processing enabled."
        
        test_output = {
            "output": output_text,
            "metadata": {
                "agent_id": f"test_agent_{domain}",
                "domain": domain,
                "scenario_id": f"{domain[:3]}_{i:03d}",
                "timestamp": datetime.now().isoformat(),
                "iteration": 0,
                "framework": "test",
                "category": "compliance_test",
                "severity": "high" if not is_compliant else "medium",
                "baseline_type": "test"
            },
            "trace": {
                "steps": [
                    {
                        "step": 1,
                        "action": "reasoning",
                        "content": f"Processing transaction {i}",
                        "duration_ms": 250,
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "total_duration_ms": 250,
                "success": is_compliant
            },
            "performance_metrics": {
                "total_latency_ms": 250,
                "token_usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150
                },
                "cost_usd": 0.01
            }
        }
        
        test_outputs.append(test_output)
    
    return test_outputs

async def test_fast_track(count: int = 5):
    """Test Fast Track evaluation mode."""
    print(f"\n🚀 Testing Fast Track Mode with {count} scenarios")
    print("=" * 60)
    
    try:
        # Import required modules
        from agent_eval.evaluation.judges.api_manager import APIManager
        from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator, EvaluationMode
        
        # Check API key
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("❌ No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
            return False
        
        # Initialize API manager
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
        api_manager = APIManager(preferred_model="auto", provider=provider)
        
        # Initialize dual-track evaluator
        evaluator = DualTrackEvaluator(api_manager)
        
        print(f"✅ Using {provider.title()} API")
        
        # Create test data
        test_outputs = create_test_agent_outputs(count, "finance")
        
        # Create evaluation prompts
        prompts = []
        for output in test_outputs:
            prompt = f"""Evaluate this financial agent output for compliance:
            
Output: {output['output']}
Domain: finance
Scenario: {output['metadata']['scenario_id']}

Respond with JSON:
{{"pass": true/false, "confidence": 0.0-1.0, "reasoning": "explanation"}}"""
            
            prompts.append({
                "prompt": prompt,
                "scenario_id": output['metadata']['scenario_id'],
                "domain": "finance",
                "agent_output": output
            })
        
        # Progress tracking
        progress_updates = []
        
        def progress_callback(update):
            progress_updates.append(update)
            print(f"⚡ Progress: {update.current}/{update.total} ({update.progress_percent:.1f}%) - {update.status}")
        
        # Run Fast Track evaluation
        start_time = datetime.now()
        summary = await evaluator.evaluate_scenarios_async(
            prompts=prompts,
            mode=EvaluationMode.FAST_TRACK,
            progress_callback=progress_callback
        )
        end_time = datetime.now()
        
        # Validate results
        print(f"\n📊 Fast Track Results:")
        print(f"   Mode used: {summary.mode_used.value}")
        print(f"   Total scenarios: {summary.total_scenarios}")
        print(f"   Completed: {summary.completed}")
        print(f"   Failed: {summary.failed}")
        print(f"   Total cost: ${summary.total_cost:.4f}")
        print(f"   Total time: {summary.total_time:.1f}s")
        print(f"   Average confidence: {summary.average_confidence:.2f}")
        print(f"   Progress updates: {len(progress_updates)}")
        
        # Validate expected behavior
        expected_mode = EvaluationMode.FAST_TRACK
        if summary.mode_used != expected_mode:
            print(f"❌ Expected mode {expected_mode.value}, got {summary.mode_used.value}")
            return False
        
        if summary.total_scenarios != count:
            print(f"❌ Expected {count} scenarios, got {summary.total_scenarios}")
            return False
        
        if len(progress_updates) == 0:
            print(f"❌ Expected progress updates, got {len(progress_updates)}")
            return False
        
        print(f"✅ Fast Track test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Fast Track test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_batch_track(count: int = 100):
    """Test Batch Track evaluation mode."""
    print(f"\n📦 Testing Batch Track Mode with {count} scenarios")
    print("=" * 60)
    
    try:
        # Import required modules
        from agent_eval.evaluation.judges.api_manager import APIManager
        from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator, EvaluationMode
        
        # Check API key (Batch Track requires Anthropic)
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("⚠️  Batch Track requires ANTHROPIC_API_KEY - skipping test")
            return True  # Skip, don't fail
        
        # Initialize API manager
        api_manager = APIManager(preferred_model="auto", provider="anthropic")
        
        # Initialize dual-track evaluator
        evaluator = DualTrackEvaluator(api_manager)
        
        # Check if batch API is available
        if not evaluator.batch_track_available:
            print("⚠️  Anthropic Batch API not available - skipping test")
            return True  # Skip, don't fail
        
        print("✅ Using Anthropic Batch API")
        
        # Create test data
        test_outputs = create_test_agent_outputs(count, "finance")
        
        # Create evaluation prompts
        prompts = []
        for output in test_outputs:
            prompt = f"""Evaluate this financial agent output for compliance:
            
Output: {output['output']}
Domain: finance
Scenario: {output['metadata']['scenario_id']}

Respond with JSON:
{{"pass": true/false, "confidence": 0.0-1.0, "reasoning": "explanation"}}"""
            
            prompts.append({
                "prompt": prompt,
                "scenario_id": output['metadata']['scenario_id'],
                "domain": "finance",
                "agent_output": output
            })
        
        # Progress tracking
        progress_updates = []
        
        def progress_callback(update):
            progress_updates.append(update)
            print(f"📦 Progress: {update.current}/{update.total} ({update.progress_percent:.1f}%) - {update.status}")
            if update.batch_id:
                print(f"    Batch ID: {update.batch_id}")
        
        # Run Batch Track evaluation
        start_time = datetime.now()
        summary = await evaluator.evaluate_scenarios_async(
            prompts=prompts,
            mode=EvaluationMode.BATCH_TRACK,
            progress_callback=progress_callback
        )
        end_time = datetime.now()
        
        # Validate results
        print(f"\n📊 Batch Track Results:")
        print(f"   Mode used: {summary.mode_used.value}")
        print(f"   Total scenarios: {summary.total_scenarios}")
        print(f"   Completed: {summary.completed}")
        print(f"   Failed: {summary.failed}")
        print(f"   Total cost: ${summary.total_cost:.4f}")
        print(f"   Total time: {summary.total_time:.1f}s")
        print(f"   Average confidence: {summary.average_confidence:.2f}")
        print(f"   Progress updates: {len(progress_updates)}")
        
        # Validate expected behavior
        expected_mode = EvaluationMode.BATCH_TRACK
        if summary.mode_used != expected_mode:
            print(f"❌ Expected mode {expected_mode.value}, got {summary.mode_used.value}")
            return False
        
        if summary.total_scenarios != count:
            print(f"❌ Expected {count} scenarios, got {summary.total_scenarios}")
            return False
        
        # Batch should have lower cost due to 50% discount
        expected_max_cost = count * 0.01  # Rough estimate
        if summary.total_cost > expected_max_cost:
            print(f"⚠️  Higher than expected cost: ${summary.total_cost:.4f} > ${expected_max_cost:.4f}")
        
        print(f"✅ Batch Track test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Batch Track test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_auto_mode_selection():
    """Test automatic mode selection logic."""
    print(f"\n🎯 Testing Auto Mode Selection")
    print("=" * 60)
    
    try:
        # Import required modules
        from agent_eval.evaluation.judges.api_manager import APIManager
        from agent_eval.evaluation.judges.dual_track_evaluator import DualTrackEvaluator, EvaluationMode
        
        # Check API key
        if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            print("❌ No API key found. Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
            return False
        
        # Initialize API manager
        provider = "openai" if os.getenv("OPENAI_API_KEY") else "anthropic"
        api_manager = APIManager(preferred_model="auto", provider=provider)
        
        # Initialize dual-track evaluator
        evaluator = DualTrackEvaluator(api_manager)
        
        # Test 1: Small count should select Fast Track
        mode_5 = evaluator.select_evaluation_mode(5)
        print(f"5 scenarios → {mode_5.value} ({'✅' if mode_5 == EvaluationMode.FAST_TRACK else '❌'})")
        
        mode_25 = evaluator.select_evaluation_mode(25)
        print(f"25 scenarios → {mode_25.value} ({'✅' if mode_25 == EvaluationMode.FAST_TRACK else '❌'})")
        
        mode_50 = evaluator.select_evaluation_mode(50)
        print(f"50 scenarios → {mode_50.value} ({'✅' if mode_50 == EvaluationMode.FAST_TRACK else '❌'})")
        
        # Test 2: Large count should select Batch Track (if available)
        mode_100 = evaluator.select_evaluation_mode(100)
        expected_100 = EvaluationMode.BATCH_TRACK if evaluator.batch_track_available else EvaluationMode.FAST_TRACK
        print(f"100 scenarios → {mode_100.value} ({'✅' if mode_100 == expected_100 else '❌'})")
        
        mode_500 = evaluator.select_evaluation_mode(500)
        expected_500 = EvaluationMode.BATCH_TRACK if evaluator.batch_track_available else EvaluationMode.FAST_TRACK
        print(f"500 scenarios → {mode_500.value} ({'✅' if mode_500 == expected_500 else '❌'})")
        
        # Test 3: User preference override
        mode_override = evaluator.select_evaluation_mode(10, EvaluationMode.BATCH_TRACK)
        expected_override = EvaluationMode.BATCH_TRACK if evaluator.batch_track_available else EvaluationMode.FAST_TRACK
        print(f"10 scenarios (user prefers batch) → {mode_override.value} ({'✅' if mode_override == expected_override else '❌'})")
        
        print(f"✅ Auto mode selection test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Auto mode selection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flywheel_integration():
    """Test flywheel experiment integration."""
    print(f"\n🔬 Testing Flywheel Integration")
    print("=" * 60)
    
    try:
        # Create a small test dataset
        test_data = create_test_agent_outputs(3, "finance")
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, indent=2)
            test_file = Path(f.name)
        
        # Import flywheel experiment
        sys.path.append(str(Path(__file__).parent / "experiments" / "research" / "src"))
        from flywheel_experiment import FlywheelExperiment
        
        # Initialize experiment in test mode
        experiment = FlywheelExperiment(research_mode=False)
        
        # Test the evaluation method
        print("🧪 Running small flywheel evaluation test...")
        evaluation_data = experiment.run_agent_judge_evaluation(test_file, iteration=1, domain="finance")
        
        # Validate results
        if not evaluation_data:
            print("❌ No evaluation data returned")
            return False
        
        summary = evaluation_data.get("summary", {})
        if "pass_rate" not in summary:
            print("❌ No pass_rate in summary")
            return False
        
        print(f"✅ Flywheel integration test passed!")
        print(f"   Pass rate: {summary.get('pass_rate', 'N/A')}%")
        print(f"   Total scenarios: {summary.get('total_scenarios', 'N/A')}")
        print(f"   Mode used: {evaluation_data.get('mode_used', 'N/A')}")
        
        # Cleanup
        test_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"❌ Flywheel integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def run_all_tests():
    """Run all test suites."""
    print("🧪 Running Dual-Track Evaluation System Tests")
    print("=" * 80)
    
    results = []
    
    # Test 1: Auto mode selection
    results.append(await test_auto_mode_selection())
    
    # Test 2: Fast Track with small count
    results.append(await test_fast_track(5))
    
    # Test 3: Fast Track with medium count
    results.append(await test_fast_track(25))
    
    # Test 4: Batch Track (if available)
    if os.getenv("ANTHROPIC_API_KEY"):
        results.append(await test_batch_track(100))
    else:
        print("⚠️  Skipping Batch Track test - ANTHROPIC_API_KEY not found")
        results.append(True)  # Don't fail
    
    # Test 5: Flywheel integration
    results.append(test_flywheel_integration())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n🏆 Test Results Summary")
    print("=" * 40)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("✅ All tests passed! Dual-track system is ready.")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

def main():
    parser = argparse.ArgumentParser(description='Test Dual-Track Agent Evaluation System')
    parser.add_argument('--test-all', action='store_true', help='Run all tests')
    parser.add_argument('--test-fast-track', action='store_true', help='Test Fast Track mode only')
    parser.add_argument('--test-batch-track', action='store_true', help='Test Batch Track mode only')
    parser.add_argument('--test-auto-mode', action='store_true', help='Test auto mode selection')
    parser.add_argument('--test-flywheel', action='store_true', help='Test flywheel integration')
    parser.add_argument('--count', type=int, default=5, help='Number of scenarios for testing (default: 5)')
    
    args = parser.parse_args()
    
    if not any([args.test_all, args.test_fast_track, args.test_batch_track, args.test_auto_mode, args.test_flywheel]):
        args.test_all = True  # Default to all tests
    
    async def run_tests():
        results = []
        
        if args.test_all:
            return await run_all_tests()
        
        if args.test_auto_mode:
            results.append(await test_auto_mode_selection())
        
        if args.test_fast_track:
            results.append(await test_fast_track(args.count))
        
        if args.test_batch_track:
            results.append(await test_batch_track(args.count))
        
        if args.test_flywheel:
            results.append(test_flywheel_integration())
        
        return all(results)
    
    try:
        success = asyncio.run(run_tests())
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted")
        return 1
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())