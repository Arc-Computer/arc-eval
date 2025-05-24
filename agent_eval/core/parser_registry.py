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
        
        # CrewAI detection
        if "crew_output" in data or "task_results" in data:
            return "crewai"
        elif "agent_responses" in data:
            return "crewai"
        
        # Generic output detection
        if "output" in data:
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
        else:
            return str(data)


def detect_and_extract(data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> tuple[Optional[str], str]:
    """
    Convenience function to detect framework and extract output.
    
    Args:
        data: Raw agent output data
        
    Returns:
        (framework_name, extracted_output)
    """
    framework = FrameworkDetector.detect_framework(data)
    output = OutputExtractor.extract_output(data, framework or "generic")
    return framework, output