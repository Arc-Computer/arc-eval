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
from agent_eval.evaluation.judges import AgentJudge


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
    compliance_frameworks: List[str]
    specific_steps: List[str]
    

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
        self.agent_judge = None  # Initialize when domain is known
    
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
        
        # Initialize AgentJudge with domain
        if not self.agent_judge:
            self.agent_judge = AgentJudge(domain=domain, preferred_model="claude-sonnet-4-20250514")
        
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
        
        # Group failures by severity and scenario details
        failure_groups = self._group_failures_enhanced(failed_scenarios, evaluation_data.get('domain'))
        
        # Create actions directly from failed scenarios (more specific approach)
        actions = self._create_actions_from_scenarios(failed_scenarios, evaluation_data)
        
        # Sort actions by priority
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        actions.sort(key=lambda x: priority_order.get(x.priority, 4))
        
        # Create summary
        summary = self._create_summary(evaluation_data, actions, curriculum)
        
        # Generate next steps
        next_steps = self._generate_next_steps(evaluation_data.get('evaluation_id', 'latest'), domain)
        
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
    
    def _group_failures_enhanced(self, failed_scenarios: List[Dict[str, Any]], domain: str) -> Dict[str, List[Dict]]:
        """Enhanced failure grouping with scenario context analysis."""
        
        # Load domain scenarios to get compliance context
        domain_scenarios = self._load_domain_scenarios(domain)
        
        groups = {
            "mcp_security": [],
            "bias_fairness": [], 
            "model_performance": [],
            "operational_reliability": [],
            "compliance": [],
            "other": []
        }
        
        for scenario in failed_scenarios:
            scenario_id = scenario.get('scenario_id', '')
            
            # Find matching domain scenario for context
            domain_scenario = domain_scenarios.get(scenario_id, {})
            category = domain_scenario.get('category', 'other')
            compliance = domain_scenario.get('compliance', [])
            
            # Enhanced scenario with domain context
            enhanced_scenario = {
                **scenario,
                'category': category,
                'compliance': compliance,
                'name': domain_scenario.get('name', ''),
                'remediation': domain_scenario.get('remediation', '')
            }
            
            # Categorize by type
            if 'mcp' in category:
                groups['mcp_security'].append(enhanced_scenario)
            elif 'bias' in category or any('bias' in c.lower() for c in compliance):
                groups['bias_fairness'].append(enhanced_scenario)
            elif 'performance' in category:
                groups['model_performance'].append(enhanced_scenario)
            elif 'reliability' in category or 'operational' in category:
                groups['operational_reliability'].append(enhanced_scenario)
            elif any('compliance' in c.lower() for c in compliance):
                groups['compliance'].append(enhanced_scenario)
            else:
                groups['other'].append(enhanced_scenario)
        
        return groups
    
    def _load_domain_scenarios(self, domain: str) -> Dict[str, Dict]:
        """Load domain scenarios for context enrichment."""
        try:
            import yaml
            domain_file = Path(__file__).parent.parent / 'domains' / f'{domain}.yaml'
            
            with open(domain_file, 'r') as f:
                domain_data = yaml.safe_load(f)
            
            scenarios_dict = {}
            for scenario in domain_data.get('scenarios', []):
                scenarios_dict[scenario['id']] = scenario
            
            return scenarios_dict
        except Exception:
            return {}
    
    def _create_actions_from_scenarios(self, failed_scenarios: List[Dict], evaluation_data: Dict) -> List[ImprovementAction]:
        """Create specific actions from individual failed scenarios."""
        
        domain = evaluation_data.get('domain', 'unknown')
        failure_groups = self._group_failures_enhanced(failed_scenarios, domain)
        actions = []
        
        # Create action for each group with multiple failures
        for group_name, scenarios in failure_groups.items():
            if not scenarios:
                continue
                
            # Generate AI-powered specific action for this group
            action = self._generate_ai_action(group_name, scenarios, domain)
            if action:
                actions.append(action)
        
        return actions
    
    def _generate_ai_action(self, group_name: str, scenarios: List[Dict], domain: str) -> Optional[ImprovementAction]:
        """Generate AI-powered specific action for a group of failed scenarios."""
        
        if not scenarios:
            return None
        
        # Prepare context for AI analysis
        scenario_context = []
        for s in scenarios:
            scenario_context.append({
                'id': s.get('scenario_id', ''),
                'name': s.get('name', ''),
                'description': s.get('description', ''),
                'severity': s.get('severity', ''),
                'compliance': s.get('compliance', []),
                'remediation': s.get('remediation', ''),
                'improvement_recommendations': s.get('improvement_recommendations', [])
            })
        
        # Generate AI-powered remediation
        ai_analysis = self._get_ai_remediation_analysis(group_name, scenario_context, domain)
        
        if not ai_analysis:
            return self._generate_fallback_action(group_name, scenarios)
        
        scenario_ids = [s.get('scenario_id', '') for s in scenarios]
        compliance_frameworks = list(set([f for s in scenarios for f in s.get('compliance', [])]))
        
        return ImprovementAction(
            priority=self._determine_priority_from_scenarios(scenarios),
            area=group_name.replace('_', ' ').title(),
            description=ai_analysis.get('description', f"Critical failures in {group_name}"),
            action=ai_analysis.get('action', f"Address {group_name} issues"),
            expected_improvement=ai_analysis.get('expected_improvement', "Significant improvement expected"),
            timeline=ai_analysis.get('timeline', "1-2 weeks"),
            scenario_ids=scenario_ids,
            compliance_frameworks=compliance_frameworks,
            specific_steps=ai_analysis.get('specific_steps', [])
        )
    
    def _get_ai_remediation_analysis(self, group_name: str, scenarios: List[Dict], domain: str) -> Optional[Dict]:
        """Use AI to generate specific remediation analysis."""
        
        try:
            # Create detailed prompt for AI analysis
            prompt = f"""You are an MLOps specialist helping teams fix critical evaluation failures.

DOMAIN: {domain}
FAILURE GROUP: {group_name}
FAILED SCENARIOS: {len(scenarios)}

SCENARIO DETAILS:
{self._format_scenarios_for_ai(scenarios)}

Generate a specific remediation plan for an MLOps team with:

1. DESCRIPTION: Clear 1-sentence description of what failed
2. ACTION: Specific technical action (2-3 sentences max) 
3. EXPECTED_IMPROVEMENT: Quantified improvement expected
4. TIMELINE: Realistic implementation timeline
5. SPECIFIC_STEPS: List of 3-5 concrete implementation steps

Focus on actionable technical steps, not generic advice. Assume the reader is an experienced MLOps engineer.

Return JSON format:
{{
  "description": "Clear failure description",
  "action": "Specific technical action", 
  "expected_improvement": "Quantified improvement",
  "timeline": "Realistic timeline",
  "specific_steps": ["Step 1", "Step 2", "Step 3"]
}}"""

            # Use AgentJudge's API manager to get client and make call
            client, _ = self.agent_judge.api_manager.get_client()
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.1
            )
            
            # Parse JSON response
            import json
            content = response.content[0].text if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
        
        return None
    
    def _format_scenarios_for_ai(self, scenarios: List[Dict]) -> str:
        """Format scenarios for AI analysis."""
        formatted = []
        for s in scenarios:
            formatted.append(f"""
- ID: {s['id']}
- Name: {s['name']}  
- Severity: {s['severity']}
- Compliance: {', '.join(s['compliance'])}
- Recommendations: {', '.join(s.get('improvement_recommendations', []))}""")
        
        return '\n'.join(formatted)
    
    def _determine_priority_from_scenarios(self, scenarios: List[Dict]) -> str:
        """Determine priority based on scenario severities."""
        severities = [s.get('severity', 'medium').lower() for s in scenarios]
        
        if any(s == 'critical' for s in severities):
            return "CRITICAL"
        elif any(s == 'high' for s in severities):
            return "HIGH" 
        elif any(s == 'medium' for s in severities):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_fallback_action(self, group_name: str, scenarios: List[Dict]) -> ImprovementAction:
        """Generate fallback action when AI analysis fails."""
        
        scenario_ids = [s.get('scenario_id', '') for s in scenarios]
        compliance_frameworks = list(set([f for s in scenarios for f in s.get('compliance', [])]))
        
        return ImprovementAction(
            priority=self._determine_priority_from_scenarios(scenarios),
            area=group_name.replace('_', ' ').title(),
            description=f"Failed {len(scenarios)} scenario{'s' if len(scenarios) > 1 else ''} in {group_name.replace('_', ' ')}",
            action=self._generate_action_text(group_name, scenarios),
            expected_improvement="Improvement expected with targeted fixes",
            timeline="1-2 weeks",
            scenario_ids=scenario_ids,
            compliance_frameworks=compliance_frameworks,
            specific_steps=["Review failed scenarios", "Implement fixes", "Validate improvements"]
        )
    
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
    
    def _generate_next_steps(self, evaluation_id: str, domain: str) -> str:
        """Generate next steps instruction."""
        
        return f"""WHEN DONE → Re-run evaluation:
arc-eval --domain {domain} --input improved_outputs.json --baseline {evaluation_id}.json"""
    
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
            
            compliance_text = f" | **Compliance:** {', '.join(action.compliance_frameworks)}" if action.compliance_frameworks else ""
            
            md_content += f"""### {i}. {priority_indicator} {action.priority} - {action.area}

**Failure Pattern:** {action.description}

**Recommended Change:** {action.action}

**Expected Improvement:** {action.expected_improvement}

**Implementation Timeline:** {action.timeline}

**Affected Scenarios:** {', '.join(action.scenario_ids) if action.scenario_ids else 'Multiple scenarios'}{compliance_text}

**Implementation Steps:**
"""
            
            # Add specific steps if available
            if hasattr(action, 'specific_steps') and action.specific_steps:
                for step_idx, step in enumerate(action.specific_steps, 1):
                    md_content += f"{step_idx}. {step}\n"
            else:
                md_content += "1. Review failed scenarios and root causes\n2. Implement targeted fixes\n3. Validate improvements through testing\n"
            
            md_content += "\n---\n\n"
        
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