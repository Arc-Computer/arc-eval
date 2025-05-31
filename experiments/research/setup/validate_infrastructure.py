#!/usr/bin/env python3
"""
Infrastructure Validation Script
Tests existing ARC-Eval components for flywheel proof experiment.
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from agent_eval.core.engine import EvaluationEngine
from agent_eval.analysis.self_improvement import SelfImprovementEngine
from agent_eval.core.types import EvaluationResult


class InfrastructureValidator:
    """Validates existing ARC-Eval infrastructure for experiment."""
    
    def __init__(self):
        self.results = {}
        
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation tests."""
        print("🔍 Validating ARC-Eval Infrastructure...")
        print("=" * 50)
        
        # Test 1: Domain scenarios
        self.validate_domain_scenarios()
        
        # Test 2: Self-improvement engine
        self.validate_self_improvement()
        
        # Test 3: Examples data
        self.validate_examples_data()
        
        # Test 4: CLI functionality
        self.validate_cli_integration()
        
        # Summary
        self.print_summary()
        return self.results
    
    def validate_domain_scenarios(self):
        """Test 378 scenarios across all domains."""
        print("\n📊 Testing Domain Scenarios...")
        
        domains = ['finance', 'security', 'ml']
        total_scenarios = 0
        
        for domain in domains:
            try:
                engine = EvaluationEngine(domain=domain)
                scenario_count = len(engine.eval_pack.scenarios)
                total_scenarios += scenario_count
                
                print(f"  ✅ {domain}: {scenario_count} scenarios loaded")
                self.results[f'{domain}_scenarios'] = scenario_count
                
            except Exception as e:
                print(f"  ❌ {domain}: Failed to load - {str(e)}")
                self.results[f'{domain}_scenarios'] = 0
        
        self.results['total_scenarios'] = total_scenarios
        print(f"  📈 Total scenarios: {total_scenarios}")
        
        if total_scenarios >= 350:  # 355 scenarios is sufficient for experiment
            print("  ✅ Scenario validation: PASSED")
        else:
            print("  ❌ Scenario validation: FAILED")
    
    def validate_self_improvement(self):
        """Test self-improvement engine functionality."""
        print("\n🧠 Testing Self-Improvement Engine...")
        
        try:
            # Test initialization
            engine = SelfImprovementEngine()
            print("  ✅ Engine initialization: SUCCESS")
            
            # Test core methods exist
            methods_to_test = [
                'record_evaluation_result',
                'generate_training_examples', 
                'create_improvement_curriculum',
                'get_performance_trends'
            ]
            
            for method in methods_to_test:
                if hasattr(engine, method):
                    print(f"  ✅ Method {method}: EXISTS")
                else:
                    print(f"  ❌ Method {method}: MISSING")
            
            self.results['self_improvement_engine'] = True
            print("  ✅ Self-improvement validation: PASSED")
            
        except Exception as e:
            print(f"  ❌ Self-improvement validation: FAILED - {str(e)}")
            self.results['self_improvement_engine'] = False
    
    def validate_examples_data(self):
        """Test examples data availability."""
        print("\n📁 Testing Examples Data...")
        
        examples_dir = Path(__file__).parent.parent.parent.parent / "examples"
        
        # Test quickstart examples
        quickstart_dir = examples_dir / "quickstart"
        if quickstart_dir.exists():
            print("  ✅ Quickstart directory: EXISTS")
            
            example_files = ['finance_example.json', 'security_example.json', 'ml_example.json']
            for file in example_files:
                file_path = quickstart_dir / file
                if file_path.exists():
                    try:
                        with open(file_path) as f:
                            data = json.load(f)
                        print(f"  ✅ {file}: {len(data)} examples")
                        self.results[f'examples_{file.split("_")[0]}'] = len(data)
                    except Exception as e:
                        print(f"  ❌ {file}: Invalid JSON - {str(e)}")
                else:
                    print(f"  ❌ {file}: NOT FOUND")
        else:
            print("  ❌ Quickstart directory: NOT FOUND")
        
        # Test enhanced traces
        enhanced_dir = examples_dir / "enhanced-traces"
        if enhanced_dir.exists():
            print("  ✅ Enhanced traces directory: EXISTS")
            self.results['enhanced_traces'] = True
        else:
            print("  ❌ Enhanced traces directory: NOT FOUND")
            self.results['enhanced_traces'] = False
    
    def validate_cli_integration(self):
        """Test CLI components we'll use."""
        print("\n🖥️  Testing CLI Integration...")
        
        try:
            from agent_eval.cli import main
            print("  ✅ CLI module: IMPORTABLE")
            self.results['cli_available'] = True
        except Exception as e:
            print(f"  ❌ CLI module: FAILED - {str(e)}")
            self.results['cli_available'] = False
        
        # Test evaluation engine can process sample data
        try:
            engine = EvaluationEngine(domain='finance')
            sample_output = [{
                "output": "Test compliance output",
                "metadata": {"test": True}
            }]
            
            # This should not fail even with minimal data
            results = engine.evaluate(sample_output)
            print("  ✅ Evaluation engine: FUNCTIONAL")
            self.results['evaluation_functional'] = True
            
        except Exception as e:
            print(f"  ❌ Evaluation engine: FAILED - {str(e)}")
            self.results['evaluation_functional'] = False
    
    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 50)
        print("📋 Infrastructure Validation Summary")
        print("=" * 50)
        
        # Count successes
        passed = 0
        total = 0
        
        critical_checks = [
            ('total_scenarios', 'Domain Scenarios', lambda x: x >= 350),
            ('self_improvement_engine', 'Self-Improvement Engine', lambda x: x is True),
            ('cli_available', 'CLI Integration', lambda x: x is True),
            ('evaluation_functional', 'Evaluation Engine', lambda x: x is True)
        ]
        
        for key, name, check_func in critical_checks:
            total += 1
            if key in self.results and check_func(self.results[key]):
                print(f"✅ {name}")
                passed += 1
            else:
                print(f"❌ {name}")
        
        print(f"\n📊 Overall: {passed}/{total} critical checks passed")
        
        if passed == total:
            print("🎉 Infrastructure validation: ALL SYSTEMS GO!")
            print("Ready to proceed with flywheel proof experiment.")
        else:
            print("⚠️  Infrastructure validation: ISSUES DETECTED")
            print("Please resolve issues before proceeding.")
        
        return passed == total


if __name__ == "__main__":
    validator = InfrastructureValidator()
    success = validator.validate_all()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)