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
    
    def calculate_learning_progress(self, agent_id: str, domain: str, window_size: int = 10) -> float:
        """
        Calculate TD-error based learning progress for more stable curriculum decisions.
        
        Args:
            agent_id: Agent identifier
            domain: Domain (e.g., 'finance')
            window_size: Number of recent evaluations to consider
            
        Returns:
            Learning progress score [0.0, 1.0] where higher indicates more learning
        """
        if not self.history_file.exists():
            return 0.0 
        
        recent_rewards = []
        historical_rewards = []
        
        with open(self.history_file, 'r') as f:
            all_entries = [json.loads(line) for line in f 
                          if json.loads(line)['agent_id'] == agent_id and 
                             json.loads(line)['domain'] == domain]
        
        if len(all_entries) < window_size:
            return 0.0
        
        # Split into recent and historical windows
        recent_entries = all_entries[-window_size:]
        historical_entries = all_entries[-(window_size*2):-window_size] if len(all_entries) >= window_size*2 else all_entries[:-window_size]
        
        # Extract average reward signals
        for entry in recent_entries:
            reward_avg = sum(entry['reward_signals'].values()) / len(entry['reward_signals'])
            recent_rewards.append(reward_avg)
            
        for entry in historical_entries:
            reward_avg = sum(entry['reward_signals'].values()) / len(entry['reward_signals'])
            historical_rewards.append(reward_avg)
        
        if not recent_rewards or not historical_rewards:
            return 0.0
            
        # Calculate TD-error based learning progress
        import numpy as np
        recent_mean = np.mean(recent_rewards)
        historical_mean = np.mean(historical_rewards)
        
        # TD-error represents how much the agent is learning (improving)
        td_error = abs(recent_mean - historical_mean)
        
        # Normalize to [0,1] and add direction bias (improvement vs decline)
        normalized_progress = min(td_error, 1.0)
        
        # Boost if improving, reduce if declining
        if recent_mean > historical_mean:
            normalized_progress = min(normalized_progress * 1.2, 1.0)  # 20% boost for improvement
        else:
            normalized_progress = max(normalized_progress * 0.8, 0.0)  # 20% reduction for decline
            
        return normalized_progress
    
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
    
    def get_scenario_specific_performance(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """
        Get performance breakdown by individual scenarios and compliance areas.
        
        Returns detailed performance metrics for ACL-based adaptive curriculum.
        """
        history = self._load_performance_history(agent_id, domain, lookback_days=90)
        
        if not history:
            return {
                "scenario_performance": {},
                "compliance_area_performance": {},
                "weakness_areas": [],
                "mastered_areas": [],
                "overall_pass_rate": 0.0
            }
        
        # Track performance per scenario ID
        scenario_performance = {}
        compliance_performance = {}
        
        total_evaluations = 0
        total_passed = 0
        
        for entry in history:
            scenario_id = entry.get('scenario_id', 'unknown')
            reward_signals = entry.get('reward_signals', {})
            compliance_gaps = entry.get('compliance_gaps', [])
            
            # Aggregate scenario performance
            if scenario_id not in scenario_performance:
                scenario_performance[scenario_id] = {
                    'attempts': 0,
                    'successes': 0,
                    'pass_rate': 0.0,
                    'avg_confidence': 0.0,
                    'recent_trend': 'stable'
                }
            
            scenario_performance[scenario_id]['attempts'] += 1
            
            # Consider successful if average reward signal > 0.7
            avg_reward = sum(reward_signals.values()) / len(reward_signals) if reward_signals else 0.0
            if avg_reward > 0.7:
                scenario_performance[scenario_id]['successes'] += 1
                total_passed += 1
            
            total_evaluations += 1
            scenario_performance[scenario_id]['avg_confidence'] = avg_reward
            
            # Track compliance area performance
            for compliance_area in compliance_gaps:
                if compliance_area not in compliance_performance:
                    compliance_performance[compliance_area] = {
                        'violations': 0,
                        'total_checks': 0,
                        'violation_rate': 0.0
                    }
                compliance_performance[compliance_area]['violations'] += 1
                compliance_performance[compliance_area]['total_checks'] += 1
        
        # Calculate pass rates
        for scenario_id, perf in scenario_performance.items():
            perf['pass_rate'] = perf['successes'] / perf['attempts'] if perf['attempts'] > 0 else 0.0
        
        for comp_area, perf in compliance_performance.items():
            perf['violation_rate'] = perf['violations'] / perf['total_checks'] if perf['total_checks'] > 0 else 0.0
        
        # Identify weakness and mastered areas
        weakness_areas = [
            area for area, perf in compliance_performance.items()
            if perf['violation_rate'] > 0.3  # More than 30% violation rate
        ]
        
        mastered_areas = [
            area for area, perf in compliance_performance.items()
            if perf['violation_rate'] < 0.1  # Less than 10% violation rate
        ]
        
        overall_pass_rate = total_passed / total_evaluations if total_evaluations > 0 else 0.0
        
        return {
            "scenario_performance": scenario_performance,
            "compliance_area_performance": compliance_performance,
            "weakness_areas": weakness_areas,
            "mastered_areas": mastered_areas,
            "overall_pass_rate": overall_pass_rate,
            "total_evaluations": total_evaluations,
            "recent_trend": self._calculate_recent_trend(history)
        }
    
    def recommend_next_scenarios(self, agent_id: str, domain: str, 
                               current_pass_rate: float) -> List[str]:
        """
        Recommend scenarios for next iteration based on mastery progression.
        
        Uses ACL principles to select scenarios in the optimal learning zone.
        """
        performance_data = self.get_scenario_specific_performance(agent_id, domain)
        scenario_performance = performance_data.get('scenario_performance', {})
        
        # Find scenarios in the "learning zone" (60-80% pass rate)
        learning_zone_scenarios = []
        review_scenarios = []  # Low performance scenarios
        mastery_scenarios = []  # High performance scenarios
        
        for scenario_id, perf in scenario_performance.items():
            pass_rate = perf['pass_rate']
            attempts = perf['attempts']
            
            # Only consider scenarios with sufficient data
            if attempts >= 2:
                if 0.6 <= pass_rate <= 0.8:
                    learning_zone_scenarios.append(scenario_id)
                elif pass_rate < 0.6:
                    review_scenarios.append(scenario_id)
                elif pass_rate > 0.8:
                    mastery_scenarios.append(scenario_id)
        
        # Prioritize learning zone, then review scenarios
        recommendations = learning_zone_scenarios[:3]
        
        if len(recommendations) < 3:
            remaining = 3 - len(recommendations)
            recommendations.extend(review_scenarios[:remaining])
        
        # If still not enough, include some mastery scenarios for confidence
        if len(recommendations) < 3:
            remaining = 3 - len(recommendations)
            recommendations.extend(mastery_scenarios[:remaining])
        
        return recommendations
    
    def calculate_readiness_for_difficulty(self, agent_id: str, domain: str) -> str:
        """
        Determine if agent is ready for next difficulty level.
        
        Returns: 'basic', 'intermediate', or 'advanced'
        """
        performance_data = self.get_scenario_specific_performance(agent_id, domain)
        overall_pass_rate = performance_data.get('overall_pass_rate', 0.0)
        recent_trend = performance_data.get('recent_trend', 'stable')
        weakness_areas = performance_data.get('weakness_areas', [])
        
        # ACL-based progression thresholds
        if overall_pass_rate >= 0.85 and len(weakness_areas) <= 1 and recent_trend in ['improving', 'stable']:
            return 'advanced'
        elif overall_pass_rate >= 0.65 and len(weakness_areas) <= 3 and recent_trend in ['improving', 'stable']:
            return 'intermediate'
        elif overall_pass_rate < 0.4 or recent_trend == 'declining':
            return 'basic'  # Step back if struggling
        else:
            return 'basic'  # Conservative default
    
    def get_adaptive_curriculum_data(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """
        Get comprehensive data for adaptive curriculum generation.
        
        Combines performance trends, scenario analysis, and readiness assessment
        for use with adaptive scenario selection in flywheel experiments.
        """
        performance_data = self.get_scenario_specific_performance(agent_id, domain)
        trends = self.get_performance_trends(agent_id, domain)
        readiness = self.calculate_readiness_for_difficulty(agent_id, domain)
        recommendations = self.recommend_next_scenarios(agent_id, domain, 
                                                      performance_data.get('overall_pass_rate', 0.0))
        
        # Calculate learning progress for enhanced curriculum decisions
        learning_progress = self.calculate_learning_progress(agent_id, domain)
        
        return {
            "performance_summary": {
                "overall_pass_rate": performance_data.get('overall_pass_rate', 0.0),
                "total_evaluations": performance_data.get('total_evaluations', 0),
                "recent_trend": performance_data.get('recent_trend', 'stable'),
                "weakness_areas": performance_data.get('weakness_areas', []),
                "mastered_areas": performance_data.get('mastered_areas', []),
                "learning_progress": learning_progress
            },
            "scenario_readiness": {
                "recommended_difficulty": readiness,
                "recommended_scenarios": recommendations,
                "learning_zone_count": len([
                    s for s, p in performance_data.get('scenario_performance', {}).items()
                    if 0.6 <= p.get('pass_rate', 0.0) <= 0.8
                ])
            },
            "detailed_performance": {
                "scenario_performance": performance_data.get('scenario_performance', {}),
                "compliance_area_performance": performance_data.get('compliance_area_performance', {})
            },
            "trends": trends.get('reward_trends', {}),
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_recent_trend(self, history: List[Dict], lookback_count: int = 5) -> str:
        """
        Calculate recent performance trend from evaluation history.
        
        Returns: 'improving', 'declining', or 'stable'
        """
        if len(history) < 3:
            return 'stable'
        
        # Get recent evaluations
        recent_history = history[-lookback_count:] if len(history) >= lookback_count else history
        
        # Calculate average rewards for first and second half
        mid_point = len(recent_history) // 2
        first_half = recent_history[:mid_point]
        second_half = recent_history[mid_point:]
        
        if not first_half or not second_half:
            return 'stable'
        
        # Calculate average performance for each half
        first_avg = self._calculate_average_performance(first_half)
        second_avg = self._calculate_average_performance(second_half)
        
        improvement_threshold = 0.05  # 5% improvement threshold
        
        if second_avg - first_avg > improvement_threshold:
            return 'improving'
        elif first_avg - second_avg > improvement_threshold:
            return 'declining'
        else:
            return 'stable'
    
    def _calculate_average_performance(self, evaluations: List[Dict]) -> float:
        """
        Calculate average performance across evaluations.
        """
        total_performance = 0.0
        count = 0
        
        for eval_data in evaluations:
            reward_signals = eval_data.get('reward_signals', {})
            if reward_signals:
                avg_reward = sum(reward_signals.values()) / len(reward_signals)
                total_performance += avg_reward
                count += 1
        
        return total_performance / count if count > 0 else 0.0


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
    
    def get_adaptive_curriculum(self, agent_id: str, domain: str) -> Dict[str, Any]:
        """Get adaptive curriculum data for ACL-based learning."""
        return self.engine.get_adaptive_curriculum_data(agent_id, domain)
