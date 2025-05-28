"""
Improvement Plan Generator for ARC-Eval Core Loop
Converts Agent-as-a-Judge evaluation results into actionable improvement plans.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from agent_eval.analysis.self_improvement import SelfImprovementEngine, TrainingExample
from agent_eval.core.types import EvaluationResult


@dataclass
class ImprovementAction:
    """Individual improvement action with priority and expected impact."""
    
    priority: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    area: str
    description: str
    action: str
    expected_improvement: str
    timeline: str
    scenario_ids: List[str]
    

@dataclass
class ImprovementPlan:
    """Complete improvement plan with prioritized actions."""
    
    agent_id: str
    domain: str
    created_at: str
    baseline_evaluation: str
    actions: List[ImprovementAction]
    summary: Dict[str, Any]
    next_steps: str
    

class ImprovementPlanner:
    """Generate actionable improvement plans from evaluation results."""
    
    def __init__(self):
        self.self_improvement_engine = SelfImprovementEngine()
    
    def generate_plan_from_evaluation(self, 
                                    evaluation_file: Path, 
                                    output_file: Optional[Path] = None) -> ImprovementPlan:
        """Generate improvement plan from evaluation results file."""
        
        # Load evaluation results
        with open(evaluation_file, 'r') as f:
            evaluation_data = json.load(f)
        
        # Extract metadata
        agent_id = evaluation_data.get('agent_id', 'unknown_agent')
        domain = evaluation_data.get('domain', 'unknown')
        
        # Get evaluation results
        results = evaluation_data.get('results', [])
        if not results:
            raise ValueError("No evaluation results found in file")
        
        # Record results for self-improvement engine
        self.self_improvement_engine.record_evaluation_result(
            agent_id=agent_id,
            domain=domain,
            evaluation_results=results
        )
        
        # Generate improvement curriculum using existing logic
        curriculum = self.self_improvement_engine.create_improvement_curriculum(
            agent_id=agent_id,
            domain=domain
        )
        
        # Convert curriculum to actionable plan
        improvement_plan = self._create_improvement_plan(
            agent_id=agent_id,
            domain=domain,
            evaluation_data=evaluation_data,
            curriculum=curriculum,
            results=results
        )
        
        # Save plan if output file specified
        if output_file:
            self._save_plan_to_markdown(improvement_plan, output_file)
        
        return improvement_plan
    
    def _create_improvement_plan(self, 
                                agent_id: str,
                                domain: str,
                                evaluation_data: Dict[str, Any],
                                curriculum: Dict[str, Any],
                                results: List[Dict[str, Any]]) -> ImprovementPlan:
        """Create structured improvement plan from curriculum."""
        
        actions = []
        
        # Process failed scenarios and create actions
        failed_scenarios = [r for r in results if not r.get('passed', True)]
        
        # Group failures by severity and type
        failure_groups = self._group_failures(failed_scenarios)
        
        # Create actions for each priority area from curriculum
        for priority_area in curriculum.get('weakness_priority', []):
            area_name = priority_area['area']
            improvement_needed = priority_area['improvement_needed']
            
            # Determine priority based on improvement needed and severity
            priority = self._calculate_priority(improvement_needed, area_name, failure_groups)
            
            # Find related failed scenarios
            related_scenarios = self._find_related_scenarios(area_name, failed_scenarios)
            scenario_ids = [s.get('scenario_id', '') for s in related_scenarios]
            
            # Generate specific action
            action = ImprovementAction(
                priority=priority,
                area=area_name,
                description=self._generate_description(area_name, related_scenarios),
                action=self._generate_action_text(area_name, related_scenarios),
                expected_improvement=self._calculate_expected_improvement(priority_area),
                timeline=self._estimate_timeline(improvement_needed),
                scenario_ids=scenario_ids
            )
            
            actions.append(action)
        
        # Sort actions by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        actions.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        # Create summary
        summary = self._create_summary(evaluation_data, actions, curriculum)
        
        # Generate next steps
        next_steps = self._generate_next_steps(evaluation_data.get('evaluation_id', 'latest'))
        
        return ImprovementPlan(
            agent_id=agent_id,
            domain=domain,
            created_at=datetime.now().isoformat(),
            baseline_evaluation=str(evaluation_data.get('evaluation_id', 'baseline')),
            actions=actions,
            summary=summary,
            next_steps=next_steps
        )
    
    def _group_failures(self, failed_scenarios: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Group failures by type and severity."""
        groups = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for scenario in failed_scenarios:
            severity = scenario.get('severity', 'medium').lower()
            if severity in groups:
                groups[severity].append(scenario)
            else:
                groups['medium'].append(scenario)
        
        return groups
    
    def _calculate_priority(self, improvement_needed: float, area_name: str, failure_groups: Dict) -> str:
        """Calculate priority based on improvement needed and failure patterns."""
        
        # Critical if security/compliance failures or high improvement needed
        if (improvement_needed > 0.4 or 
            len(failure_groups['critical']) > 0 or
            any(keyword in area_name.lower() for keyword in ['security', 'compliance', 'bias', 'leak'])):
            return "CRITICAL"
        
        # High if significant improvement needed or multiple high severity failures
        if improvement_needed > 0.25 or len(failure_groups['high']) > 2:
            return "HIGH"
        
        # Medium if moderate improvement needed
        if improvement_needed > 0.15:
            return "MEDIUM"
        
        return "LOW"
    
    def _find_related_scenarios(self, area_name: str, failed_scenarios: List[Dict]) -> List[Dict]:
        """Find scenarios related to a specific improvement area."""
        related = []
        
        # Simple keyword matching - could be enhanced with semantic similarity
        keywords = area_name.lower().split('_')
        
        for scenario in failed_scenarios:
            scenario_text = f"{scenario.get('scenario_id', '')} {scenario.get('description', '')}".lower()
            if any(keyword in scenario_text for keyword in keywords):
                related.append(scenario)
        
        return related[:3]  # Limit to top 3 related scenarios
    
    def _generate_description(self, area_name: str, related_scenarios: List[Dict]) -> str:
        """Generate human-readable description of the issue."""
        
        if not related_scenarios:
            return f"Improvement needed in {area_name.replace('_', ' ')} area"
        
        scenario_count = len(related_scenarios)
        return f"Failed {scenario_count} scenario{'s' if scenario_count > 1 else ''} in {area_name.replace('_', ' ')}"
    
    def _generate_action_text(self, area_name: str, related_scenarios: List[Dict]) -> str:
        """Generate specific action recommendation."""
        
        # Domain-specific action templates
        action_templates = {
            'compliance': "Update compliance validation logic to match regulatory requirements",
            'bias': "Add bias detection metrics and threshold-based filtering",
            'security': "Implement input sanitization and output filtering mechanisms",
            'accuracy': "Add verification steps and confidence thresholding",
            'reliability': "Implement retry logic and graceful failure handling",
            'performance': "Optimize inference pipeline and memory usage",
        }
        
        # Find matching template
        for keyword, template in action_templates.items():
            if keyword in area_name.lower():
                return template
        
        # Default action if no specific template
        return f"Address issues in {area_name.replace('_', ' ')} through targeted improvements"
    
    def _calculate_expected_improvement(self, priority_area: Dict) -> str:
        """Calculate expected improvement percentage."""
        
        current_avg = priority_area.get('current_avg', 0.0)
        target = priority_area.get('target', 0.0)
        
        if current_avg > 0:
            improvement_pct = int(((target - current_avg) / current_avg) * 100)
            return f"Pass rate ↑ from {int(current_avg * 100)}% to {int(target * 100)}%"
        else:
            return f"Target pass rate: {int(target * 100)}%"
    
    def _estimate_timeline(self, improvement_needed: float) -> str:
        """Estimate implementation timeline based on complexity."""
        
        if improvement_needed > 0.4:
            return "1-2 weeks"
        elif improvement_needed > 0.25:
            return "3-5 days"
        elif improvement_needed > 0.15:
            return "2-3 days"
        else:
            return "1-2 days"
    
    def _create_summary(self, evaluation_data: Dict, actions: List[ImprovementAction], curriculum: Dict) -> Dict[str, Any]:
        """Create executive summary of the improvement plan."""
        
        total_scenarios = len(evaluation_data.get('results', []))
        failed_scenarios = len([r for r in evaluation_data.get('results', []) if not r.get('passed', True)])
        
        priority_counts = {}
        for action in actions:
            priority_counts[action.priority] = priority_counts.get(action.priority, 0) + 1
        
        return {
            "total_scenarios_evaluated": total_scenarios,
            "failed_scenarios": failed_scenarios,
            "pass_rate": f"{int(((total_scenarios - failed_scenarios) / total_scenarios) * 100)}%" if total_scenarios > 0 else "0%",
            "improvement_actions": len(actions),
            "priority_breakdown": priority_counts,
            "estimated_total_time": curriculum.get('estimated_training_time', 'Unknown'),
            "focus_areas": [action.area.replace('_', ' ').title() for action in actions[:3]]
        }
    
    def _generate_next_steps(self, evaluation_id: str) -> str:
        """Generate next steps instruction."""
        
        return f"""WHEN DONE → Re-run evaluation:
arc-eval --domain {{domain}} --input {{improved_outputs.json}} --baseline {evaluation_id}.json"""
    
    def _save_plan_to_markdown(self, plan: ImprovementPlan, output_file: Path) -> None:
        """Save improvement plan as formatted markdown."""
        
        md_content = f"""# Improvement Plan: {plan.agent_id}

**Domain:** {plan.domain}  
**Generated:** {plan.created_at[:19]}  
**Baseline Evaluation:** {plan.baseline_evaluation}

## Summary

- **Total Scenarios:** {plan.summary['total_scenarios_evaluated']}
- **Pass Rate:** {plan.summary['pass_rate']}
- **Failed Scenarios:** {plan.summary['failed_scenarios']}
- **Recommended Actions:** {plan.summary['improvement_actions']}
- **Estimated Implementation Time:** {plan.summary['estimated_total_time']}

**Primary Focus Areas:** {', '.join(plan.summary['focus_areas'])}

---

## Recommended Actions (by Priority)

"""
        
        for i, action in enumerate(plan.actions, 1):
            priority_indicator = {
                "CRITICAL": "🔴",
                "HIGH": "🟠", 
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }.get(action.priority, "⚪")
            
            md_content += f"""### {i}. {priority_indicator} {action.priority} - {action.area.replace('_', ' ').title()}

**Failure Pattern:** {action.description}

**Recommended Change:** {action.action}

**Expected Improvement:** {action.expected_improvement}

**Implementation Time:** {action.timeline}

**Affected Scenarios:** {', '.join(action.scenario_ids) if action.scenario_ids else 'Multiple scenarios'}

---

"""
        
        md_content += f"""## Re-evaluation Command

{plan.next_steps}

---

*Generated by ARC-Eval improvement planner*
"""
        
        # Ensure output directory exists
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write markdown file
        with open(output_file, 'w') as f:
            f.write(md_content)