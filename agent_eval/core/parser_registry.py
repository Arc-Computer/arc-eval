"""
Enhanced framework detection and parsing for agent outputs.

Supports multiple agent frameworks with automatic detection and normalization.
"""

from typing import Dict, Any, Optional, List, Union
import logging

logger = logging.getLogger(__name__)


class FrameworkDetector:
    """Advanced framework detection for agent outputs."""
    
    @staticmethod
    def detect_framework(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Optional[str]:
        """
        Detect the agent framework from output data structure.
        
        Args:
            data: Raw agent output data
            
        Returns:
            Framework name or None if not detected
        """
        if isinstance(data, list) and len(data) > 0:
            # Check first item in list for framework patterns
            data = data[0]
        
        if not isinstance(data, dict):
            return None
        
        # Direct framework field detection (highest priority)
        if "framework" in data:
            framework = str(data["framework"]).lower()
            # Normalize common framework names
            if framework in ["langchain", "langgraph", "crewai", "autogen", "openai", 
                           "anthropic", "agno", "google_adk", "nvidia_aiq"]:
                return framework
        
        # AutoGen detection - Microsoft's multi-agent framework
        if "messages" in data and "summary" in data:
            if isinstance(data["messages"], list) and len(data["messages"]) > 0:
                if any("author" in msg for msg in data["messages"] if isinstance(msg, dict)):
                    return "autogen"
        
        # Agno detection - Phidata's lightweight framework
        if "structured_output" in data and "agent_run_id" in data:
            return "agno"
        elif "response" in data and "tools_used" in data:
            return "agno"
            
        # Google ADK detection - Google's Agent Development Kit
        if "author" in data and "content" in data:
            if isinstance(data["content"], dict) and "parts" in data["content"]:
                if isinstance(data["content"]["parts"], list):
                    return "google_adk"
        
        # NVIDIA AIQ detection - Agent Intelligence Toolkit
        if "workflow_output" in data and "agent_state" in data:
            return "nvidia_aiq"
        elif "input_message" in data and "workflow_output" in data:
            return "nvidia_aiq"
            
        # LangGraph detection (vs legacy LangChain)
        if "messages" in data and "graph_state" in data:
            return "langgraph"
        elif "messages" in data and isinstance(data["messages"], list):
            # Check for LangGraph message format
            if len(data["messages"]) > 0:
                msg = data["messages"][0]
                if isinstance(msg, dict) and "type" in msg and msg["type"] in ["human", "ai", "system"]:
                    return "langgraph"
        
        # OpenAI detection - OpenAI API format
        if "choices" in data and "message" in data.get("choices", [{}])[0]:
            return "openai"
        elif "choices" in data and isinstance(data["choices"], list):
            return "openai"
            
        # Anthropic detection - Claude API format
        if "content" in data and ("stop_reason" in data or "model" in data):
            return "anthropic"
        elif "content" in data and isinstance(data["content"], list):
            if len(data["content"]) > 0 and "type" in data["content"][0]:
                return "anthropic"
        
        # Legacy LangChain detection
        if "llm_output" in data:
            return "langchain"
        elif "agent_scratchpad" in data or "tool_calls" in data:
            return "langchain"
        elif "tool_call" in data and isinstance(data.get("tool_call"), dict):
            # LangChain workflow trace format
            if "name" in data["tool_call"] and "parameters" in data["tool_call"]:
                return "langchain"
        
        # CrewAI detection
        if "crew_output" in data or "task_results" in data:
            return "crewai"
        elif "agent_responses" in data:
            return "crewai"
        
        # Generic output detection
        if "output" in data:
            return "generic"
        elif "scenario_id" in data and "output" in data:
            return "generic"
        elif "metadata" in data and isinstance(data.get("metadata"), dict):
            # Check if this looks like a simple agent output with metadata
            return "generic"
        
        logger.debug(f"No framework detected for data keys: {list(data.keys())}")
        return None


class OutputExtractor:
    """Extract normalized output text from framework-specific data structures."""
    
    @staticmethod
    def extract_output(data: Union[Dict[str, Any], List[Dict[str, Any]]], framework: str) -> str:
        """
        Extract normalized output text from framework data.
        
        Args:
            data: Framework-specific data structure
            framework: Detected framework name
            
        Returns:
            Normalized output text
        """
        try:
            if isinstance(data, list) and len(data) > 0:
                # For list inputs, process each item and concatenate
                outputs = []
                for item in data:
                    if isinstance(item, dict):
                        extracted = OutputExtractor._extract_single(item, framework)
                        if extracted:
                            outputs.append(extracted)
                return " ".join(outputs) if outputs else str(data)
            else:
                return OutputExtractor._extract_single(data, framework)
        except Exception as e:
            logger.error(f"Error extracting output from {framework}: {e}")
            return str(data)
    
    @staticmethod
    def _extract_single(data: Dict[str, Any], framework: str) -> str:
        """Extract output from a single data object."""
        extractors = {
            "autogen": OutputExtractor._extract_autogen,
            "agno": OutputExtractor._extract_agno,
            "google_adk": OutputExtractor._extract_google_adk,
            "nvidia_aiq": OutputExtractor._extract_nvidia_aiq,
            "langgraph": OutputExtractor._extract_langgraph,
            "openai": OutputExtractor._extract_openai,
            "anthropic": OutputExtractor._extract_anthropic,
            "langchain": OutputExtractor._extract_langchain,
            "crewai": OutputExtractor._extract_crewai,
            "generic": OutputExtractor._extract_generic,
        }
        
        extractor = extractors.get(framework, OutputExtractor._extract_generic)
        return extractor(data)
    
    @staticmethod
    def _extract_autogen(data: Dict[str, Any]) -> str:
        """Extract output from AutoGen format."""
        if "messages" in data and isinstance(data["messages"], list):
            messages = data["messages"]
            if messages:
                last_message = messages[-1]
                if isinstance(last_message, dict) and "content" in last_message:
                    return str(last_message["content"])
        return str(data)
    
    @staticmethod
    def _extract_agno(data: Dict[str, Any]) -> str:
        """Extract output from Agno format."""
        if "response" in data:
            return str(data["response"])
        elif "output" in data:
            return str(data["output"])
        return str(data)
    
    @staticmethod
    def _extract_google_adk(data: Dict[str, Any]) -> str:
        """Extract output from Google ADK format."""
        if "content" in data and isinstance(data["content"], dict):
            parts = data["content"].get("parts", [])
            if isinstance(parts, list) and parts:
                text_parts = []
                for part in parts:
                    if isinstance(part, dict) and "text" in part:
                        text_parts.append(str(part["text"]))
                return " ".join(text_parts) if text_parts else str(data)
        return str(data)
    
    @staticmethod
    def _extract_nvidia_aiq(data: Dict[str, Any]) -> str:
        """Extract output from NVIDIA AIQ format."""
        if "workflow_output" in data:
            return str(data["workflow_output"])
        elif "agent_state" in data and isinstance(data["agent_state"], dict):
            state = data["agent_state"]
            if "observation" in state:
                return str(state["observation"])
            elif "thought" in state:
                return str(state["thought"])
        return str(data)
    
    @staticmethod
    def _extract_langgraph(data: Dict[str, Any]) -> str:
        """Extract output from LangGraph format."""
        if "messages" in data and isinstance(data["messages"], list):
            messages = data["messages"]
            # Find the last AI message
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("type") == "ai":
                    return str(msg.get("content", ""))
            # Fallback to last message
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, dict):
                    return str(last_msg.get("content", ""))
        return str(data)
    
    @staticmethod
    def _extract_openai(data: Dict[str, Any]) -> str:
        """Extract output from OpenAI format."""
        if "choices" in data and isinstance(data["choices"], list):
            choices = data["choices"]
            if choices and "message" in choices[0]:
                message = choices[0]["message"]
                if isinstance(message, dict) and "content" in message:
                    return str(message["content"])
        return str(data)
    
    @staticmethod
    def _extract_anthropic(data: Dict[str, Any]) -> str:
        """Extract output from Anthropic format."""
        if "content" in data:
            content = data["content"]
            if isinstance(content, list):
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text_parts.append(str(block.get("text", "")))
                return " ".join(text_parts) if text_parts else str(content)
            else:
                return str(content)
        return str(data)
    
    @staticmethod
    def _extract_langchain(data: Dict[str, Any]) -> str:
        """Extract output from legacy LangChain format."""
        if "llm_output" in data:
            return str(data["llm_output"])
        elif "output" in data:
            return str(data["output"])
        return str(data)
    
    @staticmethod
    def _extract_crewai(data: Dict[str, Any]) -> str:
        """Extract output from CrewAI format."""
        if "crew_output" in data:
            return str(data["crew_output"])
        elif "task_results" in data:
            return str(data["task_results"])
        elif "agent_responses" in data:
            return str(data["agent_responses"])
        return str(data)
    
    @staticmethod
    def _extract_generic(data: Dict[str, Any]) -> str:
        """Extract output from generic format."""
        if "output" in data:
            return str(data["output"])
        elif "text" in data:
            return str(data["text"])
        elif "content" in data:
            return str(data["content"])
        elif "response" in data:
            return str(data["response"])
        elif "result" in data:
            return str(data["result"])
        elif "answer" in data:
            return str(data["answer"])
        else:
            # If no standard fields found, check for a scenario/metadata pattern
            if "scenario_id" in data and "metadata" in data:
                # Look for any field that might contain the output
                for key, value in data.items():
                    if key not in ["scenario_id", "metadata", "timestamp", "agent_id"]:
                        return str(value)
            return str(data)


