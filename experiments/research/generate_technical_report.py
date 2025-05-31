#!/usr/bin/env python3
"""
ARC-Eval Flywheel Research: Complete Technical Report Generation

This script generates the complete technical report with charts, metrics, and 
publication-ready analysis from experiment data.

Usage:
    python3 generate_technical_report.py

This will:
1. Check for experiment data
2. Generate all charts and visualizations  
3. Calculate summary metrics
4. Create complete technical report in Markdown and HTML
5. Package everything for publication

Authors: ARC-Eval Research Team
Date: May 2025
"""

import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def main():
    """Generate complete technical report from experiment data."""
    print("🎯 ARC-Eval Flywheel Research: Technical Report Generation")
    print("=" * 60)
    
    # Check for experiment data
    experiment_dir = Path("experiment_outputs")
    results_log = experiment_dir / "experiment_log.jsonl"
    
    if not results_log.exists():
        print("❌ No experiment data found!")
        print(f"   Expected: {results_log}")
        print(f"\n🚀 Run the experiment first:")
        print(f"   python3 run_experiment.py")
        print(f"   # OR")
        print(f"   cd src && python3 flywheel_experiment.py")
        return 1
    
    try:
        # Step 1: Generate metrics and charts
        print("\n📊 Step 1: Generating metrics and visualizations...")
        from metrics_collector import FlywheelMetricsCollector
        
        collector = FlywheelMetricsCollector(experiment_dir)
        technical_data, success = collector.generate_technical_report_data()
        
        if not success:
            print("❌ Failed to generate metrics and charts")
            return 1
        
        # Step 2: Generate technical report
        print("\n📄 Step 2: Generating technical report...")
        from report_generator import TechnicalReportGenerator
        
        generator = TechnicalReportGenerator(experiment_dir)
        report = generator.generate_complete_report()
        
        if not report:
            print("❌ Failed to generate technical report")
            return 1
        
        # Step 3: Summary and next steps
        print("\n🎉 Technical Report Generation Complete!")
        print("=" * 60)
        
        # Show key results
        if technical_data and "results_summary" in technical_data:
            exp = technical_data["results_summary"]["experiment_summary"]
            time_eff = technical_data["results_summary"]["time_efficiency"]
            cost = technical_data["results_summary"]["cost_analysis"]
            
            print(f"\n📈 Key Research Findings:")
            print(f"   🎯 Performance: {exp['initial_pass_rate']}% → {exp['final_pass_rate']}% (+{exp['improvement_percentage_points']} points)")
            print(f"   🚀 Iterations: {exp['total_iterations']} (target: ≤30)")
            print(f"   ⚡ Speed: {time_eff['time_savings_factor']}x faster than traditional")
            print(f"   💰 Savings: ${cost['total_cost_savings']:,.0f}")
            print(f"   🎯 Target: {'✅ Achieved' if exp['target_achieved'] else '❌ Not Reached'}")
        
        print(f"\n📁 Generated Files:")
        print(f"   📄 Report: technical_report/technical_report.md")
        print(f"   🌐 HTML: technical_report/technical_report.html")
        print(f"   📊 Charts: technical_report/charts/")
        print(f"   📋 Metrics: technical_report/metrics.json")
        print(f"   📖 Appendix: technical_report/technical_appendix.json")
        
        print(f"\n🎯 Next Steps:")
        print(f"   📖 Review: Open technical_report/technical_report.html in browser")
        print(f"   📊 Charts: Check technical_report/charts/ for all visualizations")
        print(f"   📝 Publish: All files ready for academic/industry publication")
        print(f"   🔍 Validate: Use metrics.json for external validation")
        
        return 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print(f"\n💡 Install required packages:")
        print(f"   pip install matplotlib seaborn pandas numpy")
        print(f"   pip install markdown  # Optional, for HTML generation")
        return 1
        
    except Exception as e:
        print(f"❌ Error generating technical report: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())