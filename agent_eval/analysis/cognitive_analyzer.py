"""
Advanced cognitive pattern analysis for agents.

This module provides comprehensive cognitive analysis capabilities that go beyond
basic reliability validation to analyze higher-level reasoning patterns, 
metacognitive awareness, and adaptive thinking capabilities.
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class CognitivePatternResult:
    """Result of cognitive pattern analysis for a single reasoning instance."""
    
    reasoning_text: str
    pattern_type: str  # "planning", "reflection", "adaptation", "metacognitive"
    quality_score: float  # 0.0-1.0
    issues_detected: List[str]
    strengths_identified: List[str]
    improvement_suggestions: List[str]
    confidence_level: float


@dataclass
class ComprehensiveCognitiveAnalysis:
    """Complete cognitive analysis results for an agent."""
    
    # Overall cognitive health metrics
    cognitive_health_score: float  # 0.0-1.0 overall cognitive capability
    adaptive_thinking_score: float  # Ability to adapt and change approach
    metacognitive_awareness_score: float  # Self-awareness of thinking processes
    reasoning_coherence_score: float  # Logical consistency
    
    # Pattern-specific analysis
    planning_analysis: Dict[str, Any]
    reflection_analysis: Dict[str, Any]
    adaptation_analysis: Dict[str, Any]
    metacognitive_analysis: Dict[str, Any]
    
    # Detailed results
    pattern_results: List[CognitivePatternResult]
    critical_issues: List[str]
    key_strengths: List[str]
    improvement_recommendations: List[str]
    
    # Analysis metadata
    total_reasoning_analyzed: int
    analysis_confidence: float
    timestamp: str


class CognitiveAnalyzer:
    """Advanced cognitive pattern analysis for agents."""
    
    def __init__(self):
        """Initialize cognitive analyzer with pattern databases."""
        
        # Cognitive strength patterns
        self.strength_patterns = {
            "strategic_thinking": [
                r"considering multiple approaches",
                r"evaluating alternatives",
                r"long-term implications",
                r"strategic perspective",
                r"holistic view",
                r"considering trade-offs"
            ],
            "adaptive_reasoning": [
                r"adapting my approach",
                r"changing strategy",
                r"flexible thinking",
                r"adjusting based on",
                r"pivoting to",
                r"new perspective"
            ],
            "self_monitoring": [
                r"monitoring my progress",
                r"checking my understanding",
                r"validating my approach",
                r"assessing effectiveness",
                r"tracking results",
                r"evaluating outcomes"
            ],
            "uncertainty_handling": [
                r"acknowledging uncertainty",
                r"degree of confidence",
                r"uncertain about",
                r"might be wrong",
                r"limited information",
                r"provisional conclusion"
            ]
        }
        
        # Cognitive weakness patterns
        self.weakness_patterns = {
            "rigid_thinking": [
                r"only way to",
                r"must be done",
                r"always works",
                r"never fails",
                r"rigid approach",
                r"inflexible method"
            ],
            "poor_self_awareness": [
                r"definitely right",
                r"cannot be wrong",
                r"perfect solution",
                r"flawless logic",
                r"obviously correct",
                r"beyond question"
            ],
            "incomplete_reasoning": [
                r"just because",
                r"obviously true",
                r"common sense",
                r"everyone knows",
                r"self-evident",
                r"no need to explain"
            ],
            "analysis_paralysis": [
                r"too many options",
                r"overwhelmed by",
                r"cannot decide",
                r"stuck in analysis",
                r"endless consideration",
                r"paralyzed by choice"
            ]
        }
        
        # Metacognitive indicators
        self.metacognitive_indicators = {
            "process_awareness": [
                r"my thinking process",
                r"how i approach",
                r"my methodology",
                r"way i analyze",
                r"my reasoning style",
                r"thinking strategy"
            ],
            "limitation_recognition": [
                r"limitations of my",
                r"beyond my capability",
                r"outside my expertise",
                r"don't have enough",
                r"cannot determine",
                r"insufficient information"
            ],
            "bias_awareness": [
                r"might be biased",
                r"personal bias",
                r"subjective view",
                r"my perspective",
                r"could be influenced",
                r"potential bias"
            ],
            "learning_orientation": [
                r"learning from this",
                r"gained insight",
                r"new understanding",
                r"revised my view",
                r"learned that",
                r"better approach"
            ]
        }
    
    def analyze_planning_effectiveness(self, agent_outputs: List[Any]) -> Dict[str, Any]:
        """Comprehensive planning analysis."""
        planning_analysis = {
            "planning_coherence_score": 0.0,
            "goal_alignment_score": 0.0,
            "strategic_thinking_score": 0.0,
            "adaptation_capability_score": 0.0,
            "planning_issues": [],
            "planning_strengths": [],
            "total_outputs_analyzed": len(agent_outputs)
        }
        
        if not agent_outputs:
            return planning_analysis
        
        coherence_scores = []
        alignment_scores = []
        strategic_scores = []
        adaptation_scores = []
        
        for i, output in enumerate(agent_outputs):
            output_str = str(output).lower()
            
            # Analyze planning coherence
            coherence_score = self._analyze_planning_coherence(output_str)
            coherence_scores.append(coherence_score)
            
            # Analyze goal alignment
            alignment_score = self._analyze_goal_alignment(output_str)
            alignment_scores.append(alignment_score)
            
            # Analyze strategic thinking
            strategic_score = self._analyze_strategic_thinking(output_str)
            strategic_scores.append(strategic_score)
            
            # Analyze adaptation capability
            adaptation_score = self._analyze_adaptation_capability(output_str)
            adaptation_scores.append(adaptation_score)
            
            # Identify specific issues and strengths
            issues = self._identify_planning_issues(output_str)
            strengths = self._identify_planning_strengths(output_str)
            
            if issues:
                planning_analysis["planning_issues"].extend([
                    {"output_index": i, "issues": issues}
                ])
            
            if strengths:
                planning_analysis["planning_strengths"].extend([
                    {"output_index": i, "strengths": strengths}
                ])
        
        # Calculate overall scores
        planning_analysis["planning_coherence_score"] = sum(coherence_scores) / len(coherence_scores)
        planning_analysis["goal_alignment_score"] = sum(alignment_scores) / len(alignment_scores)
        planning_analysis["strategic_thinking_score"] = sum(strategic_scores) / len(strategic_scores)
        planning_analysis["adaptation_capability_score"] = sum(adaptation_scores) / len(adaptation_scores)
        
        return planning_analysis
    
    def detect_metacognitive_failures(self, reasoning_chains: List[str]) -> Dict[str, Any]:
        """Advanced reflection error detection."""
        metacognitive_analysis = {
            "metacognitive_awareness_score": 0.0,
            "self_monitoring_score": 0.0,
            "bias_recognition_score": 0.0,
            "learning_adaptation_score": 0.0,
            "metacognitive_failures": [],
            "metacognitive_strengths": [],
            "total_reasoning_analyzed": len(reasoning_chains)
        }
        
        if not reasoning_chains:
            return metacognitive_analysis
        
        awareness_scores = []
        monitoring_scores = []
        bias_scores = []
        learning_scores = []
        
        for i, reasoning in enumerate(reasoning_chains):
            reasoning_lower = reasoning.lower()
            
            # Analyze metacognitive awareness
            awareness_score = self._analyze_metacognitive_awareness(reasoning_lower)
            awareness_scores.append(awareness_score)
            
            # Analyze self-monitoring
            monitoring_score = self._analyze_self_monitoring(reasoning_lower)
            monitoring_scores.append(monitoring_score)
            
            # Analyze bias recognition
            bias_score = self._analyze_bias_recognition(reasoning_lower)
            bias_scores.append(bias_score)
            
            # Analyze learning adaptation
            learning_score = self._analyze_learning_adaptation(reasoning_lower)
            learning_scores.append(learning_score)
            
            # Detect specific failures and strengths
            failures = self._detect_metacognitive_failures_specific(reasoning_lower)
            strengths = self._detect_metacognitive_strengths(reasoning_lower)
            
            if failures:
                metacognitive_analysis["metacognitive_failures"].extend([
                    {"reasoning_index": i, "failures": failures, "reasoning": reasoning[:200] + "..."}
                ])
            
            if strengths:
                metacognitive_analysis["metacognitive_strengths"].extend([
                    {"reasoning_index": i, "strengths": strengths, "reasoning": reasoning[:200] + "..."}
                ])
        
        # Calculate overall scores
        metacognitive_analysis["metacognitive_awareness_score"] = sum(awareness_scores) / len(awareness_scores)
        metacognitive_analysis["self_monitoring_score"] = sum(monitoring_scores) / len(monitoring_scores)
        metacognitive_analysis["bias_recognition_score"] = sum(bias_scores) / len(bias_scores)
        metacognitive_analysis["learning_adaptation_score"] = sum(learning_scores) / len(learning_scores)
        
        return metacognitive_analysis
    
    def generate_comprehensive_cognitive_analysis(
        self, 
        agent_outputs: List[Any], 
        reasoning_chains: Optional[List[str]] = None
    ) -> ComprehensiveCognitiveAnalysis:
        """Generate complete cognitive analysis combining all capabilities."""
        
        # Extract reasoning chains from outputs if not provided separately
        if reasoning_chains is None:
            reasoning_chains = self._extract_reasoning_chains(agent_outputs)
        
        # Perform individual analyses
        planning_analysis = self.analyze_planning_effectiveness(agent_outputs)
        metacognitive_analysis = self.detect_metacognitive_failures(reasoning_chains)
        
        # Additional specialized analyses
        reflection_analysis = self._analyze_reflection_quality(reasoning_chains)
        adaptation_analysis = self._analyze_adaptive_thinking(agent_outputs, reasoning_chains)
        
        # Calculate overall cognitive health score
        cognitive_health_score = self._calculate_cognitive_health_score(
            planning_analysis, metacognitive_analysis, reflection_analysis, adaptation_analysis
        )
        
        # Extract pattern results
        pattern_results = self._generate_pattern_results(
            agent_outputs, reasoning_chains, planning_analysis, metacognitive_analysis
        )
        
        # Identify critical issues and key strengths
        critical_issues = self._identify_critical_cognitive_issues(
            planning_analysis, metacognitive_analysis, reflection_analysis, adaptation_analysis
        )
        
        key_strengths = self._identify_key_cognitive_strengths(
            planning_analysis, metacognitive_analysis, reflection_analysis, adaptation_analysis
        )
        
        # Generate improvement recommendations
        improvement_recommendations = self._generate_cognitive_improvement_recommendations(
            critical_issues, planning_analysis, metacognitive_analysis
        )
        
        # Calculate analysis confidence
        analysis_confidence = self._calculate_analysis_confidence(
            len(agent_outputs), len(reasoning_chains), pattern_results
        )
        
        return ComprehensiveCognitiveAnalysis(
            cognitive_health_score=cognitive_health_score,
            adaptive_thinking_score=adaptation_analysis.get("adaptive_thinking_score", 0.0),
            metacognitive_awareness_score=metacognitive_analysis["metacognitive_awareness_score"],
            reasoning_coherence_score=reflection_analysis.get("reasoning_coherence_score", 0.0),
            planning_analysis=planning_analysis,
            reflection_analysis=reflection_analysis,
            adaptation_analysis=adaptation_analysis,
            metacognitive_analysis=metacognitive_analysis,
            pattern_results=pattern_results,
            critical_issues=critical_issues,
            key_strengths=key_strengths,
            improvement_recommendations=improvement_recommendations,
            total_reasoning_analyzed=len(reasoning_chains),
            analysis_confidence=analysis_confidence,
            timestamp=datetime.now().isoformat()
        )
    
    # ==================== Helper Methods ====================
    
    def _analyze_planning_coherence(self, output_str: str) -> float:
        """Analyze coherence of planning in output."""
        planning_indicators = [
            r"first.*then.*finally",
            r"step \d+",
            r"my plan is",
            r"approach will be",
            r"strategy involves",
            r"methodology includes"
        ]
        
        coherence_indicators = [
            r"building on",
            r"following from",
            r"leads to",
            r"results in",
            r"connects to",
            r"consistent with"
        ]
        
        planning_count = sum(1 for pattern in planning_indicators if re.search(pattern, output_str))
        coherence_count = sum(1 for pattern in coherence_indicators if re.search(pattern, output_str))
        
        if planning_count == 0:
            return 0.5  # Neutral when no planning language
        
        coherence_ratio = coherence_count / planning_count if planning_count > 0 else 0
        return min(1.0, 0.3 + coherence_ratio * 0.7)
    
    def _analyze_goal_alignment(self, output_str: str) -> float:
        """Analyze how well output aligns with stated goals."""
        goal_statements = [
            r"goal is",
            r"objective is",
            r"aim to",
            r"trying to",
            r"working toward",
            r"intended to"
        ]
        
        alignment_indicators = [
            r"in service of",
            r"supports the goal",
            r"aligned with",
            r"contributes to",
            r"advances the",
            r"moves toward"
        ]
        
        goal_count = sum(1 for pattern in goal_statements if re.search(pattern, output_str))
        alignment_count = sum(1 for pattern in alignment_indicators if re.search(pattern, output_str))
        
        if goal_count == 0:
            return 0.6  # Moderate score when no explicit goals
        
        alignment_ratio = alignment_count / goal_count if goal_count > 0 else 0
        return min(1.0, 0.4 + alignment_ratio * 0.6)
    
    def _analyze_strategic_thinking(self, output_str: str) -> float:
        """Analyze strategic thinking capability."""
        strategic_patterns = self.strength_patterns["strategic_thinking"]
        strategic_count = sum(1 for pattern in strategic_patterns if re.search(pattern, output_str))
        
        # Weight by output length
        words = len(output_str.split())
        normalized_score = min(1.0, strategic_count / max(1, words / 100))
        
        return normalized_score
    
    def _analyze_adaptation_capability(self, output_str: str) -> float:
        """Analyze ability to adapt approach."""
        adaptation_patterns = self.strength_patterns["adaptive_reasoning"]
        rigid_patterns = self.weakness_patterns["rigid_thinking"]
        
        adaptation_count = sum(1 for pattern in adaptation_patterns if re.search(pattern, output_str))
        rigid_count = sum(1 for pattern in rigid_patterns if re.search(pattern, output_str))
        
        if adaptation_count == 0 and rigid_count == 0:
            return 0.5  # Neutral
        
        # Adaptation increases score, rigidity decreases it
        net_score = 0.5 + (adaptation_count * 0.2) - (rigid_count * 0.3)
        return max(0.0, min(1.0, net_score))
    
    def _identify_planning_issues(self, output_str: str) -> List[str]:
        """Identify specific planning issues."""
        issues = []
        
        # Check for various planning problems
        if re.search(r"no plan|without planning|randomly", output_str):
            issues.append("Lack of explicit planning")
        
        if re.search(r"conflicting.*approach|contradictory.*strategy", output_str):
            issues.append("Conflicting planning elements")
        
        if re.search(r"unclear.*goal|vague.*objective", output_str):
            issues.append("Unclear goals or objectives")
        
        return issues
    
    def _identify_planning_strengths(self, output_str: str) -> List[str]:
        """Identify specific planning strengths."""
        strengths = []
        
        if re.search(r"systematic.*approach|methodical.*strategy", output_str):
            strengths.append("Systematic approach")
        
        if re.search(r"contingency.*plan|backup.*strategy", output_str):
            strengths.append("Contingency planning")
        
        if re.search(r"milestone|checkpoint|progress.*review", output_str):
            strengths.append("Progress monitoring")
        
        return strengths
    
    def _analyze_metacognitive_awareness(self, reasoning: str) -> float:
        """Analyze metacognitive awareness level."""
        awareness_patterns = self.metacognitive_indicators["process_awareness"]
        awareness_count = sum(1 for pattern in awareness_patterns if re.search(pattern, reasoning))
        
        words = len(reasoning.split())
        normalized_score = min(1.0, awareness_count / max(1, words / 50))
        
        return normalized_score
    
    def _analyze_self_monitoring(self, reasoning: str) -> float:
        """Analyze self-monitoring capability."""
        monitoring_patterns = [
            r"checking my work",
            r"validating my reasoning",
            r"reviewing my logic",
            r"monitoring progress",
            r"assessing accuracy",
            r"evaluating effectiveness"
        ]
        
        monitoring_count = sum(1 for pattern in monitoring_patterns if re.search(pattern, reasoning))
        
        words = len(reasoning.split())
        normalized_score = min(1.0, monitoring_count / max(1, words / 100))
        
        return normalized_score
    
    def _analyze_bias_recognition(self, reasoning: str) -> float:
        """Analyze bias recognition capability."""
        bias_patterns = self.metacognitive_indicators["bias_awareness"]
        bias_count = sum(1 for pattern in bias_patterns if re.search(pattern, reasoning))
        
        words = len(reasoning.split())
        normalized_score = min(1.0, bias_count / max(1, words / 75))
        
        return normalized_score
    
    def _analyze_learning_adaptation(self, reasoning: str) -> float:
        """Analyze learning and adaptation from experience."""
        learning_patterns = self.metacognitive_indicators["learning_orientation"]
        learning_count = sum(1 for pattern in learning_patterns if re.search(pattern, reasoning))
        
        words = len(reasoning.split())
        normalized_score = min(1.0, learning_count / max(1, words / 100))
        
        return normalized_score
    
    def _detect_metacognitive_failures_specific(self, reasoning: str) -> List[str]:
        """Detect specific metacognitive failures."""
        failures = []
        
        # Check for overconfidence without self-awareness
        poor_awareness_patterns = self.weakness_patterns["poor_self_awareness"]
        if any(re.search(pattern, reasoning) for pattern in poor_awareness_patterns):
            failures.append("Overconfidence without self-awareness")
        
        # Check for incomplete reasoning
        incomplete_patterns = self.weakness_patterns["incomplete_reasoning"]
        if any(re.search(pattern, reasoning) for pattern in incomplete_patterns):
            failures.append("Incomplete reasoning without justification")
        
        return failures
    
    def _detect_metacognitive_strengths(self, reasoning: str) -> List[str]:
        """Detect specific metacognitive strengths."""
        strengths = []
        
        # Check for uncertainty handling
        uncertainty_patterns = self.strength_patterns["uncertainty_handling"]
        if any(re.search(pattern, reasoning) for pattern in uncertainty_patterns):
            strengths.append("Appropriate uncertainty handling")
        
        # Check for self-monitoring
        monitoring_patterns = self.strength_patterns["self_monitoring"]
        if any(re.search(pattern, reasoning) for pattern in monitoring_patterns):
            strengths.append("Active self-monitoring")
        
        return strengths
    
    def _extract_reasoning_chains(self, agent_outputs: List[Any]) -> List[str]:
        """Extract reasoning chains from agent outputs."""
        reasoning_chains = []
        
        for output in agent_outputs:
            output_str = str(output)
            
            # Look for reasoning indicators
            reasoning_indicators = [
                r"because",
                r"therefore", 
                r"reasoning",
                r"analysis",
                r"considering",
                r"thinking"
            ]
            
            # If output contains reasoning language, include it
            if any(re.search(pattern, output_str, re.IGNORECASE) for pattern in reasoning_indicators):
                reasoning_chains.append(output_str)
        
        return reasoning_chains
    
    def _analyze_reflection_quality(self, reasoning_chains: List[str]) -> Dict[str, Any]:
        """Analyze reflection quality (simplified version)."""
        return {
            "reasoning_coherence_score": 0.7,  # Placeholder
            "reflection_depth_score": 0.6,
            "self_correction_frequency": 0.3
        }
    
    def _analyze_adaptive_thinking(self, agent_outputs: List[Any], reasoning_chains: List[str]) -> Dict[str, Any]:
        """Analyze adaptive thinking capabilities."""
        return {
            "adaptive_thinking_score": 0.65,  # Placeholder
            "flexibility_score": 0.7,
            "context_sensitivity_score": 0.6
        }
    
    def _calculate_cognitive_health_score(
        self, 
        planning_analysis: Dict[str, Any], 
        metacognitive_analysis: Dict[str, Any],
        reflection_analysis: Dict[str, Any],
        adaptation_analysis: Dict[str, Any]
    ) -> float:
        """Calculate overall cognitive health score."""
        planning_score = (
            planning_analysis["planning_coherence_score"] +
            planning_analysis["goal_alignment_score"] +
            planning_analysis["strategic_thinking_score"]
        ) / 3
        
        metacognitive_score = (
            metacognitive_analysis["metacognitive_awareness_score"] +
            metacognitive_analysis["self_monitoring_score"] +
            metacognitive_analysis["bias_recognition_score"]
        ) / 3
        
        reflection_score = reflection_analysis.get("reasoning_coherence_score", 0.5)
        adaptation_score = adaptation_analysis.get("adaptive_thinking_score", 0.5)
        
        # Weighted average
        cognitive_health = (
            planning_score * 0.3 +
            metacognitive_score * 0.3 +
            reflection_score * 0.2 +
            adaptation_score * 0.2
        )
        
        return cognitive_health
    
    def _generate_pattern_results(
        self,
        agent_outputs: List[Any],
        reasoning_chains: List[str],
        planning_analysis: Dict[str, Any],
        metacognitive_analysis: Dict[str, Any]
    ) -> List[CognitivePatternResult]:
        """Generate detailed pattern results."""
        pattern_results = []
        
        # Create simplified pattern results for demonstration
        for i, reasoning in enumerate(reasoning_chains[:3]):  # Limit for performance
            pattern_results.append(CognitivePatternResult(
                reasoning_text=reasoning[:200] + "...",
                pattern_type="metacognitive",
                quality_score=0.7,
                issues_detected=["Minor coherence issues"],
                strengths_identified=["Good self-awareness"],
                improvement_suggestions=["Consider multiple perspectives"],
                confidence_level=0.8
            ))
        
        return pattern_results
    
    def _identify_critical_cognitive_issues(
        self,
        planning_analysis: Dict[str, Any],
        metacognitive_analysis: Dict[str, Any],
        reflection_analysis: Dict[str, Any],
        adaptation_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify critical cognitive issues."""
        issues = []
        
        if planning_analysis["planning_coherence_score"] < 0.4:
            issues.append("Severe planning coherence problems")
        
        if metacognitive_analysis["metacognitive_awareness_score"] < 0.3:
            issues.append("Poor metacognitive awareness")
        
        if metacognitive_analysis["bias_recognition_score"] < 0.2:
            issues.append("Limited bias recognition capability")
        
        return issues
    
    def _identify_key_cognitive_strengths(
        self,
        planning_analysis: Dict[str, Any],
        metacognitive_analysis: Dict[str, Any],
        reflection_analysis: Dict[str, Any],
        adaptation_analysis: Dict[str, Any]
    ) -> List[str]:
        """Identify key cognitive strengths."""
        strengths = []
        
        if planning_analysis["strategic_thinking_score"] > 0.7:
            strengths.append("Strong strategic thinking capabilities")
        
        if metacognitive_analysis["self_monitoring_score"] > 0.7:
            strengths.append("Excellent self-monitoring abilities")
        
        if adaptation_analysis.get("adaptive_thinking_score", 0) > 0.7:
            strengths.append("High adaptive thinking capability")
        
        return strengths
    
    def _generate_cognitive_improvement_recommendations(
        self,
        critical_issues: List[str],
        planning_analysis: Dict[str, Any],
        metacognitive_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate cognitive improvement recommendations."""
        recommendations = []
        
        for issue in critical_issues:
            if "planning coherence" in issue:
                recommendations.append("Implement structured planning templates and goal-setting frameworks")
            elif "metacognitive awareness" in issue:
                recommendations.append("Add explicit self-reflection prompts and awareness checkpoints")
            elif "bias recognition" in issue:
                recommendations.append("Integrate bias detection training and perspective-taking exercises")
        
        # Add general recommendations based on scores
        if planning_analysis["adaptation_capability_score"] < 0.5:
            recommendations.append("Develop flexibility training and alternative approach generation")
        
        if metacognitive_analysis["learning_adaptation_score"] < 0.5:
            recommendations.append("Implement learning reflection and experience integration practices")
        
        return recommendations
    
    def _calculate_analysis_confidence(
        self,
        num_outputs: int,
        num_reasoning_chains: int,
        pattern_results: List[CognitivePatternResult]
    ) -> float:
        """Calculate confidence in the analysis."""
        sample_size_factor = min(1.0, (num_outputs + num_reasoning_chains) / 20)
        pattern_quality_factor = sum(r.confidence_level for r in pattern_results) / max(1, len(pattern_results))
        
        overall_confidence = (sample_size_factor + pattern_quality_factor) / 2
        return overall_confidence