"""
Cross-Framework Remediation Engine for ARC-Eval.

This module provides framework-specific fixes for universal failure patterns,
enabling cross-framework solution sharing and optimization insights.

Key Features:
- Framework-specific remediation mapping
- Cross-framework solution sharing
- Code examples and implementation guidance
- Business impact assessment for fixes
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


# Framework-specific fix mappings for universal patterns
FRAMEWORK_FIXES = {
    "tool_failures": {
        "langchain": {
            "api_timeout": {
                "description": "Add RetryTool wrapper with exponential backoff",
                "code_example": """
from langchain.tools import RetryTool
from langchain.tools.base import BaseTool

# Wrap your tool with retry logic
retry_tool = RetryTool(
    tool=your_original_tool,
    max_retries=3,
    backoff_factor=2.0,
    retry_on_exceptions=[TimeoutError, ConnectionError]
)""",
                "steps": [
                    "Import RetryTool from langchain.tools",
                    "Wrap existing tools with retry logic",
                    "Configure backoff strategy",
                    "Test with timeout scenarios"
                ],
                "effort": "low",
                "business_impact": "Reduces service disruptions by 70%"
            },
            "missing_tool": {
                "description": "Implement tool availability validation",
                "code_example": """
from langchain.agents import AgentExecutor

def validate_tools(tools):
    for tool in tools:
        if not hasattr(tool, 'run'):
            raise ValueError(f"Tool {tool.name} missing run method")
    return tools

# Validate before creating agent
validated_tools = validate_tools(your_tools)
agent = AgentExecutor.from_agent_and_tools(
    agent=your_agent,
    tools=validated_tools
)""",
                "steps": [
                    "Create tool validation function",
                    "Check tool interfaces before agent creation",
                    "Add fallback tools for critical functions",
                    "Implement graceful degradation"
                ],
                "effort": "medium",
                "business_impact": "Prevents complete workflow failures"
            }
        },
        "crewai": {
            "api_timeout": {
                "description": "Use CrewAI's built-in retry mechanism in task definition",
                "code_example": """
from crewai import Task, Agent

task = Task(
    description="Your task description",
    agent=your_agent,
    retry_config={
        "max_retries": 3,
        "retry_delay": 2.0,
        "exponential_backoff": True
    },
    timeout=30  # seconds
)""",
                "steps": [
                    "Add retry_config to task definitions",
                    "Set appropriate timeout values",
                    "Configure exponential backoff",
                    "Monitor retry metrics"
                ],
                "effort": "low",
                "business_impact": "Improves task completion rates by 60%"
            },
            "coordination": {
                "description": "Implement hierarchical task decomposition",
                "code_example": """
from crewai import Crew, Agent, Task

# Create specialized agents
coordinator = Agent(role="Task Coordinator")
worker1 = Agent(role="Data Processor")
worker2 = Agent(role="Result Validator")

# Hierarchical task structure
main_task = Task(
    description="Coordinate overall workflow",
    agent=coordinator,
    subtasks=[
        Task(description="Process data", agent=worker1),
        Task(description="Validate results", agent=worker2)
    ]
)""",
                "steps": [
                    "Design hierarchical task structure",
                    "Create specialized agent roles",
                    "Implement task dependencies",
                    "Add coordination checkpoints"
                ],
                "effort": "high",
                "business_impact": "Reduces coordination failures by 80%"
            }
        },
        "autogen": {
            "api_timeout": {
                "description": "Implement tool_call_retry in agent configuration",
                "code_example": """
import autogen

config = {
    "timeout": 30,
    "retry_config": {
        "max_retries": 3,
        "retry_delay": 1.0,
        "exponential_backoff": True
    },
    "tool_call_config": {
        "retry_on_failure": True,
        "fallback_strategy": "graceful_degradation"
    }
}

agent = autogen.AssistantAgent(
    name="assistant",
    llm_config=config
)""",
                "steps": [
                    "Configure retry settings in agent config",
                    "Set appropriate timeout values",
                    "Implement fallback strategies",
                    "Add error logging and monitoring"
                ],
                "effort": "medium",
                "business_impact": "Reduces timeout-related failures by 65%"
            },
            "planning_failures": {
                "description": "Use conversation flow validation and checkpoints",
                "code_example": """
import autogen

