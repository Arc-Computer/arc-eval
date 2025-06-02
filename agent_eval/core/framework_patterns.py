"""
Centralized framework detection patterns for ARC-Eval.

This module consolidates all framework detection patterns to eliminate duplication
and provide a single source of truth for framework identification.
"""

import re
from typing import Dict, List, Pattern, Any, Optional


class FrameworkPatterns:
    """Centralized framework detection patterns and utilities."""
    
    def __init__(self):
        """Initialize framework patterns with compiled regex for performance."""
        self._tool_call_patterns = self._compile_tool_call_patterns()
        self._structure_patterns = self._compile_structure_patterns()
        self._failure_patterns = self._compile_failure_patterns()
    
    def _compile_tool_call_patterns(self) -> Dict[str, List[Pattern[str]]]:
        """Compile tool call detection patterns for each framework."""
        patterns = {
            "openai": [
                r'"function":\s*\{\s*"name":\s*"([^"]+)"',
                r'"function_call".*?"name":\s*"([^"]+)"',
                r'"tools".*?"function".*?"name":\s*"([^"]+)"',
                r'openai.*?function.*?([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "anthropic": [
                r'<function_calls>.*?<invoke name="([^"]+)"',
                r'<tool_use>.*?<n>([^<]+)</n>',
                r'"type":\s*"tool_use".*?"name":\s*"([^"]+)"',
                r'"tool_use".*?"name":\s*"([^"]+)"',
                r'Tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'Using tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "langchain": [
                r'"tool":\s*"([^"]+)"',
                r'Action:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'AgentAction\(tool=[\'"]([^\'\"]+)[\'"]',
                r'tool=[\'"]([^\'\"]+)[\'"]',
                r'intermediate_steps.*?tool=[\'"]([^\'\"]+)[\'"]',
                r'```\s*(\w+)\(',
                r'using tool ([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "langgraph": [
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',
                r'node execution:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"messages".*?"tool_calls".*?"name":\s*"([^"]+)"',
                r'langgraph.*?tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "crewai": [
                r'"tool_name":\s*"([^"]+)"',
                r'"action":\s*"([^"]+)"',
                r'crew.*?tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'agent.*?using.*?([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "autogen": [
                r'"function_call".*?"name":\s*"([^"]+)"',
                r'autogen.*?function.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"tool_calls".*?"function".*?"name":\s*"([^"]+)"',
                r'execute_function.*?([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "agno": [
                r'"tools_used":\s*\[.*?"([^"]+)".*?\]',
                r'"function_calls".*?"name":\s*"([^"]+)"',
                r'using tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'agno.*?tool:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
            ],
            "google_adk": [
                r'"functionCall":\s*{\s*"name":\s*"([^"]+)"',
                r'function call:\s*([a-zA-Z_][a-zA-Z0-9_]*)',
                r'"tool_name":\s*"([^"]+)"',
                r'vertex_ai_tools.*?"tool_name":\s*"([^"]+)"',
            ],
            "nvidia_aiq": [
                r'"workflow_output".*?"intermediate_steps".*?"([^"]+)"',
                r'"input_message".*?"workflow_output".*?"([^"]+)"',
                r'"TOOL_START".*?"([^"]+)"',
                r'"TOOL_END".*?"([^"]+)"',
                r'workflow_output\.json.*?"([^"]+)"',
            ],
            "generic": [
                r'"tool":\s*"([^"]+)"',
                r'(?:call|calling|invoke|invoking|use|using|execute|executing).*?tool.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'(?:function|method|api).*?call.*?([a-zA-Z_][a-zA-Z0-9_]*)',
                r'tool.*?([a-zA-Z_][a-zA-Z0-9_]*(?:_api|_tool|_engine|_analyzer|_validator|_detector|_monitor|_checker))',
                r'```python\n.*?(\w+)\(',
                r'(\w+)\.(\w+)\(',
            ]
        }
        
        # Compile all patterns for performance
        compiled_patterns = {}
        for framework, pattern_list in patterns.items():
            compiled_patterns[framework] = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in pattern_list]
        
        return compiled_patterns
    
    def _compile_structure_patterns(self) -> Dict[str, List[Pattern[str]]]:
        """Compile structural detection patterns for framework identification."""
        patterns = {
            "openai": [
                r'"tool_calls":\s*\[',
                r'"choices".*?"message".*?"tool_calls"',
                r'"function_call".*?"name"',
            ],
            "anthropic": [
                r'"content":\s*\[.*?"type":\s*"tool_use"',
                r'<function_calls>.*?<invoke name=',
                r'"stop_reason".*?"tool_use"',
            ],
            "langchain": [
                r'"intermediate_steps":\s*\[',
                r'"agent_scratchpad"',
                r'AgentAction\(',
                r'"_type":\s*"agent"',
            ],
            "langgraph": [
                r'"messages":\s*\[.*?"tool_calls"',
                r'"node":\s*"[^"]*"',
                r'langgraph',
            ],
            "crewai": [
                r'"crew_output"',
                r'"tasks_output"',
                r'"token_usage"',
                r'crewai',
            ],
            "autogen": [
                r'"messages":\s*\[.*?"role":\s*"assistant".*?"function_call"',
                r'autogen',
                r'"name":\s*"[^"]*agent[^"]*"',
            ],
            "agno": [
                r'"structured_output"',
                r'"tools_used"',
                r'agno',
            ],
            "google_adk": [
                r'"functionCall":\s*{',
                r'vertex_ai',
                r'google_adk',
            ],
            "nvidia_aiq": [
                r'"workflow_output"',
                r'"TOOL_START"',
                r'nvidia_aiq',
            ]
        }
        
        # Compile all patterns for performance
        compiled_patterns = {}
        for framework, pattern_list in patterns.items():
            compiled_patterns[framework] = [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in pattern_list]
        
        return compiled_patterns
    
    def _compile_failure_patterns(self) -> Dict[str, List[str]]:
        """Define failure detection patterns for each framework."""
        return {
            "langchain": ["intermediate_steps", "error"],
            "crewai": ["crew_output", "execution_error"],
            "openai": ["error", "choices"],
            "anthropic": ["error", "stop_reason"],
            "autogen": ["error", "function_call"],
            "generic": ["error", "exception", "failure", "failed"]
        }
    
    def get_tool_call_patterns(self, framework: str) -> List[Pattern[str]]:
        """Get compiled tool call patterns for a specific framework."""
        return self._tool_call_patterns.get(framework, self._tool_call_patterns.get("generic", []))
    
    def get_structure_patterns(self, framework: str) -> List[Pattern[str]]:
        """Get compiled structure patterns for a specific framework."""
        return self._structure_patterns.get(framework, [])
    
    def get_failure_patterns(self, framework: str) -> List[str]:
        """Get failure detection patterns for a specific framework."""
        return self._failure_patterns.get(framework, self._failure_patterns.get("generic", []))

    def get_framework_names(self) -> List[str]:
        """Get list of all supported framework names."""
        return list(self._tool_call_patterns.keys())
    
    def detect_framework_from_structure(self, data: Any) -> Optional[str]:
        """Detect framework based on data structure patterns."""
        if not isinstance(data, dict):
            return None
        
        data_str = str(data).lower()
        
        # Check each framework's structure patterns
        for framework, patterns in self._structure_patterns.items():
            for pattern in patterns:
                if pattern.search(data_str):
                    return framework
        
        return None
    
    def detect_framework_from_failure(self, data: Dict[str, Any]) -> Optional[str]:
        """Detect framework from failure patterns."""
        for framework, indicators in self._failure_patterns.items():
            if framework == "generic":
                continue
                
            # Check for framework-specific failure patterns
            if framework == "langchain" and "intermediate_steps" in data and data.get("error"):
                return framework
            elif framework == "crewai" and "crew_output" in data and data.get("execution_error"):
                return framework
            elif framework in ["openai", "anthropic"] and "error" in data:
                # Could be either, need more specific detection
                continue
        
        return None


# Global instance for easy access
framework_patterns = FrameworkPatterns()
