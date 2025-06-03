"""
Cross-Framework Remediation Engine for ARC-Eval.

This module provides context-aware fixes for universal failure patterns,
enabling cross-framework solution sharing and optimization insights using judge analysis.

Key Features:
- Remediation recommendations using ImproveJudge
- Context-aware code generation based on actual failure patterns
- Cross-framework solution sharing
- Business impact assessment
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict

from agent_eval.analysis.universal_failure_classifier import FailurePattern, UNIVERSAL_FAILURE_PATTERNS

logger = logging.getLogger(__name__)


@dataclass
class RemediationSuggestion:
    """Represents a specific remediation suggestion."""
    pattern_type: str
    subtype: str
    framework: str
    fix_description: str
    code_example: Optional[str]
    implementation_steps: List[str]
    estimated_effort: str  # 'low', 'medium', 'high'
    business_impact: str
    confidence: float


@dataclass
class RemediationResult:
    """Result of remediation analysis."""
    framework_specific_fixes: List[RemediationSuggestion]
    cross_framework_insights: List[str]
    implementation_priority: List[str]
    estimated_roi: Dict[str, Any]


# ==================== AI Judge Integration ====================
# Static template system replaced with ImproveJudge for intelligent remediation.
# See ImproveJudge.generate_improvement_plan() for AI-powered contextual analysis.


class RemediationEngine:
    """
    Cross-framework remediation engine for universal failure patterns.
    
    Provides context-aware fixes and cross-framework learning insights
    using judge analysis instead of static templates.
    """
    
    def __init__(self, api_manager=None):
        """Initialize remediation engine with judge capabilities."""
        self.api_manager = api_manager
        self._analysis_cache = {}
    
    def get_framework_specific_fix(
        self, 
        universal_pattern: FailurePattern, 
        framework: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[RemediationSuggestion]:
        """
        Return framework-specific remediation for universal pattern.
        
        Args:
            universal_pattern: Universal failure pattern to fix
            framework: Target framework for remediation
            context: Additional context for analysis
            
        Returns:
            Framework-specific remediation suggestion or None
        """
        try:
            # Use ImproveJudge for intelligent remediation
            from agent_eval.evaluation.judges.workflow.improve import ImproveJudge
            from agent_eval.evaluation.judges.api_manager import APIManager
            
            # Initialize judge with Cerebras for fast inference
            api_manager = self.api_manager or APIManager(provider="cerebras")
            improve_judge = ImproveJudge(api_manager)
            
            # Generate intelligent remediation
            remediation_analysis = improve_judge.generate_framework_specific_remediation(
                universal_pattern, framework, context
            )
            
            if remediation_analysis:
                return RemediationSuggestion(
                    pattern_type=universal_pattern.pattern_type,
                    subtype=universal_pattern.subtype,
                    framework=framework,
                    fix_description=remediation_analysis.get("fix_description", ""),
                    code_example=remediation_analysis.get("code_example"),
                    implementation_steps=remediation_analysis.get("implementation_steps", []),
                    estimated_effort=remediation_analysis.get("estimated_effort", "medium"),
                    business_impact=remediation_analysis.get("business_impact", ""),
                    confidence=remediation_analysis.get("confidence", 0.85)
                )
                
        except ImportError:
            # Fallback to basic analysis if judge not available
            logger.warning("ImproveJudge not available, using basic remediation")
            return self._generate_basic_remediation(universal_pattern, framework)
        except Exception as e:
            logger.warning(f"AI remediation failed: {e}")
            return self._generate_basic_remediation(universal_pattern, framework)
        
        return None

    def generate_cross_framework_recommendations(
        self,
        pattern: FailurePattern,
        source_framework: str,
        target_framework: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Generate recommendations based on cross-framework analysis.

        Args:
            pattern: Universal failure pattern
            source_framework: Framework that handles this pattern well
            target_framework: Framework needing improvement
            context: Additional context for analysis

        Returns:
            List of cross-framework recommendations
        """
        try:
            # Use ImproveJudge for intelligent cross-framework analysis
            from agent_eval.evaluation.judges.workflow.improve import ImproveJudge
            from agent_eval.evaluation.judges.api_manager import APIManager
            
            api_manager = self.api_manager or APIManager(provider="cerebras")
            improve_judge = ImproveJudge(api_manager)
            
            # Generate cross-framework insights
            recommendations = improve_judge.analyze_cross_framework_solutions(
                pattern, source_framework, target_framework, context
            )
            
            return recommendations or self._generate_basic_cross_framework_insights(pattern)
            
        except ImportError:
            logger.warning("ImproveJudge not available, using basic cross-framework analysis")
            return self._generate_basic_cross_framework_insights(pattern)
        except Exception as e:
            logger.warning(f"AI cross-framework analysis failed: {e}")
            return self._generate_basic_cross_framework_insights(pattern)

    def analyze_remediation_impact(
        self,
        patterns: List[FailurePattern],
        framework: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RemediationResult:
        """
        Analyze remediation options using impact assessment.

        Args:
            patterns: List of failure patterns to remediate
            framework: Target framework for remediation
            context: Additional context for analysis

        Returns:
            Comprehensive remediation analysis
        """
        try:
            # Use ImproveJudge for intelligent impact analysis
            from agent_eval.evaluation.judges.workflow.improve import ImproveJudge
            from agent_eval.evaluation.judges.api_manager import APIManager
            
            api_manager = self.api_manager or APIManager(provider="cerebras")
            improve_judge = ImproveJudge(api_manager)
            
            # Generate comprehensive remediation analysis
            analysis_result = improve_judge.analyze_comprehensive_remediation(
                patterns, framework, context
            )
            
            if analysis_result:
                return RemediationResult(
                    framework_specific_fixes=analysis_result.get("framework_fixes", []),
                    cross_framework_insights=analysis_result.get("cross_framework_insights", []),
                    implementation_priority=analysis_result.get("implementation_priority", []),
                    estimated_roi=analysis_result.get("estimated_roi", {})
                )
                
        except ImportError:
            logger.warning("ImproveJudge not available, using basic remediation analysis")
        except Exception as e:
            logger.warning(f"AI remediation analysis failed: {e}")
        
        # Fallback to basic analysis
        return self._generate_basic_remediation_result(patterns, framework)

    def generate_intelligent_remediation(
        self, 
        patterns: List[FailurePattern], 
        framework: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RemediationResult:
        """
        Generate remediation using judge analysis.
        
        This is the main entry point for remediation analysis,
        replacing static template-based approaches.
        
        Args:
            patterns: List of failure patterns to remediate
            framework: Target framework
            context: Additional context for analysis
            
        Returns:
            Comprehensive remediation analysis
        """
        return self.analyze_remediation_impact(patterns, framework, context)

    def _generate_basic_remediation(self, pattern: FailurePattern, framework: str) -> Optional[RemediationSuggestion]:
        """Generate basic remediation as fallback when judge is unavailable."""
        return RemediationSuggestion(
            pattern_type=pattern.pattern_type,
            subtype=pattern.subtype,
            framework=framework,
            fix_description=f"Address {pattern.subtype} issue in {framework}",
            code_example=None,
            implementation_steps=["Analyze specific failure context", "Implement framework-appropriate solution"],
            estimated_effort="medium",
            business_impact="Improves system reliability",
            confidence=0.6
        )

    def _generate_basic_cross_framework_insights(self, pattern: FailurePattern) -> List[str]:
        """Generate basic cross-framework insights as fallback."""
        return [
            f"Cross-framework analysis available for {pattern.pattern_type}",
            "Enable ImproveJudge for detailed cross-framework recommendations",
            "Consider framework-specific best practices for this pattern type"
        ]

    def _generate_basic_remediation_result(self, patterns: List[FailurePattern], framework: str) -> RemediationResult:
        """Generate basic remediation result as fallback."""
        return RemediationResult(
            framework_specific_fixes=[],
            cross_framework_insights=[
                f"Judge-based remediation available for {framework}",
                "Enable ImproveJudge for enhanced remediation analysis"
            ],
            implementation_priority=[
                "1. Enable judge integration for enhanced remediation",
                "2. Analyze specific failure patterns in context"
            ],
            estimated_roi={
                "total_fixes": len(patterns),
                "estimated_savings": 0,
                "implementation_cost": 0,
                "roi_ratio": 0
            }
        )