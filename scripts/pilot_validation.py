#!/usr/bin/env python3
"""
ARC-Eval Pilot Validation Script

Based on Core_loop.md validation requirements (lines 172-188).
Automates pilot session tracking and success criteria measurement.
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import argparse

@dataclass
class PilotSession:
    """Track pilot session data and metrics."""
    
    customer_name: str
    domain: str
    session_date: str
    baseline_evaluation_file: str
    improvement_plan_file: Optional[str] = None
    comparison_evaluation_file: Optional[str] = None
    
    # Technical validation
    workflow_completed: bool = False
    execution_time_minutes: float = 0.0
    technical_errors: List[str] = None
    
    # Usage validation  
    weekly_usage_intent: bool = False
    implementation_percentage: int = 0  # Percentage of recommendations they'd implement
    improvement_value_recognized: bool = False
    payment_willingness: bool = False
    
    # Feedback
    actionable_recommendations_pct: int = 0  # Percentage rated as actionable
    timeline_realistic: bool = False
    missing_functionality: List[str] = None
    integration_needs: List[str] = None
    
    def __post_init__(self):
        if self.technical_errors is None:
            self.technical_errors = []
        if self.missing_functionality is None:
            self.missing_functionality = []
        if self.integration_needs is None:
            self.integration_needs = []


class PilotValidator:
    """Automate pilot validation and success criteria tracking."""
    
    def __init__(self, output_dir: str = "pilot_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Success criteria thresholds from Core_loop.md
        self.success_thresholds = {
            "weekly_usage_intent": 0.75,  # ≥75% of pilots show weekly usage intent
            "implementation_rate": 0.50,  # ≥50% of improvement plans implemented
            "improvement_measurement": 0.30,  # ≥30% violation reduction
            "payment_intent": 0.60,  # ≥60% indicate payment willingness
        }
    
    def run_baseline_evaluation(self, domain: str, input_file: str, customer_name: str) -> PilotSession:
        """Execute baseline evaluation and start pilot session tracking."""
        
        print(f"🔄 Starting pilot validation for {customer_name} ({domain} domain)")
        start_time = time.time()
        
        session = PilotSession(
            customer_name=customer_name,
            domain=domain,
            session_date=datetime.now().isoformat(),
            baseline_evaluation_file=""
        )
        
        try:
            # Run baseline evaluation
            cmd = [
                "arc-eval", 
                "--domain", domain,
                "--input", input_file,
                "--agent-judge",
                "--dev"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                session.technical_errors.append(f"Baseline evaluation failed: {result.stderr}")
                return session
            
            # Find generated evaluation file
            evaluation_files = list(Path(".").glob(f"{domain}_evaluation_*.json"))
            if evaluation_files:
                session.baseline_evaluation_file = str(evaluation_files[-1])  # Most recent
                print(f"✅ Baseline evaluation saved: {session.baseline_evaluation_file}")
            else:
                session.technical_errors.append("No evaluation file generated")
                
        except subprocess.TimeoutExpired:
            session.technical_errors.append("Baseline evaluation timeout (>5 minutes)")
        except Exception as e:
            session.technical_errors.append(f"Baseline evaluation error: {str(e)}")
        
        session.execution_time_minutes = (time.time() - start_time) / 60
        return session
    
    def generate_improvement_plan(self, session: PilotSession) -> PilotSession:
        """Generate improvement plan and track execution."""
        
        if not session.baseline_evaluation_file:
            session.technical_errors.append("No baseline evaluation file for improvement plan")
            return session
        
        try:
            cmd = [
                "arc-eval",
                "--improvement-plan", 
                "--from", session.baseline_evaluation_file,
                "--dev"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                session.technical_errors.append(f"Improvement plan generation failed: {result.stderr}")
                return session
            
            # Find generated improvement plan
            plan_files = list(Path(".").glob("improvement_plan_*.md"))
            if plan_files:
                session.improvement_plan_file = str(plan_files[-1])  # Most recent
                print(f"✅ Improvement plan generated: {session.improvement_plan_file}")
            else:
                session.technical_errors.append("No improvement plan file generated")
                
        except subprocess.TimeoutExpired:
            session.technical_errors.append("Improvement plan generation timeout")
        except Exception as e:
            session.technical_errors.append(f"Improvement plan error: {str(e)}")
        
        return session
    
    def run_comparison_evaluation(self, session: PilotSession, improved_input_file: str) -> PilotSession:
        """Run comparison evaluation with improved data."""
        
        if not session.baseline_evaluation_file:
            session.technical_errors.append("No baseline file for comparison")
            return session
        
        try:
            cmd = [
                "arc-eval",
                "--domain", session.domain,
                "--input", improved_input_file,
                "--baseline", session.baseline_evaluation_file,
                "--dev"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                session.technical_errors.append(f"Comparison evaluation failed: {result.stderr}")
                return session
            
            # Find generated comparison report
            comparison_files = list(Path(".").glob("comparison_report_*.json"))
            if comparison_files:
                session.comparison_evaluation_file = str(comparison_files[-1])  # Most recent
                print(f"✅ Comparison evaluation complete: {session.comparison_evaluation_file}")
                
                # Mark workflow as completed if no technical errors
                if not session.technical_errors:
                    session.workflow_completed = True
                    print("✅ Complete workflow validation successful")
            else:
                session.technical_errors.append("No comparison report generated")
                
        except subprocess.TimeoutExpired:
            session.technical_errors.append("Comparison evaluation timeout")
        except Exception as e:
            session.technical_errors.append(f"Comparison evaluation error: {str(e)}")
        
        return session
    
    def collect_feedback(self, session: PilotSession) -> PilotSession:
        """Collect customer feedback and usage validation."""
        
        print(f"\n📋 Collecting feedback for {session.customer_name}")
        print("Please answer based on customer responses during pilot session:")
        
        # Usage validation questions
        weekly_usage = input("Would customer use this 3+ times per week per agent? (y/n): ").lower().startswith('y')
        session.weekly_usage_intent = weekly_usage
        
        try:
            impl_pct = int(input("What percentage of recommendations would they implement? (0-100): "))
            session.implementation_percentage = max(0, min(100, impl_pct))
        except ValueError:
            session.implementation_percentage = 0
        
        value_recognized = input("Do they see clear value in before/after measurement? (y/n): ").lower().startswith('y')
        session.improvement_value_recognized = value_recognized
        
        payment_intent = input("Would they pay for continued access? (y/n): ").lower().startswith('y')
        session.payment_willingness = payment_intent
        
        # Recommendation quality feedback
        try:
            actionable_pct = int(input("What percentage of recommendations were actionable? (0-100): "))
            session.actionable_recommendations_pct = max(0, min(100, actionable_pct))
        except ValueError:
            session.actionable_recommendations_pct = 0
        
        timeline_realistic = input("Were timeline estimates realistic? (y/n): ").lower().startswith('y')
        session.timeline_realistic = timeline_realistic
        
        # Optional feedback
        missing_func = input("Missing functionality (comma-separated, or press enter): ").strip()
        if missing_func:
            session.missing_functionality = [f.strip() for f in missing_func.split(',')]
        
        integration_needs = input("Integration needs (comma-separated, or press enter): ").strip()
        if integration_needs:
            session.integration_needs = [i.strip() for i in integration_needs.split(',')]
        
        return session
    
    def save_session(self, session: PilotSession) -> str:
        """Save pilot session data to JSON file."""
        
        session_file = self.output_dir / f"pilot_{session.customer_name}_{session.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        print(f"💾 Session data saved: {session_file}")
        return str(session_file)
    
    def generate_session_report(self, session: PilotSession) -> str:
        """Generate human-readable session report."""
        
        report = f"""
