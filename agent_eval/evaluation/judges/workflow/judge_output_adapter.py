"""
JudgeOutputAdapter: UI compatibility layer for workflow judges.

This adapter converts judge outputs to UI data structures for dashboard compatibility.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from agent_eval.evaluation.reliability_validator import (
    ComprehensiveReliabilityAnalysis,
    FrameworkPerformanceAnalysis, 
    WorkflowReliabilityMetrics
)
from agent_eval.core.improvement_planner import ImprovementPlan, ImprovementAction


class JudgeOutputAdapter:
    """Converts judge outputs to UI data structures."""
    
    @staticmethod
    def debug_judge_to_reliability_analysis(
        judge_output: Dict[str, Any], 
        framework: Optional[str] = None,
        sample_size: int = 1
    ) -> ComprehensiveReliabilityAnalysis:
        """Convert DebugJudge output to ComprehensiveReliabilityAnalysis for UI compatibility."""
        
        # Extract judge analysis data
        confidence = judge_output.get("confidence", 0.8)
        reasoning = judge_output.get("reasoning", "Judge-based analysis completed")
        reward_signals = judge_output.get("reward_signals", {})
        improvements = judge_output.get("improvements", [])
        
        # Create framework performance analysis if framework detected
        framework_performance = None
        if framework:
            framework_performance = JudgeOutputAdapter._create_framework_performance_from_judge(
                framework, judge_output, sample_size
            )
        
        # Create workflow reliability metrics
        workflow_metrics = JudgeOutputAdapter._create_workflow_metrics_from_judge(judge_output)
        
        # Create tool call summary
        tool_call_summary = JudgeOutputAdapter._create_tool_call_summary_from_judge(judge_output)
        
        # Generate insights and next steps from judge output
        insights_summary = JudgeOutputAdapter._extract_insights_from_judge(judge_output)
        next_steps = JudgeOutputAdapter._extract_next_steps_from_judge(judge_output)
        
        return ComprehensiveReliabilityAnalysis(
            detected_framework=framework,
            framework_confidence=confidence,
            auto_detection_successful=framework is not None,
            framework_performance=framework_performance,
            workflow_metrics=workflow_metrics,
            tool_call_summary=tool_call_summary,
            validation_results=[],  # Populated from existing validation if available
            reliability_dashboard="Judge-Enhanced Analysis Available",
            insights_summary=insights_summary,
            next_steps=next_steps,
            cognitive_analysis=None,  # Can be populated from cognitive analysis
            reliability_prediction=None,  # Can be populated from prediction
            analysis_confidence=confidence,
            evidence_quality="high" if confidence > 0.8 else "medium",
            sample_size=sample_size
        )
    
    @staticmethod
    def improve_judge_to_improvement_plan(
        judge_output: Dict[str, Any],
        agent_id: str,
        domain: str
    ) -> ImprovementPlan:
        """Convert ImproveJudge output to ImprovementPlan for workflow compatibility."""
        
        reward_signals = judge_output.get("reward_signals", {})
        improvement_actions = reward_signals.get("improvement_actions", [])
        
        # Convert judge actions to ImprovementAction objects
        actions = []
        for action_data in improvement_actions:
            if isinstance(action_data, dict):
                actions.append(ImprovementAction(
                    priority=action_data.get("priority", "MEDIUM"),
                    area=action_data.get("area", "General"),
                    description=action_data.get("description", "Improvement action"),
                    action=action_data.get("action", "Implement improvement"),
                    expected_improvement=action_data.get("expected_improvement", "Moderate improvement expected"),
                    timeline=action_data.get("timeline", "1-2 weeks"),
                    scenario_ids=action_data.get("scenario_ids", []),
                    compliance_frameworks=action_data.get("compliance_frameworks", []),
                    specific_steps=action_data.get("specific_steps", [])
                ))
        
        # Create summary from judge output
        summary = {
            "expected_improvement": reward_signals.get("expected_improvement", 15),
            "priority_breakdown": reward_signals.get("priority_breakdown", {}),
            "total_actions": len(actions),
            "estimated_total_time": reward_signals.get("timeline", "2-4 weeks"),
            "success_metrics": reward_signals.get("success_metrics", []),
            "risk_assessment": reward_signals.get("risks", [])
        }
        
        # Extract next steps from improvements
        next_steps = "\n".join(judge_output.get("improvements", [
            "Review generated improvement plan",
            "Prioritize actions by business impact",
            "Implement high-priority actions first"
        ]))
        
        return ImprovementPlan(
            agent_id=agent_id,
            domain=domain,
            created_at=JudgeOutputAdapter._get_current_timestamp(),
            baseline_evaluation="judge_based_analysis",
            actions=actions,
            summary=summary,
            next_steps=next_steps
        )
    
    @staticmethod
    def _create_framework_performance_from_judge(
        framework: str, 
        judge_output: Dict[str, Any], 
        sample_size: int
    ) -> FrameworkPerformanceAnalysis:
        """Create FrameworkPerformanceAnalysis from judge output."""
        
        reward_signals = judge_output.get("reward_signals", {})
        confidence = judge_output.get("confidence", 0.8)
        
        # Extract performance metrics from judge analysis
        performance_issues = reward_signals.get("performance_issues", [])
        framework_issues = reward_signals.get("framework_issues", {})
        optimization_opportunities = reward_signals.get("optimization_opportunities", [])
        
        # Convert to FrameworkPerformanceAnalysis format
        performance_bottlenecks = []
        for issue in performance_issues[:5]:
            performance_bottlenecks.append({
                "type": "judge_identified_bottleneck",
                "description": str(issue),
                "severity": "medium",
                "evidence": "Identified by AI analysis"
            })
        
        optimization_ops = []
        for opportunity in optimization_opportunities[:5]:
            optimization_ops.append({
                "description": str(opportunity),
                "evidence": "AI-recommended optimization",
                "estimated_improvement": "Moderate improvement expected",
                "priority": "medium"
            })
        
        return FrameworkPerformanceAnalysis(
            framework_name=framework,
            sample_size=sample_size,
            avg_response_time=0.0,  # Not available from judge analysis
            success_rate=confidence,  # Use confidence as proxy
            tool_call_failure_rate=len(performance_issues) / 10.0,  # Rough estimate
            timeout_frequency=0.0,  # Not available from judge analysis
            abstraction_overhead=0.0,  # Not available from judge analysis
            delegation_bottlenecks=list(framework_issues.keys())[:3],
            memory_leak_indicators=[],  # Not available from judge analysis
            performance_bottlenecks=performance_bottlenecks,
            optimization_opportunities=optimization_ops,
            framework_alternatives=[],  # Could be populated from judge recommendations
            analysis_confidence=confidence,
            recommendation_strength="high" if confidence > 0.8 else "medium"
        )
    
    @staticmethod
    def _create_workflow_metrics_from_judge(judge_output: Dict[str, Any]) -> WorkflowReliabilityMetrics:
        """Create WorkflowReliabilityMetrics from judge output."""
        
        confidence = judge_output.get("confidence", 0.8)
        reward_signals = judge_output.get("reward_signals", {})
        
        # Map judge confidence to reliability metrics
        return WorkflowReliabilityMetrics(
            workflow_success_rate=confidence,
            tool_chain_reliability=confidence,
            decision_consistency_score=confidence,
            multi_step_completion_rate=confidence,
            average_workflow_time=0.0,  # Not available from judge
            error_recovery_rate=reward_signals.get("error_recovery_rate", 0.5),
            timeout_rate=0.0,  # Not available from judge
            framework_compatibility_score=confidence,
            tool_usage_efficiency=confidence,
            schema_mismatch_rate=0.0,  # Not available from judge
            prompt_tool_alignment_score=confidence,
            reliability_trend="improving" if confidence > 0.8 else "stable",
            critical_failure_points=reward_signals.get("failure_patterns", [])[:3]
        )
    
    @staticmethod
    def _create_tool_call_summary_from_judge(judge_output: Dict[str, Any]) -> Dict[str, Any]:
        """Create tool call summary from judge output."""
        
        reward_signals = judge_output.get("reward_signals", {})
        tool_failures = reward_signals.get("tool_failures", [])
        
        return {
            "total_tool_calls": len(tool_failures) + 5,  # Rough estimate
            "successful_calls": 5,  # Rough estimate
            "failed_calls": len(tool_failures),
            "failure_rate": len(tool_failures) / (len(tool_failures) + 5) if tool_failures else 0.0,
            "common_failures": tool_failures[:5],
            "judge_enhanced": True
        }
    
    @staticmethod
    def _extract_insights_from_judge(judge_output: Dict[str, Any]) -> List[str]:
        """Extract insights from judge output for dashboard display."""
        
        insights = []
        
        # Add primary reasoning as insight
        reasoning = judge_output.get("reasoning", "")
        if reasoning:
            insights.append(f"🧠 AI Analysis: {reasoning[:200]}...")
        
        # Add key patterns from reward signals
        reward_signals = judge_output.get("reward_signals", {})
        
        failure_patterns = reward_signals.get("failure_patterns", [])
        if failure_patterns:
            insights.append(f"⚠️ Failure Patterns: {len(failure_patterns)} patterns identified")
        
        success_patterns = reward_signals.get("success_patterns", [])
        if success_patterns:
            insights.append(f"✅ Success Patterns: {len(success_patterns)} effective patterns found")
        
        optimization_opportunities = reward_signals.get("optimization_opportunities", [])
        if optimization_opportunities:
            insights.append(f"🚀 Optimizations: {len(optimization_opportunities)} opportunities identified")
        
        return insights[:5]  # Limit to 5 insights
    
    @staticmethod
    def _extract_next_steps_from_judge(judge_output: Dict[str, Any]) -> List[str]:
        """Extract next steps from judge output."""
        
        # Start with judge improvements
        next_steps = judge_output.get("improvements", [])
        
        # Add judge-specific next steps
        judge_next_steps = [
            "Review AI-powered analysis insights",
            "Implement prioritized recommendations",
            "Monitor improvements and re-evaluate"
        ]
        
        # Combine and deduplicate
        all_steps = next_steps + judge_next_steps
        unique_steps = list(dict.fromkeys(all_steps))  # Preserve order, remove duplicates
        
        return unique_steps[:10]  # Limit to 10 steps
    
    @staticmethod
    def _get_current_timestamp() -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @staticmethod
    def enhance_dashboard_with_judge_reasoning(
        analysis: ComprehensiveReliabilityAnalysis, 
        judge_output: Dict[str, Any]
    ) -> ComprehensiveReliabilityAnalysis:
        """Enhance existing analysis with judge reasoning for display."""
        
        # Add judge reasoning to insights
        reasoning = judge_output.get("reasoning", "")
        if reasoning:
            enhanced_insights = [f"🧠 AI Reasoning: {reasoning}"] + analysis.insights_summary
            analysis.insights_summary = enhanced_insights[:10]
        
        # Add confidence information
        confidence = judge_output.get("confidence", 0.8)
        confidence_insight = f"🎯 AI Confidence: {confidence:.1%}"
        analysis.insights_summary.insert(0, confidence_insight)
        
        # Update evidence quality based on judge confidence
        if confidence > 0.9:
            analysis.evidence_quality = "high"
        elif confidence > 0.7:
            analysis.evidence_quality = "medium"
        else:
            analysis.evidence_quality = "low"
        
        return analysis