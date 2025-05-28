"""
Basic usage analytics tracking for ARC-Eval pilot validation.
Tracks key metrics for core loop workflow adoption.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class UsageEvent:
    """Individual usage event tracking."""
    
    timestamp: str
    event_type: str  # "evaluation", "improvement_plan", "comparison"
    domain: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    duration_seconds: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class UsageAnalytics:
    """Simple analytics tracker for pilot validation."""
    
    def __init__(self, analytics_dir: str = ".arc_analytics"):
        self.analytics_dir = Path(analytics_dir)
        self.analytics_dir.mkdir(exist_ok=True)
        
        # Analytics files
        self.events_file = self.analytics_dir / "usage_events.jsonl"
        self.summary_file = self.analytics_dir / "usage_summary.json"
        
        # Session tracking
        self.current_session = self._generate_session_id()
    
    def track_event(self, event_type: str, domain: str, duration_seconds: Optional[float] = None,
                   success: bool = True, error_message: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """Track a usage event."""
        
        event = UsageEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            domain=domain,
            session_id=self.current_session,
            duration_seconds=duration_seconds,
            success=success,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        # Append to events file
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(asdict(event)) + '\n')
    
    def track_evaluation(self, domain: str, duration_seconds: float, 
                        scenario_count: int, pass_rate: float, success: bool = True,
                        error_message: Optional[str] = None) -> None:
        """Track evaluation execution."""
        
        metadata = {
            "scenario_count": scenario_count,
            "pass_rate": pass_rate
        }
        
        self.track_event("evaluation", domain, duration_seconds, success, error_message, metadata)
    
    def track_improvement_plan(self, domain: str, evaluation_file: str,
                             action_count: int, success: bool = True,
                             error_message: Optional[str] = None) -> None:
        """Track improvement plan generation."""
        
        metadata = {
            "evaluation_file": evaluation_file,
            "action_count": action_count
        }
        
        self.track_event("improvement_plan", domain, None, success, error_message, metadata)
    
    def track_comparison(self, domain: str, baseline_file: str,
                        net_improvement: int, pass_rate_change: float,
                        success: bool = True, error_message: Optional[str] = None) -> None:
        """Track comparison evaluation."""
        
        metadata = {
            "baseline_file": baseline_file,
            "net_improvement": net_improvement,
            "pass_rate_change": pass_rate_change
        }
        
        self.track_event("comparison", domain, None, success, error_message, metadata)
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate usage summary statistics."""
        
        if not self.events_file.exists():
            return {"error": "No usage data available"}
        
        events = []
        with open(self.events_file, 'r') as f:
            for line in f:
                events.append(json.loads(line))
        
        if not events:
            return {"error": "No events recorded"}
        
        # Calculate summary metrics
        total_events = len(events)
        
        # Event type breakdown
        event_counts = {}
        for event in events:
            event_type = event['event_type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        # Domain usage
        domain_counts = {}
        for event in events:
            domain = event['domain']
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        # Success rate
        successful_events = sum(1 for event in events if event['success'])
        success_rate = (successful_events / total_events) * 100
        
        # Core loop completion tracking
        sessions = {}
        for event in events:
            session_id = event.get('session_id', 'unknown')
            if session_id not in sessions:
                sessions[session_id] = {'events': [], 'complete_workflow': False}
            sessions[session_id]['events'].append(event['event_type'])
        
        # Check for complete workflows (evaluation + improvement_plan + comparison)
        complete_workflows = 0
        for session_data in sessions.values():
            events_in_session = set(session_data['events'])
            if {'evaluation', 'improvement_plan', 'comparison'}.issubset(events_in_session):
                complete_workflows += 1
        
        # Recent activity (last 7 days)
        recent_cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
        recent_events = [
            event for event in events 
            if datetime.fromisoformat(event['timestamp']).timestamp() > recent_cutoff
        ]
        
        summary = {
            "total_events": total_events,
            "event_breakdown": event_counts,
            "domain_usage": domain_counts,
            "success_rate": f"{success_rate:.1f}%",
            "total_sessions": len(sessions),
            "complete_workflows": complete_workflows,
            "workflow_completion_rate": f"{(complete_workflows / len(sessions)) * 100:.1f}%" if sessions else "0%",
            "recent_activity_7d": len(recent_events),
            "generated_at": datetime.now().isoformat()
        }
        
        # Save summary
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def get_pilot_metrics(self) -> Dict[str, Any]:
        """Get pilot-specific metrics for validation."""
        
        summary = self.generate_summary()
        
        if "error" in summary:
            return summary
        
        # Calculate pilot validation metrics
        pilot_metrics = {
            "usage_frequency": {
                "total_evaluations": summary["event_breakdown"].get("evaluation", 0),
                "evaluations_per_week": summary["recent_activity_7d"] / 7 if summary["recent_activity_7d"] > 0 else 0,
                "meets_3x_week_threshold": summary["recent_activity_7d"] >= 21  # 3 per day * 7 days
            },
            "workflow_adoption": {
                "complete_workflows": summary["complete_workflows"],
                "workflow_completion_rate": summary["workflow_completion_rate"],
                "meets_completion_threshold": complete_workflows >= 2  # At least 2 complete workflows
            },
            "technical_reliability": {
                "success_rate": summary["success_rate"],
                "meets_reliability_threshold": float(summary["success_rate"].replace('%', '')) >= 90
            },
            "domain_distribution": summary["domain_usage"]
        }
        
        return pilot_metrics
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


# Global analytics instance
_analytics = None

def get_analytics() -> UsageAnalytics:
    """Get global analytics instance."""
    global _analytics
    if _analytics is None:
        _analytics = UsageAnalytics()
    return _analytics


def track_evaluation(domain: str, duration_seconds: float, scenario_count: int, 
                    pass_rate: float, success: bool = True, error_message: Optional[str] = None) -> None:
    """Convenience function for tracking evaluations."""
    get_analytics().track_evaluation(domain, duration_seconds, scenario_count, pass_rate, success, error_message)


def track_improvement_plan(domain: str, evaluation_file: str, action_count: int,
                          success: bool = True, error_message: Optional[str] = None) -> None:
    """Convenience function for tracking improvement plans."""
    get_analytics().track_improvement_plan(domain, evaluation_file, action_count, success, error_message)


def track_comparison(domain: str, baseline_file: str, net_improvement: int, 
                    pass_rate_change: float, success: bool = True, error_message: Optional[str] = None) -> None:
    """Convenience function for tracking comparisons."""
    get_analytics().track_comparison(domain, baseline_file, net_improvement, pass_rate_change, success, error_message)