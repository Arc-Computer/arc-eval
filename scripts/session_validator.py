#!/usr/bin/env python3
"""
ARC-Eval Session Validation Script

Based on Core_loop.md validation requirements (lines 172-188).
Automates session tracking and success criteria measurement.
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
class EvaluationSession:
    """Track evaluation session data and metrics."""
    
    user_name: str
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


class SessionValidator:
    """Automate session validation and success criteria tracking."""
    
    def __init__(self, output_dir: str = "session_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Success criteria thresholds from Core_loop.md
        self.success_thresholds = {
            "regular_usage_intent": 0.75,  # ≥75% show regular usage intent
            "implementation_rate": 0.50,  # ≥50% of improvement plans implemented
            "improvement_measurement": 0.30,  # ≥30% violation reduction
            "value_recognition": 0.60,  # ≥60% recognize clear value
        }
    
    def run_baseline_evaluation(self, domain: str, input_file: str, user_name: str) -> EvaluationSession:
        """Execute baseline evaluation and start session tracking."""
        
        print(f"🔄 Starting session validation for {user_name} ({domain} domain)")
        start_time = time.time()
        
        session = EvaluationSession(
            user_name=user_name,
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
    
    def generate_improvement_plan(self, session: EvaluationSession) -> EvaluationSession:
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
    
    def run_comparison_evaluation(self, session: EvaluationSession, improved_input_file: str) -> EvaluationSession:
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
    
    def collect_feedback(self, session: EvaluationSession) -> EvaluationSession:
        """Collect user feedback and usage validation."""
        
        print(f"\n📋 Collecting feedback for {session.user_name}")
        print("Please answer based on user responses during session:")
        
        # Usage validation questions
        regular_usage = input("Would user integrate this into regular workflow? (y/n): ").lower().startswith('y')
        session.weekly_usage_intent = regular_usage
        
        try:
            impl_pct = int(input("What percentage of recommendations would they implement? (0-100): "))
            session.implementation_percentage = max(0, min(100, impl_pct))
        except ValueError:
            session.implementation_percentage = 0
        
        value_recognized = input("Do they see clear value in before/after measurement? (y/n): ").lower().startswith('y')
        session.improvement_value_recognized = value_recognized
        
        value_recognition = input("Do they see clear value for continued usage? (y/n): ").lower().startswith('y')
        session.payment_willingness = value_recognition
        
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
    
    def save_session(self, session: EvaluationSession) -> str:
        """Save session data to JSON file."""
        
        session_file = self.output_dir / f"session_{session.user_name}_{session.domain}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(session_file, 'w') as f:
            json.dump(asdict(session), f, indent=2)
        
        print(f"💾 Session data saved: {session_file}")
        return str(session_file)
    
    def generate_session_report(self, session: EvaluationSession) -> str:
        """Generate human-readable session report."""
        
        report = f"""
# Session Report: {session.user_name}

**Domain**: {session.domain}  
**Date**: {session.session_date[:19]}  
**Duration**: {session.execution_time_minutes:.1f} minutes

## Technical Validation
- **Workflow Completed**: {'✅ Yes' if session.workflow_completed else '❌ No'}
- **Execution Time**: {session.execution_time_minutes:.1f} minutes ({'✅ <5min' if session.execution_time_minutes < 5 else '⚠️ >5min'})
- **Technical Errors**: {len(session.technical_errors)} {'✅ None' if not session.technical_errors else '❌ Issues found'}

## Usage Validation  
- **Regular Usage Intent**: {'✅ Yes' if session.weekly_usage_intent else '❌ No'}
- **Implementation Percentage**: {session.implementation_percentage}% ({'✅ ≥50%' if session.implementation_percentage >= 50 else '❌ <50%'})
- **Value Recognition**: {'✅ Yes' if session.improvement_value_recognized else '❌ No'}
- **Continued Usage Value**: {'✅ Yes' if session.payment_willingness else '❌ No'}

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
            report += "- ✅ Regular usage intent\n"
        else:
            report += "- ❌ Regular usage intent\n"
        
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
            report += "- ✅ Continued usage value recognized\n"
        else:
            report += "- ❌ No continued usage value recognized\n"
        
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
    
    def analyze_session_cohort(self, session_files: List[str]) -> Dict[str, Any]:
        """Analyze results across multiple sessions."""
        
        sessions = []
        for file_path in session_files:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
                sessions.append(session_data)
        
        if not sessions:
            return {"error": "No session data to analyze"}
        
        total_sessions = len(sessions)
        
        # Calculate aggregate metrics
        regular_usage_count = sum(1 for s in sessions if s['weekly_usage_intent'])
        implementation_avg = sum(s['implementation_percentage'] for s in sessions) / total_sessions
        value_recognition_count = sum(1 for s in sessions if s['payment_willingness'])
        workflow_completed_count = sum(1 for s in sessions if s['workflow_completed'])
        
        analysis = {
            "total_sessions": total_sessions,
            "regular_usage_rate": regular_usage_count / total_sessions,
            "avg_implementation_percentage": implementation_avg,
            "value_recognition_rate": value_recognition_count / total_sessions,
            "technical_success_rate": workflow_completed_count / total_sessions,
            "success_criteria_met": {},
            "recommendation": ""
        }
        
        # Check against success thresholds
        analysis["success_criteria_met"] = {
            "regular_usage": analysis["regular_usage_rate"] >= self.success_thresholds["regular_usage_intent"],
            "implementation": implementation_avg >= self.success_thresholds["implementation_rate"],
            "value_recognition": analysis["value_recognition_rate"] >= self.success_thresholds["value_recognition"],
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
    parser = argparse.ArgumentParser(description="ARC-Eval Session Validation")
    parser.add_argument("command", choices=["run", "analyze"], help="Command to execute")
    parser.add_argument("--user", required=False, help="User name")
    parser.add_argument("--domain", choices=["finance", "security", "ml"], help="Evaluation domain")
    parser.add_argument("--baseline-input", help="Baseline input file")
    parser.add_argument("--improved-input", help="Improved input file for comparison")
    parser.add_argument("--sessions-dir", default="session_results", help="Directory containing session files")
    
    args = parser.parse_args()
    
    validator = SessionValidator()
    
    if args.command == "run":
        if not all([args.user, args.domain, args.baseline_input]):
            print("Error: --user, --domain, and --baseline-input required for 'run' command")
            sys.exit(1)
        
        # Run complete session workflow
        session = validator.run_baseline_evaluation(args.domain, args.baseline_input, args.user)
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
        session_files = list(Path(args.sessions_dir).glob("session_*.json"))
        analysis = validator.analyze_session_cohort([str(f) for f in session_files])
        
        print(json.dumps(analysis, indent=2))


if __name__ == "__main__":
    main()