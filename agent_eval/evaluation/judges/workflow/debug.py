"""
DebugJudge: Root cause analysis and failure pattern identification.

This judge performs analysis for debugging agent workflows, tool call failures, and performance issues.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from agent_eval.core.types import AgentOutput, EvaluationScenario
from agent_eval.evaluation.judges.base import BaseJudge, JudgmentResult, ContinuousFeedback

logger = logging.getLogger(__name__)


class DebugJudge(BaseJudge):
    """Judge for debugging agent workflows and tool call failures."""
    
    def __init__(self, api_manager, enable_confidence_calibration: bool = False):
        super().__init__(api_manager, enable_confidence_calibration)
        self.domain = "debug"
        self.knowledge_base = [
            "Agent workflow failure patterns and root causes",
            "Framework-specific debugging methodologies (LangChain, CrewAI, AutoGen, etc.)",
            "Tool call failure analysis and remediation strategies",
            "Performance bottleneck identification and optimization",
            "Error recovery pattern assessment and improvement",
            "Cross-framework debugging best practices",
            "Reliability metrics interpretation and analysis"
        ]
    
    def evaluate(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> JudgmentResult:
        """Evaluate agent output for debugging insights."""
        prompt = self._build_prompt(agent_output, scenario)
        return self._execute_evaluation(prompt, scenario, self.api_manager.preferred_model)
    
    def evaluate_failure_patterns(self, agent_outputs: List[Any], framework: str) -> Dict[str, Any]:
        """Analyze failure patterns across multiple agent outputs.
        
        This method replaces the rule-based failure analysis methods in ReliabilityAnalyzer.
        """
        # Prepare scenario for batch analysis
        scenario = EvaluationScenario(
            id="debug_batch_analysis",
            name="Debug Batch Analysis",
            description="Comprehensive failure pattern analysis across multiple outputs",
            expected_behavior="Identify patterns, root causes, and actionable fixes",
            severity="high",
            test_type="negative",  # Use valid TestType enum value
            category="debug",
            input_template="Multiple agent outputs for pattern analysis",
            failure_indicators=["errors", "timeouts", "failures"],
            compliance=[],
            remediation="Apply recommended fixes from analysis"
        )
        
        # Convert outputs to AgentOutput format for analysis
        agent_output = AgentOutput(
            raw_output={"outputs": agent_outputs, "framework": framework},
            normalized_output=f"Batch analysis of {len(agent_outputs)} outputs from {framework}"
        )
        
        # Use judge evaluation
        result = self.evaluate(agent_output, scenario)
        
        # Convert to expected format for ReliabilityAnalyzer integration
        return {
            "failure_patterns": result.reward_signals.get("failure_patterns", []),
            "root_causes": result.reasoning,
            "recommended_actions": result.improvement_recommendations,
            "confidence": result.confidence,
            "framework_specific_issues": result.reward_signals.get("framework_issues", {}),
            "performance_bottlenecks": result.reward_signals.get("performance_issues", []),
            "tool_call_failures": result.reward_signals.get("tool_failures", [])
        }
    
    def analyze_cognitive_patterns(self, agent_reasoning: List[str]) -> Dict[str, Any]:
        """Analyze cognitive patterns in agent reasoning.
        
        Replaces rule-based methods like analyze_reflection_quality, _detect_circular_reasoning, etc.
        """
        scenario = EvaluationScenario(
            id="cognitive_analysis",
            name="Cognitive Pattern Analysis", 
            description="Analyze reasoning quality, metacognitive awareness, and cognitive patterns",
            expected_behavior="Identify cognitive strengths and weaknesses",
            severity="medium",
            test_type="positive",  # Use valid TestType enum value
            category="debug",
            input_template="Agent reasoning chains for cognitive analysis",
            failure_indicators=["circular_reasoning", "overconfidence", "poor_reflection"],
            compliance=[],
            remediation="Improve reasoning patterns based on analysis"
        )
        
        agent_output = AgentOutput(
            raw_output={"reasoning_chains": agent_reasoning},
            normalized_output=" ".join(agent_reasoning)
        )
        
        result = self.evaluate(agent_output, scenario)
        
        return {
            "cognitive_quality_score": result.confidence,
            "reasoning_coherence": result.reward_signals.get("reasoning_coherence", 0.5),
            "metacognitive_awareness": result.reward_signals.get("metacognitive_awareness", 0.5),
            "circular_reasoning_detected": result.reward_signals.get("circular_reasoning", False),
            "self_correction_capability": result.reward_signals.get("self_correction", 0.5),
            "overconfidence_indicators": result.reward_signals.get("overconfidence", False),
            "reflection_depth": result.reward_signals.get("reflection_depth", 0.5),
            "insights": result.improvement_recommendations
        }
    
    def _build_prompt(self, agent_output: AgentOutput, scenario: EvaluationScenario) -> str:
        """Build debug-specific evaluation prompt."""
        output_data = agent_output.raw_output if agent_output.raw_output else agent_output.normalized_output
        
        if scenario.id == "debug_batch_analysis":
            # Batch failure analysis prompt
            return self._build_batch_analysis_prompt(output_data)
        elif scenario.id == "cognitive_analysis":
            # Cognitive pattern analysis prompt
            return self._build_cognitive_analysis_prompt(output_data)
        else:
            # Standard debug analysis prompt
            return self._build_standard_debug_prompt(output_data, scenario)
    
    def _build_batch_analysis_prompt(self, output_data: Dict[str, Any]) -> str:
        """Build prompt for batch failure pattern analysis."""
        outputs = output_data.get("outputs", [])
        framework = output_data.get("framework", "unknown")
        
        return f"""You are an expert debugging analyst specializing in AI agent workflow failures.

