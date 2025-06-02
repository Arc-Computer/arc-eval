"""
Universal Failure Classification System for ARC-Eval.

This module provides framework-agnostic failure pattern detection and classification,
enabling cross-framework learning and universal optimization insights.

Key Features:
- Universal failure taxonomy mapping
- Framework-agnostic pattern detection
- Cross-framework correlation analysis
- Business impact assessment
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
from datetime import datetime

from agent_eval.core.parser_registry import FrameworkDetector, OutputExtractor, ToolCallExtractor
from agent_eval.core.framework_patterns import FrameworkPatterns

logger = logging.getLogger(__name__)


@dataclass
class FailurePattern:
    """Represents a universal failure pattern."""
    pattern_type: str
    subtype: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    framework: Optional[str]
    description: str
    indicators: List[str]
    business_impact: str
    confidence: float


@dataclass
class ClassificationResult:
    """Result of universal failure classification."""
    universal_patterns: List[FailurePattern]
    framework_specific_issues: Dict[str, List[str]]
    cross_framework_insights: List[str]
    business_impact_score: float
    remediation_priority: List[str]


# Universal Failure Taxonomy - Framework Agnostic
UNIVERSAL_FAILURE_PATTERNS = {
    "tool_failures": {
        "api_timeout": {
            "indicators": ["timeout", "connection", "request failed", "network error", "502", "503", "504"],
            "severity": "high",
            "business_impact": "Service disruption, user experience degradation",
            "description": "External API calls failing due to timeouts or connectivity issues"
        },
        "missing_tool": {
            "indicators": ["tool not found", "function not available", "unknown tool", "missing function"],
            "severity": "critical", 
            "business_impact": "Complete workflow failure, blocked operations",
            "description": "Required tools or functions not available to the agent"
        },
        "incorrect_usage": {
            "indicators": ["invalid parameters", "wrong format", "parameter error", "schema validation"],
            "severity": "medium",
            "business_impact": "Reduced accuracy, potential data corruption",
            "description": "Tools called with incorrect parameters or format"
        },
        "permission_denied": {
            "indicators": ["permission denied", "unauthorized", "access denied", "403", "401"],
            "severity": "high",
            "business_impact": "Security compliance risk, blocked operations",
            "description": "Insufficient permissions to access required resources"
        }
    },
    "planning_failures": {
        "goal_setting": {
            "indicators": ["unclear objective", "ambiguous goal", "conflicting instructions", "no clear target"],
            "severity": "high",
            "business_impact": "Inefficient resource usage, poor outcomes",
            "description": "Agent unable to establish clear, achievable goals"
        },
        "reflection_errors": {
            "indicators": ["no self-correction", "repeated mistakes", "ignoring feedback", "no learning"],
            "severity": "medium",
            "business_impact": "Degraded performance over time, missed improvements",
            "description": "Agent fails to learn from mistakes or incorporate feedback"
        },
        "coordination": {
            "indicators": ["agent conflict", "duplicate work", "communication failure", "sync issues"],
            "severity": "high",
            "business_impact": "Resource waste, inconsistent results",
            "description": "Multi-agent coordination and communication failures"
        },
        "infinite_loops": {
            "indicators": ["stuck in loop", "repeated actions", "no progress", "circular reasoning"],
            "severity": "critical",
            "business_impact": "System resource exhaustion, complete failure",
            "description": "Agent trapped in repetitive behavior patterns"
        }
    },
    "efficiency_issues": {
        "excessive_steps": {
            "indicators": ["too many steps", "inefficient path", "redundant actions", "over-processing"],
            "severity": "medium",
            "business_impact": "Increased costs, slower response times",
            "description": "Agent taking unnecessarily complex paths to solutions"
        },
        "costly_operations": {
            "indicators": ["expensive model", "high token usage", "resource intensive", "cost spike"],
            "severity": "high",
            "business_impact": "Budget overruns, unsustainable operations",
            "description": "Operations consuming excessive computational or financial resources"
        },
        "delays": {
            "indicators": ["slow response", "timeout", "processing delay", "queue backup"],
            "severity": "medium",
            "business_impact": "Poor user experience, SLA violations",
            "description": "Unacceptable delays in agent response or processing"
        },
        "redundant_calls": {
            "indicators": ["duplicate requests", "repeated calls", "unnecessary API usage", "cache miss"],
            "severity": "low",
            "business_impact": "Increased costs, API rate limiting",
            "description": "Unnecessary repetition of expensive operations"
        }
    },
    "output_quality": {
        "incorrect_outputs": {
            "indicators": ["wrong answer", "factual error", "logic error", "calculation mistake"],
            "severity": "critical",
            "business_impact": "Business decisions based on wrong data, compliance violations",
            "description": "Agent producing factually incorrect or logically flawed outputs"
        },
        "translation_errors": {
            "indicators": ["mistranslation", "language error", "cultural insensitivity", "context loss"],
            "severity": "high",
            "business_impact": "Communication failures, cultural incidents",
            "description": "Errors in language translation or cultural adaptation"
        },
        "incomplete": {
            "indicators": ["partial response", "missing information", "truncated output", "unfinished"],
            "severity": "medium",
            "business_impact": "Incomplete business processes, user frustration",
            "description": "Agent failing to provide complete responses or solutions"
        },
        "hallucinations": {
            "indicators": ["made up facts", "false information", "non-existent data", "fabricated details"],
            "severity": "critical",
            "business_impact": "Misinformation spread, legal liability, trust erosion",
            "description": "Agent generating false or non-existent information"
        }
    }
}


class UniversalFailureClassifier:
    """
    Framework-agnostic failure pattern classifier.
    
    Provides universal failure detection that works across all agent frameworks,
    enabling cross-framework learning and optimization insights.
    """
    
    def __init__(self):
        """Initialize classifier with framework patterns and detection rules."""
        self.framework_patterns = FrameworkPatterns()
        self.framework_detector = FrameworkDetector()
        self._pattern_cache = {}
        
    def classify_failure_universal(
        self, 
        trace: Dict[str, Any], 
        framework: Optional[str] = None
    ) -> ClassificationResult:
        """
        Map any framework failure to universal taxonomy.
        
        Args:
            trace: Agent execution trace or output
            framework: Framework name (auto-detected if None)
            
        Returns:
            ClassificationResult with universal patterns and insights
        """
        # Detect framework if not provided
        if not framework:
            framework = self.framework_detector.detect_framework(trace)
        
        # Extract relevant data from trace
        output_text = OutputExtractor.extract_output(trace, framework or "generic")
        tool_calls = ToolCallExtractor.extract_tool_calls(trace, framework or "generic")
        
        # Classify failures using universal patterns
        universal_patterns = self._detect_universal_patterns(trace, output_text, tool_calls, framework)
        
        # Identify framework-specific issues
        framework_issues = self._detect_framework_specific_issues(trace, framework)
        
        # Generate cross-framework insights
        cross_framework_insights = self._generate_cross_framework_insights(universal_patterns, framework)
        
        # Calculate business impact
        business_impact_score = self._calculate_business_impact(universal_patterns)
        
        # Prioritize remediation
        remediation_priority = self._prioritize_remediation(universal_patterns)
        
        return ClassificationResult(
            universal_patterns=universal_patterns,
            framework_specific_issues=framework_issues,
            cross_framework_insights=cross_framework_insights,
            business_impact_score=business_impact_score,
            remediation_priority=remediation_priority
        )
    
    def detect_cross_framework_patterns(
        self, 
        failure_pattern: FailurePattern, 
        all_frameworks_data: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Identify how different frameworks handle the same failure type.
        
        Args:
            failure_pattern: Universal failure pattern to analyze
            all_frameworks_data: Historical data from all frameworks
            
        Returns:
            Cross-framework analysis with insights and recommendations
        """
        pattern_type = failure_pattern.pattern_type
        subtype = failure_pattern.subtype
        
        framework_handling = {}
        success_rates = {}
        
        for framework, traces in all_frameworks_data.items():
            # Analyze how this framework handles this pattern type
            handling_analysis = self._analyze_framework_handling(traces, pattern_type, subtype)
            framework_handling[framework] = handling_analysis
            success_rates[framework] = handling_analysis.get('success_rate', 0.0)
        
        # Find best practices
        best_framework = max(success_rates.items(), key=lambda x: x[1])[0] if success_rates else None
        
        return {
            "pattern_type": pattern_type,
            "subtype": subtype,
            "framework_handling": framework_handling,
            "success_rates": success_rates,
            "best_practice_framework": best_framework,
            "recommendations": self._generate_cross_framework_recommendations(
                failure_pattern, framework_handling, best_framework
            )
        }
    
    def _detect_universal_patterns(
        self, 
        trace: Dict[str, Any], 
        output_text: str, 
        tool_calls: List[str], 
        framework: Optional[str]
    ) -> List[FailurePattern]:
        """Detect universal failure patterns in trace data."""
        patterns = []
        
        # Combine all text for analysis
        all_text = f"{output_text} {json.dumps(trace)} {' '.join(tool_calls)}".lower()
        
        # Check each universal pattern category
        for category, subcategories in UNIVERSAL_FAILURE_PATTERNS.items():
            for subtype, pattern_def in subcategories.items():
                confidence = self._calculate_pattern_confidence(all_text, pattern_def["indicators"])
                
                if confidence > 0.1:  # Threshold for pattern detection
                    patterns.append(FailurePattern(
                        pattern_type=category,
                        subtype=subtype,
                        severity=pattern_def["severity"],
                        framework=framework,
                        description=pattern_def["description"],
                        indicators=pattern_def["indicators"],
                        business_impact=pattern_def["business_impact"],
                        confidence=confidence
                    ))
        
        # Sort by confidence and severity
        patterns.sort(key=lambda p: (self._severity_weight(p.severity), p.confidence), reverse=True)
        
        return patterns
    
    def _calculate_pattern_confidence(self, text: str, indicators: List[str]) -> float:
        """Calculate confidence score for pattern detection."""
        matches = 0
        total_indicators = len(indicators)

        for indicator in indicators:
            # Use partial matching for better detection
            if indicator.lower() in text or any(word in text for word in indicator.lower().split()):
                matches += 1

        # Give bonus for multiple matches
        confidence = matches / total_indicators if total_indicators > 0 else 0.0

        # Boost confidence if we have multiple indicator matches
        if matches > 1:
            confidence = min(1.0, confidence * 1.2)

        return confidence
    
    def _severity_weight(self, severity: str) -> int:
        """Convert severity to numeric weight for sorting."""
        weights = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        return weights.get(severity, 0)
    
    def _detect_framework_specific_issues(
        self, 
        trace: Dict[str, Any], 
        framework: Optional[str]
    ) -> Dict[str, List[str]]:
        """Detect issues specific to the detected framework."""
        if not framework:
            return {}
        
        issues = defaultdict(list)
        
        # Framework-specific issue detection
        framework_specific_checks = {
            "langchain": self._check_langchain_issues,
            "crewai": self._check_crewai_issues,
            "autogen": self._check_autogen_issues,
            "openai": self._check_openai_issues,
            "anthropic": self._check_anthropic_issues
        }
        
        checker = framework_specific_checks.get(framework.lower())
        if checker:
            issues[framework] = checker(trace)
        
        return dict(issues)
    
    def _check_langchain_issues(self, trace: Dict[str, Any]) -> List[str]:
        """Check for LangChain-specific issues."""
        issues = []
        trace_str = json.dumps(trace).lower()
        
        if "intermediate_steps" in trace_str and len(trace.get("intermediate_steps", [])) > 10:
            issues.append("Excessive intermediate steps - consider chain optimization")
        
        if "agent_scratchpad" in trace_str and len(str(trace.get("agent_scratchpad", ""))) > 5000:
            issues.append("Large scratchpad - memory management needed")
        
        return issues
    
    def _check_crewai_issues(self, trace: Dict[str, Any]) -> List[str]:
        """Check for CrewAI-specific issues."""
        issues = []
        trace_str = json.dumps(trace).lower()
        
        if "crew_output" in trace_str and "task_results" in trace_str:
            task_results = trace.get("task_results", [])
            if len(task_results) > 5:
                issues.append("Too many tasks - consider task consolidation")
        
        return issues
    
    def _check_autogen_issues(self, trace: Dict[str, Any]) -> List[str]:
        """Check for AutoGen-specific issues."""
        issues = []
        
        if "messages" in trace:
            messages = trace.get("messages", [])
            if len(messages) > 20:
                issues.append("Long conversation - consider conversation pruning")
        
        return issues
    
    def _check_openai_issues(self, trace: Dict[str, Any]) -> List[str]:
        """Check for OpenAI-specific issues."""
        issues = []
        
        if "choices" in trace:
            choices = trace.get("choices", [])
            if any(choice.get("finish_reason") == "length" for choice in choices):
                issues.append("Response truncated - increase max_tokens")
        
        return issues
    
    def _check_anthropic_issues(self, trace: Dict[str, Any]) -> List[str]:
        """Check for Anthropic-specific issues."""
        issues = []
        
        if "stop_reason" in trace and trace.get("stop_reason") == "max_tokens":
            issues.append("Response truncated - increase max_tokens")
        
        return issues

    def _generate_cross_framework_insights(
        self,
        patterns: List[FailurePattern],
        current_framework: Optional[str]
    ) -> List[str]:
        """Generate insights from cross-framework pattern analysis."""
        insights = []

        if not patterns or not current_framework:
            return insights

        # Framework-specific insights based on detected patterns
        framework_insights = {
            "langchain": {
                "tool_failures": "Consider using LangChain's RetryTool wrapper for better error handling",
                "planning_failures": "Use ReActAgent with structured planning prompts",
                "efficiency_issues": "Optimize chain composition and reduce intermediate steps"
            },
            "crewai": {
                "tool_failures": "Leverage CrewAI's built-in retry mechanisms in task definitions",
                "planning_failures": "Use hierarchical task decomposition for better coordination",
                "efficiency_issues": "Optimize crew composition and task delegation"
            },
            "autogen": {
                "tool_failures": "Implement tool_call_retry in agent configuration",
                "planning_failures": "Use conversation flow validation and checkpoints",
                "efficiency_issues": "Optimize conversation pruning and memory management"
            }
        }

        current_insights = framework_insights.get(current_framework.lower(), {})

        for pattern in patterns:
            if pattern.pattern_type in current_insights:
                insights.append(current_insights[pattern.pattern_type])

        # Add cross-framework learning insights
        if current_framework.lower() == "langchain":
            insights.append("CrewAI users solve coordination issues with hierarchical task structures")
            insights.append("AutoGen users handle long conversations with pruning strategies")
        elif current_framework.lower() == "crewai":
            insights.append("LangChain users handle tool failures with RetryTool wrappers")
            insights.append("AutoGen users manage complex workflows with conversation checkpoints")
        elif current_framework.lower() == "autogen":
            insights.append("LangChain users optimize efficiency with chain composition")
            insights.append("CrewAI users handle coordination with task delegation patterns")

        return insights

    def _calculate_business_impact(self, patterns: List[FailurePattern]) -> float:
        """Calculate overall business impact score from detected patterns."""
        if not patterns:
            return 0.0

        severity_weights = {"critical": 1.0, "high": 0.7, "medium": 0.4, "low": 0.1}
        total_impact = 0.0

        for pattern in patterns:
            weight = severity_weights.get(pattern.severity, 0.0)
            total_impact += weight * pattern.confidence

        # Normalize to 0-1 scale
        max_possible_impact = len(patterns) * 1.0
        return min(total_impact / max_possible_impact, 1.0) if max_possible_impact > 0 else 0.0

    def _prioritize_remediation(self, patterns: List[FailurePattern]) -> List[str]:
        """Prioritize remediation actions based on severity and business impact."""
        if not patterns:
            return []

        # Sort patterns by priority (severity + confidence)
        priority_patterns = sorted(
            patterns,
            key=lambda p: (self._severity_weight(p.severity) * p.confidence),
            reverse=True
        )

        remediation_actions = []
        for pattern in priority_patterns[:5]:  # Top 5 priorities
            action = f"Address {pattern.subtype} ({pattern.severity} severity, {pattern.confidence:.1%} confidence)"
            remediation_actions.append(action)

        return remediation_actions

    def _analyze_framework_handling(
        self,
        traces: List[Dict[str, Any]],
        pattern_type: str,
        subtype: str
    ) -> Dict[str, Any]:
        """Analyze how a framework handles specific failure patterns."""
        total_traces = len(traces)
        if total_traces == 0:
            return {"success_rate": 0.0, "handling_strategies": []}

        # Count traces with this pattern type
        pattern_traces = 0
        successful_handling = 0
        strategies = set()

        for trace in traces:
            # Simple heuristic: check if trace contains pattern indicators
            trace_text = json.dumps(trace).lower()
            pattern_def = UNIVERSAL_FAILURE_PATTERNS.get(pattern_type, {}).get(subtype, {})
            indicators = pattern_def.get("indicators", [])

            has_pattern = any(indicator in trace_text for indicator in indicators)
            if has_pattern:
                pattern_traces += 1

                # Check for success indicators (framework-specific)
                if self._has_success_indicators(trace, trace_text):
                    successful_handling += 1

                # Extract handling strategies
                strategies.update(self._extract_handling_strategies(trace, pattern_type))

        success_rate = successful_handling / pattern_traces if pattern_traces > 0 else 1.0

        return {
            "success_rate": success_rate,
            "pattern_occurrences": pattern_traces,
            "handling_strategies": list(strategies)
        }

    def _has_success_indicators(self, trace: Dict[str, Any], trace_text: str) -> bool:
        """Check if trace shows successful handling of issues."""
        success_indicators = [
            "success", "completed", "resolved", "fixed", "recovered",
            "retry successful", "fallback worked", "error handled"
        ]
        return any(indicator in trace_text for indicator in success_indicators)

    def _extract_handling_strategies(self, trace: Dict[str, Any], pattern_type: str) -> Set[str]:
        """Extract handling strategies from trace."""
        strategies = set()
        trace_text = json.dumps(trace).lower()

        # Common handling strategies by pattern type
        strategy_indicators = {
            "tool_failures": ["retry", "fallback", "timeout increase", "circuit breaker"],
            "planning_failures": ["replan", "decompose", "validate", "checkpoint"],
            "efficiency_issues": ["optimize", "cache", "batch", "parallel"],
            "output_quality": ["validate", "verify", "cross-check", "review"]
        }

        indicators = strategy_indicators.get(pattern_type, [])
        for indicator in indicators:
            if indicator in trace_text:
                strategies.add(indicator)

        return strategies

    def _generate_cross_framework_recommendations(
        self,
        failure_pattern: FailurePattern,
        framework_handling: Dict[str, Dict[str, Any]],
        best_framework: Optional[str]
    ) -> List[str]:
        """Generate recommendations based on cross-framework analysis."""
        recommendations = []

        if not best_framework or best_framework not in framework_handling:
            return recommendations

        best_handling = framework_handling[best_framework]
        strategies = best_handling.get("handling_strategies", [])

        pattern_type = failure_pattern.pattern_type
        subtype = failure_pattern.subtype

        # Generate specific recommendations
        if strategies:
            recommendations.append(
                f"Best practice from {best_framework}: {', '.join(strategies[:3])}"
            )

        # Pattern-specific recommendations
        if pattern_type == "tool_failures" and "retry" in strategies:
            recommendations.append("Implement exponential backoff retry logic")
        elif pattern_type == "planning_failures" and "decompose" in strategies:
            recommendations.append("Break complex tasks into smaller, manageable steps")
        elif pattern_type == "efficiency_issues" and "cache" in strategies:
            recommendations.append("Implement caching for expensive operations")

        return recommendations