class ToolCallExtractor:
    """Extract tool calls from framework-specific data structures."""
    
    @staticmethod
    def extract_tool_calls(data: Union[Dict[str, Any], List[Dict[str, Any]]], framework: str) -> List[str]:
        """
        Extract tool calls from framework data.
        
        Args:
            data: Framework-specific data structure
            framework: Detected framework name
            
        Returns:
            List of tool names that were called
        """
        try:
            if isinstance(data, list) and len(data) > 0:
                # For list inputs, process each item and combine tool calls
                all_tools = []
                for item in data:
                    if isinstance(item, dict):
                        tools = ToolCallExtractor._extract_tools_single(item, framework)
                        all_tools.extend(tools)
                return list(dict.fromkeys(all_tools))  # Remove duplicates while preserving order
            else:
                return ToolCallExtractor._extract_tools_single(data, framework)
        except Exception as e:
            logger.error(f"Error extracting tool calls from {framework}: {e}")
            return []
    
    @staticmethod
    def _extract_tools_single(data: Dict[str, Any], framework: str) -> List[str]:
        """Extract tool calls from a single data object."""
        extractors = {
            "autogen": ToolCallExtractor._extract_tools_autogen,
            "agno": ToolCallExtractor._extract_tools_agno,
            "google_adk": ToolCallExtractor._extract_tools_google_adk,
            "nvidia_aiq": ToolCallExtractor._extract_tools_nvidia_aiq,
            "langgraph": ToolCallExtractor._extract_tools_langgraph,
            "openai": ToolCallExtractor._extract_tools_openai,
            "anthropic": ToolCallExtractor._extract_tools_anthropic,
            "langchain": ToolCallExtractor._extract_tools_langchain,
            "crewai": ToolCallExtractor._extract_tools_crewai,
            "generic": ToolCallExtractor._extract_tools_generic,
        }
        
        extractor = extractors.get(framework, ToolCallExtractor._extract_tools_generic)
        return extractor(data)
    
    @staticmethod
    def _extract_tools_autogen(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from AutoGen format."""
        tools = []
        if "messages" in data and isinstance(data["messages"], list):
            for message in data["messages"]:
                if isinstance(message, dict):
                    # Check for function calls in message content
                    content = str(message.get("content", ""))
                    if "function_call" in content or "tool_call" in content:
                        # Extract function names from content
                        import re
                        matches = re.findall(r'"name":\s*"([^"]+)"', content)
                        tools.extend(matches)
        return [tool.lower() for tool in tools]
    
    @staticmethod
    def _extract_tools_agno(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from Agno format."""
        tools = []
        if "tools_used" in data and isinstance(data["tools_used"], list):
            tools.extend([str(tool).lower() for tool in data["tools_used"]])
        elif "function_calls" in data:
            calls = data["function_calls"]
            if isinstance(calls, list):
                for call in calls:
                    if isinstance(call, dict) and "name" in call:
                        tools.append(str(call["name"]).lower())
        return tools
    
    @staticmethod
    def _extract_tools_google_adk(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from Google ADK format."""
        tools = []
        if "content" in data and isinstance(data["content"], dict):
            parts = data["content"].get("parts", [])
            for part in parts:
                if isinstance(part, dict) and "functionCall" in part:
                    func_call = part["functionCall"]
                    if isinstance(func_call, dict) and "name" in func_call:
                        tools.append(str(func_call["name"]).lower())
        return tools
    
    @staticmethod
    def _extract_tools_nvidia_aiq(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from NVIDIA AIQ format."""
        tools = []
        if "workflow_output" in data:
            output = str(data["workflow_output"])
            # Look for tool execution patterns in output
            import re
            matches = re.findall(r'(?:tool|action|execute):\s*([a-zA-Z_][a-zA-Z0-9_]*)', output, re.IGNORECASE)
            tools.extend([match.lower() for match in matches])
        return tools
    
    @staticmethod
    def _extract_tools_langgraph(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from LangGraph format."""
        tools = []
        if "messages" in data and isinstance(data["messages"], list):
            for message in data["messages"]:
                if isinstance(message, dict):
                    # Check for tool calls in message
                    if "tool_calls" in message and isinstance(message["tool_calls"], list):
                        for tool_call in message["tool_calls"]:
                            if isinstance(tool_call, dict) and "function" in tool_call:
                                func = tool_call["function"]
                                if isinstance(func, dict) and "name" in func:
                                    tools.append(str(func["name"]).lower())
        return tools
    
    @staticmethod
    def _extract_tools_openai(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from OpenAI format."""
        tools = []
        if "choices" in data and isinstance(data["choices"], list):
            for choice in data["choices"]:
                if isinstance(choice, dict) and "message" in choice:
                    message = choice["message"]
                    if isinstance(message, dict):
                        # Check for tool calls
                        if "tool_calls" in message and isinstance(message["tool_calls"], list):
                            for tool_call in message["tool_calls"]:
                                if isinstance(tool_call, dict) and "function" in tool_call:
                                    func = tool_call["function"]
                                    if isinstance(func, dict) and "name" in func:
                                        tools.append(str(func["name"]).lower())
                        # Check for function call (legacy format)
                        elif "function_call" in message:
                            func_call = message["function_call"]
                            if isinstance(func_call, dict) and "name" in func_call:
                                tools.append(str(func_call["name"]).lower())
        return tools
    
    @staticmethod
    def _extract_tools_anthropic(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from Anthropic format."""
        tools = []
        if "content" in data and isinstance(data["content"], list):
            for block in data["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    if "name" in block:
                        tools.append(str(block["name"]).lower())
        return tools
    
    @staticmethod
    def _extract_tools_langchain(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from legacy LangChain format."""
        tools = []
        if "tool_calls" in data and isinstance(data["tool_calls"], list):
            for tool_call in data["tool_calls"]:
                if isinstance(tool_call, dict) and "tool" in tool_call:
                    tools.append(str(tool_call["tool"]).lower())
        elif "intermediate_steps" in data and isinstance(data["intermediate_steps"], list):
            for step in data["intermediate_steps"]:
                if isinstance(step, tuple) and len(step) >= 2:
                    # LangChain intermediate steps format: (AgentAction, observation)
                    action = step[0]
                    if hasattr(action, "tool"):
                        tools.append(str(action.tool).lower())
        return tools
    
    @staticmethod
    def _extract_tools_crewai(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from CrewAI format."""
        tools = []
        if "task_results" in data and isinstance(data["task_results"], list):
            for result in data["task_results"]:
                if isinstance(result, dict) and "tools_used" in result:
                    if isinstance(result["tools_used"], list):
                        tools.extend([str(tool).lower() for tool in result["tools_used"]])
        elif "tools_used" in data and isinstance(data["tools_used"], list):
            tools.extend([str(tool).lower() for tool in data["tools_used"]])
        return tools
    
    @staticmethod
    def _extract_tools_generic(data: Dict[str, Any]) -> List[str]:
        """Extract tool calls from generic format using text parsing."""
        tools = []
        # Convert entire data to string and look for tool patterns
        content = str(data)
        
        # Use reliability validator patterns for generic tool extraction
        from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
        validator = ReliabilityAnalyzer()
        detected_tools = validator.extract_tool_calls(content)
        tools.extend(detected_tools)
        
        return tools


def detect_and_extract(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> tuple[Optional[str], str]:
    """
    Convenience function to detect framework and extract output.
    
    Args:
        data: Raw agent output data
        
    Returns:
        (framework_name, extracted_output)
    """
    # Early validation to prevent error spam from invalid inputs
    if data is None:
        return None, "None"
    
    # Handle simple string inputs
    if isinstance(data, str):
        return None, data.strip()
    
    # Handle numeric and other simple types
    if not isinstance(data, (dict, list)):
        return None, str(data)
    
    # Handle empty containers
    if len(data) == 0:
        return None, str(data)
    
    # Proceed with framework detection for valid structured data
    framework = FrameworkDetector.detect_framework(data)
    output = OutputExtractor.extract_output(data, framework or "generic")
    return framework, output


def detect_and_extract_tools(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> tuple[Optional[str], List[str]]:
    """
    Convenience function to detect framework and extract tool calls.
    
    Args:
        data: Raw agent output data
        
    Returns:
        (framework_name, list_of_tool_calls)
    """
    # Early validation to prevent error spam from invalid inputs
    if data is None:
        return None, []
    
    # Handle simple string inputs with generic tool extraction
    if isinstance(data, str):
        from agent_eval.evaluation.reliability_validator import ReliabilityAnalyzer
        validator = ReliabilityAnalyzer()
        tools = validator.extract_tool_calls(data)
        return None, tools
    
    # Handle numeric and other simple types
    if not isinstance(data, (dict, list)):
        return None, []
    
    # Handle empty containers
    if len(data) == 0:
        return None, []
    
    # Proceed with framework detection for valid structured data
    framework = FrameworkDetector.detect_framework(data)
    tools = ToolCallExtractor.extract_tool_calls(data, framework or "generic")
    return framework, tools