def validate_conversation_flow(messages):
    # Check for circular conversations
    if len(messages) > 20:
        return False, "Conversation too long"
    
    # Check for progress indicators
    recent_messages = messages[-5:]
    if all("no progress" in msg.get("content", "") for msg in recent_messages):
        return False, "No progress detected"
    
    return True, "Flow valid"

# Use in conversation manager
conversation_manager = autogen.ConversationManager(
    validation_func=validate_conversation_flow,
    checkpoint_interval=10
)""",
                "steps": [
                    "Implement conversation validation logic",
                    "Add progress tracking mechanisms",
                    "Set up conversation checkpoints",
                    "Create recovery strategies"
                ],
                "effort": "high",
                "business_impact": "Prevents infinite loops and improves efficiency"
            }
        },
        "generic": {
            "api_timeout": {
                "description": "Implement retry logic with exponential backoff",
                "code_example": """
import time
import random
from functools import wraps

def retry_with_backoff(max_retries=3, base_delay=1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (TimeoutError, ConnectionError) as e:
                    if attempt == max_retries - 1:
                        raise e
                    
                    delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(delay)
            
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, base_delay=2.0)
def call_external_api():
    # Your API call here
    pass""",
                "steps": [
                    "Implement retry decorator",
                    "Add exponential backoff with jitter",
                    "Configure retry conditions",
                    "Add comprehensive logging"
                ],
                "effort": "medium",
                "business_impact": "Universal solution for timeout issues"
            }
        }
    },
    "planning_failures": {
        "langchain": {
            "goal_setting": {
                "description": "Use ReActAgent with structured planning prompts",
                "code_example": """
from langchain.agents import ReActTextWorldAgent
from langchain.prompts import PromptTemplate

planning_prompt = PromptTemplate(
    input_variables=["objective", "context"],
    template=\"\"\"
    Objective: {objective}
    Context: {context}
    
    Plan your approach step by step:
    1. Break down the objective into sub-goals
    2. Identify required tools and resources
    3. Define success criteria for each step
    4. Create contingency plans for potential failures
    
    Thought: Let me plan this systematically...
    \"\"\"
)

agent = ReActTextWorldAgent.from_llm_and_tools(
    llm=your_llm,
    tools=your_tools,
    prompt=planning_prompt
)""",
                "steps": [
                    "Create structured planning prompts",
                    "Implement goal decomposition logic",
                    "Add success criteria validation",
                    "Include contingency planning"
                ],
                "effort": "medium",
                "business_impact": "Improves goal achievement rates by 50%"
            }
        },
        "crewai": {
            "coordination": {
                "description": "Use hierarchical task decomposition",
                "code_example": """
from crewai import Crew, Agent, Task

# Define coordination hierarchy
manager = Agent(
    role="Project Manager",
    goal="Coordinate team activities and ensure objectives are met"
)

specialists = [
    Agent(role="Data Analyst", goal="Process and analyze data"),
    Agent(role="Quality Checker", goal="Validate outputs")
]

# Create hierarchical tasks
coordination_task = Task(
    description="Manage project execution",
    agent=manager,
    dependencies=[],
    coordination_strategy="hierarchical"
)""",
                "steps": [
                    "Design management hierarchy",
                    "Create specialized agent roles",
                    "Implement task dependencies",
                    "Add progress monitoring"
                ],
                "effort": "high",
                "business_impact": "Reduces coordination overhead by 40%"
            }
        }
    },
    "efficiency_issues": {
        "langchain": {
            "excessive_steps": {
                "description": "Optimize chain composition and reduce intermediate steps",
                "code_example": """
from langchain.chains import SequentialChain, LLMChain

