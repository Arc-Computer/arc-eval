#!/usr/bin/env python3
"""
Parallel Agent-as-a-Judge comparison: Anthropic Claude Sonnet 4 vs OpenAI GPT-4.1
Run the same flywheel experiment with both judge models to compare performance.
"""

import asyncio
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Any, Tuple

class ParallelJudgeComparison:
    def __init__(self):
        self.anthropic_results = []
        self.openai_results = []
        self.experiment_dir = Path("parallel_judge_comparison")
        self.experiment_dir.mkdir(exist_ok=True)
        
    def run_experiment_with_judge(self, judge_type: str, max_iterations: int = 10) -> Dict[str, Any]:
        """Run flywheel experiment with specified judge type."""
        print(f"🚀 Starting {judge_type} experiment...")
        
        # Configure environment for judge type
        if judge_type == "anthropic":
            # Use existing ANTHROPIC_API_KEY
            judge_config = "--agent-judge"
        elif judge_type == "openai":
            # Would need OPENAI_API_KEY and modified CLI
            judge_config = "--agent-judge --judge-model gpt-4.1"
        
        try:
            cmd = [
                sys.executable, "flywheel_experiment.py",
                "--iterations", str(max_iterations),
                "--target", "85.0",
                "--budget", "50.0"
            ]
            
            start_time = time.time()
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 min timeout
            duration = time.time() - start_time
            
            return {
                "judge_type": judge_type,
                "success": result.returncode == 0,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": time.time()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "judge_type": judge_type,
                "success": False,
                "duration": 1800,
                "error": "Timeout after 30 minutes",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "judge_type": judge_type,
                "success": False,
                "duration": 0,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def run_parallel_comparison(self, max_iterations: int = 10) -> Dict[str, Any]:
        """Run both experiments in parallel and compare results."""
        print("🔬 Starting Parallel Agent-as-a-Judge Comparison")
        print(f"🎯 Max iterations: {max_iterations}")
        print("=" * 60)
        
        # Run both experiments in parallel
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(self.run_experiment_with_judge, "anthropic", max_iterations): "anthropic",
                # Note: OpenAI support would need to be implemented in CLI first
                # executor.submit(self.run_experiment_with_judge, "openai", max_iterations): "openai"
            }
            
            results = {}
            for future in as_completed(futures):
                judge_type = futures[future]
                try:
                    result = future.result()
                    results[judge_type] = result
                    print(f"✅ {judge_type} experiment completed in {result['duration']:.1f}s")
                except Exception as e:
                    print(f"❌ {judge_type} experiment failed: {e}")
                    results[judge_type] = {"success": False, "error": str(e)}
        
        # Save comparison results
        comparison_file = self.experiment_dir / "judge_comparison_results.json"
        with open(comparison_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        self.analyze_comparison(results)
        return results
    
    def analyze_comparison(self, results: Dict[str, Any]):
        """Analyze and display comparison results."""
        print("\n📊 AGENT-AS-A-JUDGE COMPARISON ANALYSIS")
        print("=" * 50)
        
        for judge_type, result in results.items():
            print(f"\n🤖 {judge_type.upper()} JUDGE:")
            if result["success"]:
                print(f"   ✅ Status: Success")
                print(f"   ⏱️  Duration: {result['duration']:.1f}s")
                # Extract metrics from stdout if available
                if "Final result:" in result["stdout"]:
                    # Parse final results
                    for line in result["stdout"].split('\n'):
                        if "Final result:" in line:
                            print(f"   🎯 {line.strip()}")
                        elif "Total cost:" in line:
                            print(f"   💰 {line.strip()}")
            else:
                print(f"   ❌ Status: Failed")
                print(f"   💥 Error: {result.get('error', 'Unknown error')}")

def main():
    """Main execution function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Parallel Agent-as-a-Judge Comparison Tool

Usage:
  python parallel_judge_comparison.py [max_iterations]

Arguments:
  max_iterations    Maximum iterations for each experiment (default: 10)

Example:
  python parallel_judge_comparison.py 15
        """)
        return
    
    max_iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    comparison = ParallelJudgeComparison()
    results = comparison.run_parallel_comparison(max_iterations)
    
    print(f"\n✅ Comparison completed. Results saved to:")
    print(f"   📁 {comparison.experiment_dir}/judge_comparison_results.json")

if __name__ == "__main__":
    main()