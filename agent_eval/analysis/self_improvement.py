"""
Self-Improvement Engine for Agent Retraining Loop
Converts Agent-as-a-Judge feedback into actionable training data.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import json
from pathlib import Path
from agent_eval.profiler.decorators import track_evaluation

@dataclass
class RewardSignalHistory:
    """Track reward signal progression over time."""
    
    agent_id: str
    scenario_id: str
    domain: str
    timestamp: datetime
    reward_signals: Dict[str, float]
    improvement_recommendations: List[str]
    compliance_gaps: List[str]
    performance_metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

@dataclass
class TrainingExample:
    """Generated training example from failed evaluation."""
    
    scenario_id: str
    domain: str
    category: str
    severity: str
    failed_output: str
    correct_output: str
    reasoning_trace: List[Dict[str, Any]]
    improvement_focus: List[str]
    reward_signal_target: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for training pipeline."""
        return asdict(self)

class SelfImprovementEngine:
    """Engine for converting evaluation feedback into retraining data."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize with optional custom storage location."""
        self.storage_path = storage_path or Path("./retraining_data")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking files
        self.history_file = self.storage_path / "reward_signal_history.jsonl"
        self.training_file = self.storage_path / "training_examples.jsonl"
        self.curriculum_file = self.storage_path / "improvement_curriculum.json"
    
    @track_evaluation
    def record_evaluation_result(self, 
                               agent_id: str,
                               domain: str,
                               evaluation_results: List[Dict[str, Any]]) -> None:
        """Record evaluation results for performance tracking."""
        
        timestamp = datetime.now()
        
        for result in evaluation_results:
            if 'reward_signals' in result and 'scenario_id' in result:
                history_entry = RewardSignalHistory(
                    agent_id=agent_id,
                    scenario_id=result['scenario_id'],
                    domain=domain,
                    timestamp=timestamp,
                    reward_signals=result['reward_signals'],
                    improvement_recommendations=result.get('improvement_recommendations', []),
                    compliance_gaps=result.get('compliance_gaps', []),
                    performance_metrics=result.get('performance_metrics', {})
                )
                
                # Append to history file
                with open(self.history_file, 'a') as f:
                    f.write(json.dumps(history_entry.to_dict()) + '\n')
    
    def generate_training_examples(self, 
                                 agent_id: str,
                                 domain: str,
                                 min_reward_threshold: float = 0.6) -> List[TrainingExample]:
        """Generate training examples from failed evaluations."""
        
        training_examples = []
        
        # Load recent evaluation history
        recent_failures = self._get_recent_failures(agent_id, domain, min_reward_threshold)
        
        for failure in recent_failures:
            # Generate corrected output based on improvement recommendations
            correct_output = self._generate_corrected_output(failure)
            
            # Create training example
            example = TrainingExample(
                scenario_id=failure['scenario_id'],
                domain=domain,
                category=failure.get('category', 'general'),
                severity=failure.get('severity', 'medium'),
                failed_output=failure.get('agent_output', ''),
                correct_output=correct_output,
                reasoning_trace=failure.get('reasoning_trace', []),
                improvement_focus=failure['improvement_recommendations'],
                reward_signal_target=self._calculate_target_rewards(failure['reward_signals'])
            )
            
            training_examples.append(example)
            
            # Save to training file
            with open(self.training_file, 'a') as f:
                f.write(json.dumps(example.to_dict()) + '\n')
        
        return training_examples
    
    def create_improvement_curriculum(self, 
                                    agent_id: str,
                                    domain: str) -> Dict[str, Any]:
        """Create progressive training curriculum based on weakness analysis."""
        
        # Analyze performance patterns
        weakness_analysis = self._analyze_weaknesses(agent_id, domain)
        
        curriculum = {
            "agent_id": agent_id,
            "domain": domain,
            "created_at": datetime.now().isoformat(),
            "weakness_priority": weakness_analysis['priority_areas'],
            "training_progression": self._create_training_progression(weakness_analysis),
            "target_improvements": weakness_analysis['target_rewards'],
            "estimated_training_time": self._estimate_training_time(weakness_analysis)
        }
        
        # Save curriculum
        with open(self.curriculum_file, 'w') as f:
            json.dump(curriculum, f, indent=2)
        
        return curriculum
    
    def get_performance_trends(self, 
                             agent_id: str,
                             domain: str,
                             lookback_days: int = 30) -> Dict[str, Any]:
        """Get performance trends for the agent over time."""
        
        history = self._load_performance_history(agent_id, domain, lookback_days)
        
        if not history:
            return {"error": "No performance history found"}
        
        trends = {}
        for reward_type in history[0]['reward_signals'].keys():
            values = [entry['reward_signals'][reward_type] for entry in history]
            trends[reward_type] = {
                "current": values[-1],
                "trend": "improving" if values[-1] > values[0] else "declining",
                "change": values[-1] - values[0],
                "average": sum(values) / len(values),
                "history": values
            }
        
        return {
            "agent_id": agent_id,
            "domain": domain,
            "evaluation_count": len(history),
            "date_range": {
                "start": history[0]['timestamp'],
                "end": history[-1]['timestamp']
            },
            "reward_trends": trends,
            "improvement_velocity": self._calculate_improvement_velocity(history)
        }
    
    def should_trigger_retraining(self, 
                                agent_id: str,
                                domain: str,
                                threshold: float = 0.1) -> Tuple[bool, Dict[str, Any]]:
        """Determine if agent needs retraining based on performance degradation."""
        
        trends = self.get_performance_trends(agent_id, domain)
        
        if "error" in trends:
            return False, trends
        
        # Check for significant performance drops
        declining_areas = []
        for reward_type, trend_data in trends['reward_trends'].items():
            if trend_data['trend'] == 'declining' and abs(trend_data['change']) > threshold:
                declining_areas.append({
                    "area": reward_type,
                    "decline": trend_data['change'],
                    "current_score": trend_data['current']
                })
        
        needs_retraining = len(declining_areas) > 0
        
        recommendation = {
            "needs_retraining": needs_retraining,
            "declining_areas": declining_areas,
            "recommended_actions": self._generate_retraining_recommendations(declining_areas),
            "urgency": "high" if any(area['current_score'] < 0.5 for area in declining_areas) else "medium"
        }
        
        return needs_retraining, recommendation
    
    # Helper methods
    def _get_recent_failures(self, agent_id: str, domain: str, threshold: float) -> List[Dict]:
        """Load recent evaluation failures below threshold."""
        failures = []
        
        if not self.history_file.exists():
            return failures
        
        with open(self.history_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if (entry['agent_id'] == agent_id and 
                    entry['domain'] == domain and
                    any(score < threshold for score in entry['reward_signals'].values())):
                    failures.append(entry)
        
        return failures[-20:]  # Last 20 failures
    
    def _generate_corrected_output(self, failure: Dict) -> str:
        """Generate corrected output based on improvement recommendations."""
        recommendations = failure.get('improvement_recommendations', [])
        
        if not recommendations:
            return "Corrected response following compliance guidelines."
        
        # Create corrected response incorporating recommendations
        corrections = []
        for rec in recommendations[:3]:  # Top 3 recommendations
            corrections.append(f"- {rec}")
        
        return f"Corrected response implementing: {'; '.join(corrections)}"
    
    def _calculate_target_rewards(self, current_rewards: Dict[str, float]) -> Dict[str, float]:
        """Calculate target reward signals for improvement."""
        targets = {}
        for reward_type, current_score in current_rewards.items():
            # Target 20% improvement, capped at 1.0
            target = min(1.0, current_score + 0.2)
            targets[reward_type] = target
        return targets
    
    def _analyze_weaknesses(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """Analyze performance patterns to identify weakness areas."""
        history = self._load_performance_history(agent_id, domain, lookback_days=90)
        
        if not history:
            return {"priority_areas": [], "target_rewards": {}}
        
        # Calculate average scores per reward type
        reward_averages = {}
        for entry in history:
            for reward_type, score in entry['reward_signals'].items():
                if reward_type not in reward_averages:
                    reward_averages[reward_type] = []
                reward_averages[reward_type].append(score)
        
        # Identify lowest performing areas
        priority_areas = []
        target_rewards = {}
        
        for reward_type, scores in reward_averages.items():
            avg_score = sum(scores) / len(scores)
            target_rewards[reward_type] = min(1.0, avg_score + 0.3)
            
            if avg_score < 0.7:  # Below acceptable threshold
                priority_areas.append({
                    "area": reward_type,
                    "current_avg": avg_score,
                    "target": target_rewards[reward_type],
                    "improvement_needed": target_rewards[reward_type] - avg_score
                })
        
        # Sort by improvement needed
        priority_areas.sort(key=lambda x: x['improvement_needed'], reverse=True)
        
        return {
            "priority_areas": priority_areas,
            "target_rewards": target_rewards
        }
    
    def _create_training_progression(self, weakness_analysis: Dict) -> List[Dict]:
        """Create progressive training plan."""
        progression = []
        
        for i, area in enumerate(weakness_analysis['priority_areas'][:3]):  # Top 3 areas
            phase = {
                "phase": i + 1,
                "focus_area": area['area'],
                "target_improvement": area['improvement_needed'],
                "estimated_duration": "1-2 weeks",
                "training_methods": [
                    "Focused scenario practice",
                    "Reward signal optimization",
                    "Compliance framework training"
                ]
            }
            progression.append(phase)
        
        return progression
    
    def _estimate_training_time(self, weakness_analysis: Dict) -> str:
        """Estimate training time based on improvement needed."""
        total_improvement = sum(area['improvement_needed'] for area in weakness_analysis['priority_areas'])
        
        if total_improvement < 0.5:
            return "1-2 weeks"
        elif total_improvement < 1.0:
            return "2-4 weeks"
        else:
            return "4-6 weeks"
    
    def _load_performance_history(self, agent_id: str, domain: str, lookback_days: int) -> List[Dict]:
        """Load performance history for analysis."""
        history = []
        cutoff_date = datetime.now().timestamp() - (lookback_days * 24 * 60 * 60)
        
        if not self.history_file.exists():
            return history
        
        with open(self.history_file, 'r') as f:
            for line in f:
                entry = json.loads(line)
                entry_time = datetime.fromisoformat(entry['timestamp']).timestamp()
                
                if (entry['agent_id'] == agent_id and 
                    entry['domain'] == domain and
                    entry_time >= cutoff_date):
                    history.append(entry)
        
        return sorted(history, key=lambda x: x['timestamp'])
    
    def _calculate_improvement_velocity(self, history: List[Dict]) -> float:
        """Calculate rate of improvement over time."""
        if len(history) < 2:
            return 0.0
        
        # Calculate average reward signal improvement
        first_avg = sum(history[0]['reward_signals'].values()) / len(history[0]['reward_signals'])
        last_avg = sum(history[-1]['reward_signals'].values()) / len(history[-1]['reward_signals'])
        
        time_diff = datetime.fromisoformat(history[-1]['timestamp']) - datetime.fromisoformat(history[0]['timestamp'])
        days_diff = time_diff.days or 1
        
        return (last_avg - first_avg) / days_diff
    
    def _generate_retraining_recommendations(self, declining_areas: List[Dict]) -> List[str]:
        """Generate specific retraining recommendations."""
        recommendations = []
        
        for area in declining_areas:
            area_name = area['area']
            if 'compliance' in area_name.lower():
                recommendations.append(f"Focus on regulatory framework training for {area_name}")
            elif 'bias' in area_name.lower():
                recommendations.append(f"Implement bias detection and mitigation training")
            elif 'security' in area_name.lower():
                recommendations.append(f"Enhance threat detection and security protocol training")
            else:
                recommendations.append(f"Targeted training for {area_name} improvement")
        
        return recommendations


# Usage Example API
class AgentSelfImprovementAPI:
    """Public API for agent self-improvement integration."""
    
    def __init__(self):
        self.engine = SelfImprovementEngine()
    
    def get_my_performance(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """API for agents to query their own performance."""
        return self.engine.get_performance_trends(agent_id, domain)
    
    def get_improvement_plan(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """Get personalized improvement curriculum."""
        return self.engine.create_improvement_curriculum(agent_id, domain)
    
    def check_retraining_needed(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """Check if agent needs retraining."""
        needs_retraining, details = self.engine.should_trigger_retraining(agent_id, domain)
        return {"needs_retraining": needs_retraining, **details}
    
    def generate_training_data(self, agent_id: str, domain: str) -> List[Dict]:
        """Generate training examples from recent failures."""
        examples = self.engine.generate_training_examples(agent_id, domain)
        return [ex.to_dict() for ex in examples]