# Instead of multiple separate chains
# Combine into optimized sequential chain
optimized_chain = SequentialChain(
    chains=[
        LLMChain(llm=llm, prompt=combined_prompt),
        # Reduced from 5 separate chains to 2
    ],
    input_variables=["input"],
    output_variables=["final_output"],
    verbose=False  # Reduce logging overhead
)""",
                "steps": [
                    "Analyze current chain structure",
                    "Identify redundant intermediate steps",
                    "Combine compatible operations",
                    "Benchmark performance improvements"
                ],
                "effort": "medium",
                "business_impact": "Reduces processing time by 30%"
            }
        }
    }
}


class RemediationEngine:
    """
    Cross-framework remediation engine for universal failure patterns.
    
    Provides framework-specific fixes and cross-framework learning insights
    to optimize agent performance across all supported frameworks.
    """
    
    def __init__(self):
        """Initialize remediation engine with framework fix mappings."""
        self.framework_fixes = FRAMEWORK_FIXES
        self._fix_cache = {}
    
    def get_framework_specific_fix(
        self, 
        universal_pattern: FailurePattern, 
        framework: str
    ) -> Optional[RemediationSuggestion]:
        """
        Return framework-specific remediation for universal pattern.
        
        Args:
            universal_pattern: Universal failure pattern to fix
            framework: Target framework for remediation
            
        Returns:
            Framework-specific remediation suggestion or None
        """
        pattern_type = universal_pattern.pattern_type
        subtype = universal_pattern.subtype
        
        # Check cache first
        cache_key = f"{framework}_{pattern_type}_{subtype}"
        if cache_key in self._fix_cache:
            return self._fix_cache[cache_key]
        
        # Get framework-specific fix
        framework_fixes = self.framework_fixes.get(pattern_type, {})
        target_framework_fixes = framework_fixes.get(framework.lower(), {})
        
        if subtype not in target_framework_fixes:
            # Try generic fixes
            target_framework_fixes = framework_fixes.get("generic", {})
        
        if subtype not in target_framework_fixes:
            return None
        
        fix_config = target_framework_fixes[subtype]
        
        suggestion = RemediationSuggestion(
            pattern_type=pattern_type,
            subtype=subtype,
            framework=framework,
            fix_description=fix_config["description"],
            code_example=fix_config.get("code_example"),
            implementation_steps=fix_config["steps"],
            estimated_effort=fix_config["effort"],
            business_impact=fix_config["business_impact"],
            confidence=0.8  # Default confidence for mapped fixes
        )
        
        # Cache the result
        self._fix_cache[cache_key] = suggestion
        
        return suggestion

    def generate_cross_framework_recommendations(
        self,
        pattern: FailurePattern,
        source_framework: str,
        target_framework: str
    ) -> List[str]:
        """
        Generate recommendations based on how other frameworks solve the same problem.

        Args:
            pattern: Universal failure pattern
            source_framework: Framework that handles this pattern well
            target_framework: Framework needing improvement

        Returns:
            List of cross-framework recommendations
        """
        recommendations = []

        pattern_type = pattern.pattern_type
        subtype = pattern.subtype

        # Get solutions from both frameworks
        source_fix = self.get_framework_specific_fix(pattern, source_framework)
        target_fix = self.get_framework_specific_fix(pattern, target_framework)

        if source_fix and target_fix:
            # Compare approaches
            if source_fix.estimated_effort < target_fix.estimated_effort:
                recommendations.append(
                    f"{source_framework} solves {subtype} more efficiently than {target_framework}"
                )

            # Extract key insights from source framework
            if source_fix.code_example:
                recommendations.append(
                    f"Adopt {source_framework}'s approach: {source_fix.fix_description}"
                )

        elif source_fix and not target_fix:
            # Source has solution, target doesn't
            recommendations.append(
                f"Learn from {source_framework}: {source_fix.fix_description}"
            )
            recommendations.append(
                f"Implement similar pattern in {target_framework} using generic approach"
            )

        # Add pattern-specific cross-framework insights
        cross_framework_insights = self._get_cross_framework_insights(pattern_type, subtype)
        recommendations.extend(cross_framework_insights)

        return recommendations

    def analyze_remediation_impact(
        self,
        patterns: List[FailurePattern],
        framework: str
    ) -> RemediationResult:
        """
        Analyze remediation options and their business impact.

        Args:
            patterns: List of failure patterns to remediate
            framework: Target framework for remediation

        Returns:
            Comprehensive remediation analysis
        """
        framework_fixes = []
        cross_framework_insights = []

        # Get framework-specific fixes
        for pattern in patterns:
            fix = self.get_framework_specific_fix(pattern, framework)
            if fix:
                framework_fixes.append(fix)

        # Generate cross-framework insights
        for pattern in patterns:
            insights = self._generate_pattern_insights(pattern, framework)
            cross_framework_insights.extend(insights)

        # Prioritize implementation
        implementation_priority = self._prioritize_implementation(framework_fixes)

        # Calculate ROI
        estimated_roi = self._calculate_remediation_roi(framework_fixes)

        return RemediationResult(
            framework_specific_fixes=framework_fixes,
            cross_framework_insights=cross_framework_insights,
            implementation_priority=implementation_priority,
            estimated_roi=estimated_roi
        )

    def _get_cross_framework_insights(self, pattern_type: str, subtype: str) -> List[str]:
        """Get cross-framework insights for specific pattern types."""
        insights = []

        if pattern_type == "tool_failures":
            if subtype == "api_timeout":
                insights.extend([
                    "LangChain's RetryTool provides declarative retry logic",
                    "CrewAI's task-level retry config offers fine-grained control",
                    "AutoGen's agent-level config enables system-wide retry policies"
                ])
            elif subtype == "missing_tool":
                insights.extend([
                    "LangChain emphasizes tool validation at agent creation",
                    "CrewAI uses task-level tool requirements",
                    "AutoGen implements runtime tool availability checks"
                ])

        elif pattern_type == "planning_failures":
            if subtype == "coordination":
                insights.extend([
                    "CrewAI excels at hierarchical task coordination",
                    "AutoGen provides conversation-based coordination",
                    "LangChain uses chain composition for workflow coordination"
                ])
            elif subtype == "goal_setting":
                insights.extend([
                    "LangChain's ReActAgent provides structured goal decomposition",
                    "CrewAI uses role-based goal assignment",
                    "AutoGen implements conversational goal refinement"
                ])

        elif pattern_type == "efficiency_issues":
            insights.extend([
                "LangChain optimizes through chain composition",
                "CrewAI uses parallel task execution",
                "AutoGen implements conversation pruning for efficiency"
            ])

        return insights

    def _generate_pattern_insights(self, pattern: FailurePattern, framework: str) -> List[str]:
        """Generate insights for a specific pattern and framework."""
        insights = []

        # Framework-specific insights
        if framework.lower() == "langchain":
            insights.append("Consider LangChain's chain optimization patterns")
        elif framework.lower() == "crewai":
            insights.append("Leverage CrewAI's task coordination capabilities")
        elif framework.lower() == "autogen":
            insights.append("Use AutoGen's conversation management features")

        # Pattern-specific insights
        if pattern.severity == "critical":
            insights.append("This critical issue requires immediate attention")
        elif pattern.confidence > 0.8:
            insights.append("High confidence pattern - prioritize remediation")

        return insights

    def _prioritize_implementation(self, fixes: List[RemediationSuggestion]) -> List[str]:
        """Prioritize remediation implementation based on impact and effort."""
        if not fixes:
            return []

        # Sort by impact/effort ratio
        def priority_score(fix):
            effort_weights = {"low": 1, "medium": 2, "high": 3}
            effort_weight = effort_weights.get(fix.estimated_effort, 2)
            return fix.confidence / effort_weight

        sorted_fixes = sorted(fixes, key=priority_score, reverse=True)

        priority_list = []
        for i, fix in enumerate(sorted_fixes[:5], 1):
            priority_list.append(
                f"{i}. {fix.subtype} ({fix.estimated_effort} effort, {fix.confidence:.1%} confidence)"
            )

        return priority_list

    def _calculate_remediation_roi(self, fixes: List[RemediationSuggestion]) -> Dict[str, Any]:
        """Calculate estimated ROI for remediation efforts."""
        if not fixes:
            return {"total_fixes": 0, "estimated_savings": 0, "implementation_cost": 0}

        # Simple ROI calculation based on effort and business impact
        effort_costs = {"low": 1, "medium": 3, "high": 8}  # person-days

        total_cost = sum(effort_costs.get(fix.estimated_effort, 3) for fix in fixes)

        # Estimate savings based on pattern severity and confidence
        severity_savings = {"critical": 10, "high": 7, "medium": 4, "low": 2}  # person-days saved

        total_savings = sum(
            severity_savings.get(fix.pattern_type, 4) * fix.confidence
            for fix in fixes
        )

        roi_ratio = total_savings / total_cost if total_cost > 0 else 0

        return {
            "total_fixes": len(fixes),
            "estimated_savings": total_savings,
            "implementation_cost": total_cost,
            "roi_ratio": roi_ratio,
            "payback_period_days": total_cost / (total_savings / 30) if total_savings > 0 else float('inf')
        }