def analyze_failure_patterns_batch(
    traces: List[Dict[str, Any]],
    frameworks: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Analyze failure patterns across multiple traces for batch insights.

    Args:
        traces: List of agent execution traces
        frameworks: Optional list of framework names (auto-detected if None)

    Returns:
        Comprehensive analysis with universal patterns and cross-framework insights
    """
    classifier = UniversalFailureClassifier()

    all_patterns = []
    framework_distribution = Counter()
    pattern_distribution = Counter()

    for i, trace in enumerate(traces):
        framework = frameworks[i] if frameworks and i < len(frameworks) else None
        result = classifier.classify_failure_universal(trace, framework)

        all_patterns.extend(result.universal_patterns)
        if result.universal_patterns:
            detected_framework = result.universal_patterns[0].framework
            if detected_framework:
                framework_distribution[detected_framework] += 1

        for pattern in result.universal_patterns:
            pattern_key = f"{pattern.pattern_type}.{pattern.subtype}"
            pattern_distribution[pattern_key] += 1

    # Calculate aggregate metrics
    total_traces = len(traces)
    failure_rate = len([p for p in all_patterns if p.confidence > 0.5]) / total_traces if total_traces > 0 else 0

    # Most common patterns
    top_patterns = pattern_distribution.most_common(5)

    # Framework comparison
    framework_stats = {}
    for framework, count in framework_distribution.items():
        framework_patterns = [p for p in all_patterns if p.framework == framework]
        avg_severity = sum(classifier._severity_weight(p.severity) for p in framework_patterns) / len(framework_patterns) if framework_patterns else 0
        framework_stats[framework] = {
            "trace_count": count,
            "avg_severity": avg_severity,
            "pattern_count": len(framework_patterns)
        }

    return {
        "summary": {
            "total_traces": total_traces,
            "failure_rate": failure_rate,
            "unique_patterns": len(pattern_distribution),
            "frameworks_detected": len(framework_distribution)
        },
        "top_patterns": top_patterns,
        "framework_stats": framework_stats,
        "all_patterns": all_patterns,
        "recommendations": _generate_batch_recommendations(all_patterns, framework_stats)
    }


def _generate_batch_recommendations(
    patterns: List[FailurePattern],
    framework_stats: Dict[str, Dict[str, Any]]
) -> List[str]:
    """Generate recommendations from batch analysis."""
    recommendations = []

    if not patterns:
        return recommendations

    # Most critical issues
    critical_patterns = [p for p in patterns if p.severity == "critical"]
    if critical_patterns:
        recommendations.append(f"Address {len(critical_patterns)} critical issues immediately")

    # Framework-specific recommendations
    if len(framework_stats) > 1:
        best_framework = min(framework_stats.items(), key=lambda x: x[1]["avg_severity"])[0]
        recommendations.append(f"Consider adopting patterns from {best_framework} (lowest avg severity)")

    # Pattern-specific recommendations
    pattern_counts = Counter(p.pattern_type for p in patterns)
    most_common_pattern = pattern_counts.most_common(1)[0][0] if pattern_counts else None

    if most_common_pattern == "tool_failures":
        recommendations.append("Focus on improving tool reliability and error handling")
    elif most_common_pattern == "planning_failures":
        recommendations.append("Improve agent planning and goal-setting capabilities")
    elif most_common_pattern == "efficiency_issues":
        recommendations.append("Optimize agent performance and resource usage")
    elif most_common_pattern == "output_quality":
        recommendations.append("Enhance output validation and quality assurance")

    return recommendations
