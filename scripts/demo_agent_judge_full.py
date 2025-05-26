#!/usr/bin/env python3
"""
Agent-as-a-Judge Full Coverage Demo Script
Demonstrates AI-powered evaluation across all 337 scenarios with cost tracking.
"""

import subprocess
import time
import json
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "examples" / "agent-outputs"
DOMAINS = ['finance', 'security', 'ml']

def run_agent_judge_evaluation(domain, input_file):
    """Run Agent-as-a-Judge evaluation for a domain."""
    print(f"\n🔍 Running Agent-as-a-Judge evaluation for {domain.upper()} domain...")
    print(f"📁 Input file: {input_file.name}")
    
    # Count scenarios in input file
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
        scenario_count = len(data)
        print(f"📊 Scenarios to evaluate: {scenario_count}")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")
        return False
    
    # Run evaluation
    cmd = [
        'arc-eval',
        '--domain', domain,
        '--input', str(input_file),
        '--agent-judge'
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR)
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"⏱️  Evaluation completed in {duration:.1f} seconds")
        
        if result.returncode == 0:
            print(f"✅ {domain.upper()} evaluation successful!")
            print("📈 Results summary:")
            # Extract key metrics from output
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line.lower() for keyword in ['critical', 'high', 'medium', 'low', 'passes', 'failures', 'cost']):
                    print(f"   {line}")
        else:
            print(f"❌ {domain.upper()} evaluation failed!")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error running evaluation: {e}")
        return False
    
    return True

def main():
    """Run comprehensive Agent-as-a-Judge demo across all domains."""
    print("🎯 Agent-as-a-Judge Full Coverage Demo")
    print("=" * 50)
    print("Evaluating AI agent outputs across all 337 scenarios")
    print("with real-time AI feedback and cost tracking.")
    print()
    
    total_start = time.time()
    successful_domains = 0
    total_scenarios = 0
    
    for domain in DOMAINS:
        input_file = OUTPUTS_DIR / f"complete_{domain}_outputs.json"
        
        if not input_file.exists():
            print(f"❌ Input file not found: {input_file}")
            continue
        
        # Count scenarios
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            domain_scenarios = len(data)
            total_scenarios += domain_scenarios
        except:
            domain_scenarios = 0
        
        success = run_agent_judge_evaluation(domain, input_file)
        if success:
            successful_domains += 1
        
        # Small delay between domains
        time.sleep(1)
    
    total_end = time.time()
    total_duration = total_end - total_start
    
    print("\n" + "=" * 50)
    print("🎉 Demo Complete!")
    print(f"⏱️  Total time: {total_duration:.1f} seconds")
    print(f"📊 Total scenarios evaluated: {total_scenarios}")
    print(f"✅ Successful domains: {successful_domains}/{len(DOMAINS)}")
    
    if successful_domains == len(DOMAINS):
        print("\n🚀 All evaluations successful!")
        print("💡 Key Benefits Demonstrated:")
        print("   • AI-powered scenario evaluation with contextual feedback")
        print("   • Real-time cost tracking and transparent pricing")
        print("   • Enterprise-ready compliance reporting")
        print("   • Comprehensive coverage across finance, security, and ML domains")
        print("   • Actionable recommendations for each failure")
    else:
        print(f"\n⚠️  Some evaluations failed. Check configuration and try again.")
    
    print(f"\n📁 Generated reports available in current directory")
    print(f"🔗 For CI/CD integration, see: examples/ci-templates/")

if __name__ == "__main__":
    main()