# Pilot Session Report: {session.customer_name}

**Domain**: {session.domain}  
**Date**: {session.session_date[:19]}  
**Duration**: {session.execution_time_minutes:.1f} minutes

## Technical Validation
- **Workflow Completed**: {'✅ Yes' if session.workflow_completed else '❌ No'}
- **Execution Time**: {session.execution_time_minutes:.1f} minutes ({'✅ <5min' if session.execution_time_minutes < 5 else '⚠️ >5min'})
- **Technical Errors**: {len(session.technical_errors)} {'✅ None' if not session.technical_errors else '❌ Issues found'}

## Usage Validation  
- **Weekly Usage Intent**: {'✅ Yes' if session.weekly_usage_intent else '❌ No'}
- **Implementation Percentage**: {session.implementation_percentage}% ({'✅ ≥50%' if session.implementation_percentage >= 50 else '❌ <50%'})
- **Value Recognition**: {'✅ Yes' if session.improvement_value_recognized else '❌ No'}
- **Payment Willingness**: {'✅ Yes' if session.payment_willingness else '❌ No'}

## Recommendation Quality
- **Actionable Recommendations**: {session.actionable_recommendations_pct}% ({'✅ ≥80%' if session.actionable_recommendations_pct >= 80 else '⚠️ <80%'})
- **Timeline Realistic**: {'✅ Yes' if session.timeline_realistic else '❌ No'}

