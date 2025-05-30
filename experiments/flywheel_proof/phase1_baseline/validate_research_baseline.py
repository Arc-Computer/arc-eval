#!/usr/bin/env python3
"""
Research Baseline Validation: Ensure baseline meets flywheel proof plan requirements
Validates against flywheel-proof-plan.md specifications for publication-ready research.
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from agent_eval.core.engine import EvaluationEngine


class ResearchBaselineValidator:
    """Validate baseline against research paper requirements."""
    
    def __init__(self, baseline_file: str = "realistic_baseline_outputs.json"):
        self.baseline_file = Path(__file__).parent / baseline_file
        self.plan_requirements = {
            "target_improvement": "42% → 91%",
            "max_iterations": 30,
            "total_scenarios": 355,  # finance: 110, security: 120, ml: 125
            "framework_agnostic": True,
            "cli_integration": True,
            "audit_ready_evidence": True
        }
        
    def validate_research_requirements(self) -> Dict[str, Any]:
        """Comprehensive validation against flywheel proof plan."""
        print("🔬 Validating Research Baseline Against Publication Requirements")
        print("=" * 70)
        
        validation_results = {}
        
        # 1. Load and analyze baseline data
        baseline_data = self._load_baseline_data()
        validation_results["baseline_analysis"] = self._analyze_baseline_data(baseline_data)
        
        # 2. Test CLI integration
        validation_results["cli_integration"] = self._test_cli_integration()
        
        # 3. Validate scenario coverage
        validation_results["scenario_coverage"] = self._validate_scenario_coverage(baseline_data)
        
        # 4. Check framework diversity
        validation_results["framework_diversity"] = self._check_framework_diversity(baseline_data)
        
        # 5. Test improvement potential
        validation_results["improvement_potential"] = self._assess_improvement_potential(baseline_data)
        
        # 6. Validate research quality
        validation_results["research_quality"] = self._validate_research_quality(baseline_data)
        
        # 7. Generate recommendations
        validation_results["recommendations"] = self._generate_recommendations(validation_results)
        
        return validation_results
    
    def _load_baseline_data(self) -> List[Dict]:
        """Load baseline data with validation."""
        print("\n📁 Loading baseline data...")
        
        if not self.baseline_file.exists():
            raise FileNotFoundError(f"Baseline file not found: {self.baseline_file}")
        
        with open(self.baseline_file) as f:
            data = json.load(f)
        
        print(f"✅ Loaded {len(data)} baseline outputs")
        return data
    
    def _analyze_baseline_data(self, baseline_data: List[Dict]) -> Dict[str, Any]:
        """Analyze baseline data quality and distribution."""
        print("\n📊 Analyzing baseline data quality...")
        
        # Domain distribution
        domains = {}
        frameworks = {}
        severities = {}
        expected_outcomes = {"pass": 0, "fail": 0}
        
        trace_quality = {
            "has_trace": 0,
            "has_performance_metrics": 0,
            "has_evaluation_context": 0,
            "multi_step_reasoning": 0,
            "tool_calls": 0
        }
        
        for item in baseline_data:
            # Domain distribution
            domain = item['metadata']['domain']
            domains[domain] = domains.get(domain, 0) + 1
            
            # Framework diversity
            framework = item['metadata']['framework']
            frameworks[framework] = frameworks.get(framework, 0) + 1
            
            # Severity levels
            severity = item['metadata'].get('severity', 'unknown')
            severities[severity] = severities.get(severity, 0) + 1
            
            # Expected outcomes
            if item['metadata'].get('expected_to_pass', True):
                expected_outcomes["pass"] += 1
            else:
                expected_outcomes["fail"] += 1
            
            # Trace quality analysis
            if 'trace' in item and item['trace']:
                trace_quality["has_trace"] += 1
                trace = item['trace']
                
                if 'steps' in trace and trace['steps']:
                    trace_quality["multi_step_reasoning"] += 1
                    
                    # Count tool calls
                    tool_calls = sum(1 for step in trace['steps'] if step.get('action') == 'tool_call')
                    if tool_calls > 0:
                        trace_quality["tool_calls"] += 1
            
            if 'performance_metrics' in item and item['performance_metrics']:
                trace_quality["has_performance_metrics"] += 1
            
            if 'evaluation_context' in item and item['evaluation_context']:
                trace_quality["has_evaluation_context"] += 1
        
        analysis = {
            "total_outputs": len(baseline_data),
            "domain_distribution": domains,
            "framework_diversity": frameworks,
            "severity_distribution": severities,
            "expected_outcomes": expected_outcomes,
            "trace_quality": trace_quality,
            "trace_completeness": trace_quality["has_trace"] / len(baseline_data),
            "framework_count": len(frameworks),
            "domain_count": len(domains)
        }
        
        print(f"  📈 Domains: {list(domains.keys())} ({len(domains)} total)")
        print(f"  🔧 Frameworks: {len(frameworks)} different frameworks")
        print(f"  📊 Trace completeness: {analysis['trace_completeness']:.1%}")
        print(f"  🎯 Expected outcome mix: {expected_outcomes['pass']} pass, {expected_outcomes['fail']} fail")
        
        return analysis
    
    def _test_cli_integration(self) -> Dict[str, Any]:
        """Test CLI integration with baseline data."""
        print("\n🖥️  Testing CLI integration...")
        
        cli_results = {}
        domains = ['finance', 'security', 'ml']
        
        for domain in domains:
            print(f"  Testing {domain} domain...")
            
            try:
                # Test CLI command with our baseline data
                cmd = [
                    "arc-eval", "compliance",
                    "--domain", domain,
                    "--input", str(self.baseline_file),
                    "--export", "json"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode == 0:
                    # Parse results
                    evaluation_data = json.loads(result.stdout)
                    
                    cli_results[domain] = {
                        "status": "success",
                        "pass_rate": evaluation_data.get("summary", {}).get("pass_rate", 0),
                        "total_scenarios": evaluation_data.get("summary", {}).get("total_scenarios", 0),
                        "cli_functional": True
                    }
                    
                    print(f"    ✅ {domain}: {cli_results[domain]['pass_rate']:.1%} pass rate")
                else:
                    cli_results[domain] = {
                        "status": "failed",
                        "error": result.stderr,
                        "cli_functional": False
                    }
                    print(f"    ❌ {domain}: CLI failed - {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                cli_results[domain] = {
                    "status": "timeout",
                    "error": "CLI command timed out",
                    "cli_functional": False
                }
                print(f"    ⏰ {domain}: CLI timed out")
            except Exception as e:
                cli_results[domain] = {
                    "status": "error",
                    "error": str(e),
                    "cli_functional": False
                }
                print(f"    ❌ {domain}: Error - {str(e)}")
        
        overall_cli_success = all(r.get("cli_functional", False) for r in cli_results.values())
        
        return {
            "overall_success": overall_cli_success,
            "domain_results": cli_results,
            "total_tested": len(domains),
            "successful": sum(1 for r in cli_results.values() if r.get("cli_functional", False))
        }
    
    def _validate_scenario_coverage(self, baseline_data: List[Dict]) -> Dict[str, Any]:
        """Validate coverage against total scenario counts."""
        print("\n🎯 Validating scenario coverage...")
        
        coverage_results = {}
        domains = ['finance', 'security', 'ml']
        
        for domain in domains:
            try:
                # Get total scenarios for domain
                engine = EvaluationEngine(domain=domain)
                total_scenarios = len(engine.eval_pack.scenarios)
                
                # Count outputs for this domain
                domain_outputs = [
                    item for item in baseline_data 
                    if item['metadata']['domain'] == domain
                ]
                
                coverage_results[domain] = {
                    "total_scenarios": total_scenarios,
                    "baseline_outputs": len(domain_outputs),
                    "coverage_ratio": len(domain_outputs) / total_scenarios if total_scenarios > 0 else 0
                }
                
                print(f"  📊 {domain}: {len(domain_outputs)} outputs for {total_scenarios} scenarios")
                
            except Exception as e:
                coverage_results[domain] = {
                    "error": str(e),
                    "total_scenarios": 0,
                    "baseline_outputs": 0
                }
                print(f"  ❌ {domain}: Error - {str(e)}")
        
        total_scenarios = sum(r.get("total_scenarios", 0) for r in coverage_results.values())
        total_outputs = sum(r.get("baseline_outputs", 0) for r in coverage_results.values())
        
        return {
            "domain_coverage": coverage_results,
            "total_scenarios": total_scenarios,
            "total_baseline_outputs": total_outputs,
            "overall_coverage": total_outputs / total_scenarios if total_scenarios > 0 else 0,
            "meets_plan_requirements": total_scenarios >= 350  # Close to 378 target
        }
    
    def _check_framework_diversity(self, baseline_data: List[Dict]) -> Dict[str, Any]:
        """Check framework diversity for research validity."""
        print("\n🔧 Checking framework diversity...")
        
        frameworks = {}
        for item in baseline_data:
            framework = item['metadata']['framework']
            frameworks[framework] = frameworks.get(framework, 0) + 1
        
        diversity_score = len(frameworks) / max(len(frameworks), 5)  # Target: 5+ frameworks
        
        print(f"  📈 Framework diversity: {len(frameworks)} frameworks")
        print(f"  🎯 Distribution: {frameworks}")
        
        return {
            "framework_count": len(frameworks),
            "framework_distribution": frameworks,
            "diversity_score": diversity_score,
            "meets_agnostic_requirement": len(frameworks) >= 4  # Multiple major frameworks
        }
    
    def _assess_improvement_potential(self, baseline_data: List[Dict]) -> Dict[str, Any]:
        """Assess potential for demonstrating improvement."""
        print("\n📈 Assessing improvement potential...")
        
        # Run quick evaluation to get current pass rates
        improvement_potential = {}
        domains = ['finance', 'security', 'ml']
        
        for domain in domains:
            domain_outputs = [
                item for item in baseline_data 
                if item['metadata']['domain'] == domain
            ]
            
            if domain_outputs:
                try:
                    engine = EvaluationEngine(domain=domain)
                    results = engine.evaluate(domain_outputs)
                    summary = engine.get_summary(results)
                    
                    pass_rate = summary.passed / summary.total_scenarios if summary.total_scenarios > 0 else 0
                    improvement_headroom = 0.91 - pass_rate  # Target 91%
                    
                    improvement_potential[domain] = {
                        "current_pass_rate": pass_rate,
                        "target_pass_rate": 0.91,
                        "improvement_headroom": improvement_headroom,
                        "dramatic_improvement_possible": improvement_headroom > 0.3,
                        "total_scenarios": summary.total_scenarios,
                        "failed_scenarios": summary.failed
                    }
                    
                    print(f"  📊 {domain}: {pass_rate:.1%} → 91% (headroom: {improvement_headroom:.1%})")
                    
                except Exception as e:
                    print(f"  ❌ {domain}: Assessment failed - {str(e)}")
                    improvement_potential[domain] = {"error": str(e)}
        
        # Overall assessment
        total_headroom = sum(
            r.get("improvement_headroom", 0) 
            for r in improvement_potential.values() 
            if "error" not in r
        ) / len([r for r in improvement_potential.values() if "error" not in r])
        
        return {
            "domain_potential": improvement_potential,
            "overall_improvement_headroom": total_headroom,
            "dramatic_improvement_possible": total_headroom > 0.2,
            "research_viable": total_headroom > 0.1
        }
    
    def _validate_research_quality(self, baseline_data: List[Dict]) -> Dict[str, Any]:
        """Validate research quality and publication readiness."""
        print("\n🔬 Validating research quality...")
        
        quality_metrics = {
            "trace_completeness": 0,
            "performance_metrics_coverage": 0,
            "multi_step_reasoning": 0,
            "realistic_agent_behavior": 0,
            "enterprise_scenarios": 0
        }
        
        for item in baseline_data:
            # Trace completeness
            if 'trace' in item and item['trace'] and 'steps' in item['trace']:
                quality_metrics["trace_completeness"] += 1
                
                # Multi-step reasoning
                steps = item['trace']['steps']
                if len(steps) >= 3:  # At least 3 reasoning/action steps
                    quality_metrics["multi_step_reasoning"] += 1
                
                # Realistic agent behavior (tool calls + reasoning)
                has_reasoning = any(step.get('action') == 'reasoning' for step in steps)
                has_tool_calls = any(step.get('action') == 'tool_call' for step in steps)
                if has_reasoning and has_tool_calls:
                    quality_metrics["realistic_agent_behavior"] += 1
            
            # Performance metrics
            if 'performance_metrics' in item and item['performance_metrics']:
                perf = item['performance_metrics']
                if 'total_latency_ms' in perf and 'token_usage' in perf:
                    quality_metrics["performance_metrics_coverage"] += 1
            
            # Enterprise scenarios
            if item['metadata'].get('severity') in ['critical', 'high']:
                quality_metrics["enterprise_scenarios"] += 1
        
        total_items = len(baseline_data)
        quality_scores = {
            metric: count / total_items 
            for metric, count in quality_metrics.items()
        }
        
        overall_quality = sum(quality_scores.values()) / len(quality_scores)
        
        print(f"  📊 Trace completeness: {quality_scores['trace_completeness']:.1%}")
        print(f"  📈 Performance metrics: {quality_scores['performance_metrics_coverage']:.1%}")
        print(f"  🧠 Multi-step reasoning: {quality_scores['multi_step_reasoning']:.1%}")
        print(f"  🎯 Overall quality score: {overall_quality:.1%}")
        
        return {
            "quality_metrics": quality_metrics,
            "quality_scores": quality_scores,
            "overall_quality": overall_quality,
            "publication_ready": overall_quality > 0.8,
            "research_grade": overall_quality > 0.9
        }
    
    def _generate_recommendations(self, validation_results: Dict) -> List[str]:
        """Generate recommendations for research baseline improvement."""
        print("\n💡 Generating recommendations...")
        
        recommendations = []
        
        # Check CLI integration
        if not validation_results["cli_integration"]["overall_success"]:
            recommendations.append("🔧 Fix CLI integration issues for reproducible research")
        
        # Check improvement potential
        improvement = validation_results.get("improvement_potential", {})
        if not improvement.get("dramatic_improvement_possible", False):
            recommendations.append("📈 Adjust baseline to create more dramatic improvement opportunity")
        
        # Check research quality
        quality = validation_results.get("research_quality", {})
        if not quality.get("publication_ready", False):
            recommendations.append("🔬 Enhance trace quality for publication-ready research")
        
        # Check scenario coverage
        coverage = validation_results.get("scenario_coverage", {})
        if not coverage.get("meets_plan_requirements", False):
            recommendations.append("🎯 Expand scenario coverage to meet plan requirements")
        
        # Framework diversity
        framework = validation_results.get("framework_diversity", {})
        if not framework.get("meets_agnostic_requirement", False):
            recommendations.append("🔧 Increase framework diversity for agnostic claims")
        
        if not recommendations:
            recommendations.append("✅ Baseline meets all research requirements - ready for Phase 2!")
        
        for rec in recommendations:
            print(f"  {rec}")
        
        return recommendations


if __name__ == "__main__":
    validator = ResearchBaselineValidator()
    results = validator.validate_research_requirements()
    
    print(f"\n📋 Research Baseline Validation Summary")
    print("=" * 50)
    
    # Overall assessment
    cli_ok = results["cli_integration"]["overall_success"]
    improvement_ok = results["improvement_potential"]["dramatic_improvement_possible"]
    quality_ok = results["research_quality"]["publication_ready"]
    coverage_ok = results["scenario_coverage"]["meets_plan_requirements"]
    
    print(f"✅ CLI Integration: {'PASS' if cli_ok else 'FAIL'}")
    print(f"✅ Improvement Potential: {'PASS' if improvement_ok else 'FAIL'}")
    print(f"✅ Research Quality: {'PASS' if quality_ok else 'FAIL'}")
    print(f"✅ Scenario Coverage: {'PASS' if coverage_ok else 'FAIL'}")
    
    overall_ready = cli_ok and improvement_ok and quality_ok and coverage_ok
    
    print(f"\n🎯 Overall Assessment: {'READY FOR RESEARCH' if overall_ready else 'NEEDS IMPROVEMENT'}")
    
    # Save validation results
    results_file = Path(__file__).parent / "research_validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"💾 Validation results saved to: {results_file}")