TASK: Analyze {len(outputs)} agent outputs from {framework} framework to identify failure patterns, root causes, and actionable fixes.

AGENT OUTPUTS:
{self._format_outputs_for_analysis(outputs)}

ANALYSIS REQUIREMENTS:
1. **Failure Pattern Identification**: Identify recurring failure patterns across outputs
2. **Root Cause Analysis**: Determine underlying causes, not just symptoms
3. **Framework-Specific Issues**: Identify {framework}-specific problems and optimizations
4. **Performance Bottlenecks**: Detect performance issues and their causes
5. **Tool Call Analysis**: Analyze tool usage patterns and failures
6. **Actionable Recommendations**: Provide specific, implementable fixes

RESPONSE FORMAT (JSON):
{{
    "judgment": "pass|fail|warning",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed analysis of patterns and root causes",
    "improvements": ["Specific actionable recommendations"],
    "reward_signals": {{
        "failure_patterns": ["Pattern 1", "Pattern 2"],
        "framework_issues": {{"issue_type": "description"}},
        "performance_issues": ["Issue 1", "Issue 2"],
        "tool_failures": ["Failure 1", "Failure 2"],
        "success_patterns": ["What worked well"],
        "optimization_opportunities": ["Optimization 1", "Optimization 2"]
    }}
}}

Focus on providing intelligent, context-aware analysis that goes beyond simple pattern matching."""
    
    def _build_cognitive_analysis_prompt(self, output_data: Dict[str, Any]) -> str:
        """Build prompt for cognitive pattern analysis."""
        reasoning_chains = output_data.get("reasoning_chains", [])
        
        return f"""You are an expert cognitive analyst specializing in AI agent reasoning quality.

TASK: Analyze agent reasoning chains for cognitive patterns, metacognitive awareness, and reasoning quality.

REASONING CHAINS:
{self._format_reasoning_for_analysis(reasoning_chains)}

ANALYSIS REQUIREMENTS:
1. **Reasoning Coherence**: Evaluate logical flow and consistency
2. **Metacognitive Awareness**: Assess self-awareness and monitoring
3. **Circular Reasoning Detection**: Identify logical loops or redundancy
4. **Self-Correction Capability**: Evaluate error detection and correction
5. **Overconfidence Assessment**: Detect overconfident assertions without evidence
6. **Reflection Depth**: Measure depth of analysis and consideration

RESPONSE FORMAT (JSON):
{{
    "judgment": "pass|fail|warning",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed cognitive analysis",
    "improvements": ["Specific cognitive improvement recommendations"],
    "reward_signals": {{
        "reasoning_coherence": 0.0-1.0,
        "metacognitive_awareness": 0.0-1.0,
        "circular_reasoning": true|false,
        "self_correction": 0.0-1.0,
        "overconfidence": true|false,
        "reflection_depth": 0.0-1.0,
        "cognitive_strengths": ["Strength 1", "Strength 2"],
        "cognitive_weaknesses": ["Weakness 1", "Weakness 2"]
    }}
}}

Provide nuanced analysis that captures cognitive sophistication beyond simple pattern matching."""
    
    def _build_standard_debug_prompt(self, output_data: Any, scenario: EvaluationScenario) -> str:
        """Build prompt for standard debug analysis."""
        return f"""You are an expert debugging analyst for AI agent workflows.

SCENARIO: {scenario.name}
DESCRIPTION: {scenario.description}
EXPECTED BEHAVIOR: {scenario.expected_behavior}
SEVERITY: {scenario.severity}

AGENT OUTPUT TO DEBUG:
{str(output_data)[:2000]}