## Success Criteria Met
"""
        
        # Calculate success criteria
        criteria_met = 0
        total_criteria = 4
        
        if session.weekly_usage_intent:
            criteria_met += 1
            report += "- ✅ Weekly usage intent\n"
        else:
            report += "- ❌ Weekly usage intent\n"
        
        if session.implementation_percentage >= 50:
            criteria_met += 1
            report += "- ✅ Implementation rate ≥50%\n"
        else:
            report += "- ❌ Implementation rate <50%\n"
        
        if session.improvement_value_recognized:
            criteria_met += 1
            report += "- ✅ Improvement value recognized\n"
        else:
            report += "- ❌ Improvement value not recognized\n"
        
        if session.payment_willingness:
            criteria_met += 1
            report += "- ✅ Payment willingness\n"
        else:
            report += "- ❌ No payment willingness\n"
        
        success_rate = (criteria_met / total_criteria) * 100
        report += f"\n**Overall Success Rate**: {criteria_met}/{total_criteria} ({success_rate:.0f}%)\n"
        
        if session.technical_errors:
            report += f"\n## Technical Issues\n"
            for error in session.technical_errors:
                report += f"- {error}\n"
        
        if session.missing_functionality:
            report += f"\n## Missing Functionality\n"
            for func in session.missing_functionality:
                report += f"- {func}\n"
        
        if session.integration_needs:
            report += f"\n## Integration Needs\n"
            for need in session.integration_needs:
                report += f"- {need}\n"
        
        return report
    
    def analyze_pilot_cohort(self, session_files: List[str]) -> Dict[str, Any]:
        """Analyze results across multiple pilot sessions."""
        
        sessions = []
        for file_path in session_files:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
                sessions.append(session_data)
        
        if not sessions:
            return {"error": "No session data to analyze"}
        
        total_sessions = len(sessions)
        
        # Calculate aggregate metrics
        weekly_usage_count = sum(1 for s in sessions if s['weekly_usage_intent'])
        implementation_avg = sum(s['implementation_percentage'] for s in sessions) / total_sessions
        payment_intent_count = sum(1 for s in sessions if s['payment_willingness'])
        workflow_completed_count = sum(1 for s in sessions if s['workflow_completed'])
        
        analysis = {
            "total_pilots": total_sessions,
            "weekly_usage_rate": weekly_usage_count / total_sessions,
            "avg_implementation_percentage": implementation_avg,
            "payment_intent_rate": payment_intent_count / total_sessions,
            "technical_success_rate": workflow_completed_count / total_sessions,
            "success_criteria_met": {},
            "recommendation": ""
        }
        
        # Check against success thresholds
        analysis["success_criteria_met"] = {
            "weekly_usage": analysis["weekly_usage_rate"] >= self.success_thresholds["weekly_usage_intent"],
            "implementation": implementation_avg >= self.success_thresholds["implementation_rate"],
            "payment_intent": analysis["payment_intent_rate"] >= self.success_thresholds["payment_intent"],
        }
        
        # Generate recommendation
        criteria_met = sum(analysis["success_criteria_met"].values())
        if criteria_met >= 3:
            analysis["recommendation"] = "PROCEED: Success criteria met - ready for scaling"
        elif criteria_met >= 2:
            analysis["recommendation"] = "ITERATE: Partial success - address specific gaps"
        else:
            analysis["recommendation"] = "PIVOT: Core value proposition needs reassessment"
        
        return analysis


def main():
    parser = argparse.ArgumentParser(description="ARC-Eval Pilot Validation")
    parser.add_argument("command", choices=["run", "analyze"], help="Command to execute")
    parser.add_argument("--customer", required=False, help="Customer name")
    parser.add_argument("--domain", choices=["finance", "security", "ml"], help="Evaluation domain")
    parser.add_argument("--baseline-input", help="Baseline input file")
    parser.add_argument("--improved-input", help="Improved input file for comparison")
    parser.add_argument("--sessions-dir", default="pilot_results", help="Directory containing session files")
    
    args = parser.parse_args()
    
    validator = PilotValidator()
    
    if args.command == "run":
        if not all([args.customer, args.domain, args.baseline_input]):
            print("Error: --customer, --domain, and --baseline-input required for 'run' command")
            sys.exit(1)
        
        # Run complete pilot workflow
        session = validator.run_baseline_evaluation(args.domain, args.baseline_input, args.customer)
        session = validator.generate_improvement_plan(session)
        
        if args.improved_input:
            session = validator.run_comparison_evaluation(session, args.improved_input)
        
        session = validator.collect_feedback(session)
        
        # Save session and generate report
        session_file = validator.save_session(session)
        report = validator.generate_session_report(session)
        
        report_file = Path(session_file).with_suffix('.md')
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📊 Session report: {report_file}")
        print(report)
    
    elif args.command == "analyze":
        # Analyze all sessions in directory
        session_files = list(Path(args.sessions_dir).glob("pilot_*.json"))
        analysis = validator.analyze_pilot_cohort([str(f) for f in session_files])
        
        print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()