DEBUGGING ANALYSIS:
1. **Issue Identification**: What specific problems are present?
2. **Root Cause Analysis**: What are the underlying causes?
3. **Impact Assessment**: How severe are the issues?
4. **Remediation Strategy**: What specific steps should be taken?
5. **Prevention Measures**: How can similar issues be prevented?

RESPONSE FORMAT (JSON):
{{
    "judgment": "pass|fail|warning",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed debugging analysis",
    "improvements": ["Specific actionable fixes"],
    "reward_signals": {{
        "issue_severity": 0.0-1.0,
        "fix_complexity": "low|medium|high",
        "prevention_feasibility": 0.0-1.0,
        "business_impact": 0.0-1.0
    }}
}}

Provide specific, actionable debugging guidance."""
    
    def _format_outputs_for_analysis(self, outputs: List[Any]) -> str:
        """Format outputs for batch analysis."""
        formatted = []
        for i, output in enumerate(outputs[:10]):  # Limit to first 10 for prompt size
            formatted.append(f"OUTPUT {i+1}:\n{str(output)[:500]}...")
        return "\n\n".join(formatted)
    
    def _format_reasoning_for_analysis(self, reasoning_chains: List[str]) -> str:
        """Format reasoning chains for cognitive analysis."""
        formatted = []
        for i, reasoning in enumerate(reasoning_chains[:5]):  # Limit to first 5
            formatted.append(f"REASONING CHAIN {i+1}:\n{reasoning[:800]}...")
        return "\n\n".join(formatted)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse DebugJudge response into structured judgment data."""
        # Use parent class JSON parsing with debug-specific defaults
        default_reward_signals = {
            "failure_patterns": [],
            "framework_issues": {},
            "performance_issues": [],
            "tool_failures": [],
            "success_patterns": [],
            "optimization_opportunities": []
        }
        
        default_improvements = [
            "Review identified failure patterns",
            "Implement recommended optimizations",
            "Add monitoring for detected issues"
        ]
        
        from agent_eval.evaluation.judges.base import _parse_json_response
        return _parse_json_response(response_text, default_reward_signals, default_improvements)
    
    def analyze_migration_opportunities(
        self, 
        current_framework: str, 
        performance_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze opportunities for framework migration using AI-powered analysis.
        
        This replaces the rule-based migration analysis in ReliabilityValidator.
        """
        scenario = EvaluationScenario(
            id="migration_analysis",
            name="Framework Migration Analysis",
            description="Analyze if migrating to a different framework would improve performance",
            expected_behavior="Identify migration opportunities with cost-benefit analysis",
            severity="medium",
            test_type="positive",
            category="debug",
            input_template="Current framework performance metrics for migration analysis",
            failure_indicators=[],
            compliance=[],
            remediation="Consider framework migration based on analysis"
        )
        
        agent_output = AgentOutput(
            raw_output={
                "current_framework": current_framework,
                "performance_metrics": performance_metrics
            },
            normalized_output=f"Migration analysis for {current_framework}"
        )
        
        result = self.evaluate(agent_output, scenario)
        
        return {
            "migration_recommended": result.judgment == "fail",  # "fail" means current framework is suboptimal
            "recommended_framework": result.reward_signals.get("recommended_framework"),
            "improvement_estimate": result.reward_signals.get("improvement_estimate", 0),
            "migration_priority": result.reward_signals.get("priority", "low"),
            "migration_steps": result.improvement_recommendations,
            "reasoning": result.reasoning,
            "confidence": result.confidence
        }
    
    def generate_continuous_feedback(self, results: List[JudgmentResult]) -> ContinuousFeedback:
        """Generate continuous feedback for debugging improvements."""
        if not results:
            return ContinuousFeedback([], [], [], [], [])
        
        # Aggregate insights from all results
        all_patterns = []
        all_issues = []
        all_improvements = []
        all_strengths = []
        
        for result in results:
            all_patterns.extend(result.reward_signals.get("failure_patterns", []))
            all_issues.extend(result.reward_signals.get("performance_issues", []))
            all_improvements.extend(result.improvement_recommendations)
            all_strengths.extend(result.reward_signals.get("success_patterns", []))
        
        # Remove duplicates and prioritize
        unique_patterns = list(set(all_patterns))
        unique_issues = list(set(all_issues))
        unique_improvements = list(set(all_improvements))
        unique_strengths = list(set(all_strengths))
        
        return ContinuousFeedback(
            strengths=unique_strengths[:5],
            weaknesses=unique_patterns[:5],
            specific_improvements=unique_improvements[:10],
            training_suggestions=[
                "Focus on failure pattern recognition",
                "Improve error handling mechanisms",
                "Enhance tool call validation"
            ],
            compliance_gaps=unique_issues[:5]
        )