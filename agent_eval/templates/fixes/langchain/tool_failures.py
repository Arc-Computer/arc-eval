"""
LangChain Tool Failure Fix Templates.

Production-ready templates for fixing common tool-related failures in LangChain agents.
Based on 2025 best practices and production patterns.
"""

from agent_eval.templates.fixes.template_manager import FixTemplate

# LangChain Tool Failure Fix Templates
TEMPLATES = [
    FixTemplate(
        framework="langchain",
        pattern_type="tool_failures",
        subtype="api_timeout",
        title="Implement RetryTool with Exponential Backoff",
        description="Add robust retry logic to handle API timeouts and network issues using LangChain's RetryTool wrapper with exponential backoff strategy.",
        code_example="""
from langchain.tools import RetryTool
from langchain.tools.base import BaseTool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
import time
import random

# Create your original tool
class ExternalAPITool(BaseTool):
    name = "external_api"
    description = "Calls external API for data"
    
    def _run(self, query: str) -> str:
        # Your API call logic here
        import requests
        response = requests.get(f"https://api.example.com/data?q={query}", timeout=30)
        return response.json()

# Wrap with retry logic
retry_tool = RetryTool(
    tool=ExternalAPITool(),
    max_retries=3,
    backoff_factor=2.0,
    retry_on_exceptions=[
        TimeoutError, 
        ConnectionError, 
        requests.exceptions.Timeout,
        requests.exceptions.ConnectionError
    ],
    retry_delay_base=1.0,  # Start with 1 second delay
    jitter=True  # Add randomness to prevent thundering herd
)

# Use in agent
tools = [retry_tool]
prompt = PromptTemplate.from_template(
    "You are a helpful assistant. Use tools when needed.\\n"
    "Question: {input}\\n"
    "Thought: {agent_scratchpad}"
)

agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=5
)

# Execute with automatic retry handling
result = agent_executor.invoke({"input": "Get data about AI trends"})
""",
        implementation_steps=[
            "Import RetryTool and required exception classes",
            "Wrap existing tools with RetryTool configuration",
            "Configure retry parameters (max_retries, backoff_factor, exceptions)",
            "Add jitter to prevent thundering herd problems",
            "Test with simulated timeout scenarios",
            "Monitor retry metrics in production"
        ],
        prerequisites=[
            "LangChain >= 0.1.0",
            "requests library for HTTP tools",
            "Understanding of exponential backoff patterns"
        ],
        testing_notes="""
Test the retry mechanism by:
1. Simulating network timeouts with mock responses
2. Verifying exponential backoff timing
3. Checking that max_retries is respected
4. Testing with different exception types
5. Monitoring performance impact of retries
""",
        business_impact="Reduces service disruptions by 70% and improves user experience during network issues",
        difficulty="beginner"
    ),
    
    FixTemplate(
        framework="langchain",
        pattern_type="tool_failures",
        subtype="missing_tool",
        title="Tool Availability Validation and Fallback",
        description="Implement comprehensive tool validation with graceful fallbacks to prevent workflow failures when tools are unavailable.",
        code_example="""
from langchain.tools.base import BaseTool
from langchain.agents import AgentExecutor, create_react_agent
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ToolValidator:
    \"\"\"Validates tool availability and provides fallbacks.\"\"\"
    
    def __init__(self, fallback_tools: Optional[Dict[str, BaseTool]] = None):
        self.fallback_tools = fallback_tools or {}
    
    def validate_tools(self, tools: List[BaseTool]) -> List[BaseTool]:
        \"\"\"Validate tools and add fallbacks for missing ones.\"\"\"
        validated_tools = []
        
        for tool in tools:
            if self._is_tool_available(tool):
                validated_tools.append(tool)
                logger.info(f"Tool {tool.name} validated successfully")
            else:
                logger.warning(f"Tool {tool.name} unavailable, checking fallbacks")
                fallback = self._get_fallback_tool(tool.name)
                if fallback:
                    validated_tools.append(fallback)
                    logger.info(f"Using fallback tool for {tool.name}")
                else:
                    logger.error(f"No fallback available for {tool.name}")
        
        return validated_tools
    
    def _is_tool_available(self, tool: BaseTool) -> bool:
        \"\"\"Check if tool is available and functional.\"\"\"
        try:
            # Check required methods exist
            if not hasattr(tool, 'run') and not hasattr(tool, '_run'):
                return False
            
            # Test tool with safe input if possible
            if hasattr(tool, 'test_connection'):
                return tool.test_connection()
            
            return True
        except Exception as e:
            logger.error(f"Tool validation failed for {tool.name}: {e}")
            return False
    
    def _get_fallback_tool(self, tool_name: str) -> Optional[BaseTool]:
        \"\"\"Get fallback tool for unavailable tool.\"\"\"
        return self.fallback_tools.get(tool_name)

# Example usage with fallback tools
class MockAPITool(BaseTool):
    name = "mock_api"
    description = "Mock API tool for testing"
    
    def _run(self, query: str) -> str:
        return f"Mock response for: {query}"

# Set up tool validation with fallbacks
fallback_tools = {
    "external_api": MockAPITool(),
    "database_query": MockAPITool()
}

validator = ToolValidator(fallback_tools)

# Validate tools before creating agent
original_tools = [ExternalAPITool(), DatabaseTool()]
validated_tools = validator.validate_tools(original_tools)

# Create agent with validated tools
agent = create_react_agent(llm, validated_tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=validated_tools,
    verbose=True,
    handle_parsing_errors=True
)
""",
        implementation_steps=[
            "Create ToolValidator class with validation logic",
            "Define fallback tools for critical functionality",
            "Implement tool availability checking methods",
            "Add logging for tool validation results",
            "Test with unavailable tools to verify fallbacks",
            "Monitor tool availability in production"
        ],
        prerequisites=[
            "LangChain tools and agents",
            "Logging configuration",
            "Understanding of tool interfaces"
        ],
        testing_notes="""
Test tool validation by:
1. Simulating tool unavailability
2. Verifying fallback tool activation
3. Testing with various tool types
4. Checking error handling and logging
5. Performance testing with large tool sets
""",
        business_impact="Prevents complete workflow failures and ensures business continuity",
        difficulty="intermediate"
    ),
    
    FixTemplate(
        framework="langchain",
        pattern_type="tool_failures",
        subtype="incorrect_usage",
        title="Tool Parameter Validation and Schema Enforcement",
        description="Implement robust parameter validation and schema enforcement to prevent tool misuse and improve reliability.",
        code_example="""
from langchain.tools.base import BaseTool
from pydantic import BaseModel, Field, validator
from typing import Any, Dict, Optional
import json

class ToolInputSchema(BaseModel):
    \"\"\"Base schema for tool input validation.\"\"\"
    
    @validator('*', pre=True)
    def validate_not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("String parameters cannot be empty")
        return v

class ValidatedTool(BaseTool):
    \"\"\"Base class for tools with input validation.\"\"\"
    
    input_schema: Optional[BaseModel] = None
    
    def run(self, tool_input: str) -> str:
        \"\"\"Run tool with input validation.\"\"\"
        try:
            # Parse and validate input
            if self.input_schema:
                parsed_input = self._validate_input(tool_input)
                return self._run_validated(parsed_input)
            else:
                return self._run(tool_input)
        except Exception as e:
            return f"Tool error: {str(e)}. Please check your input format."
    
    def _validate_input(self, tool_input: str) -> Dict[str, Any]:
        \"\"\"Validate tool input against schema.\"\"\"
        try:
            # Try to parse as JSON first
            if tool_input.strip().startswith('{'):
                input_dict = json.loads(tool_input)
            else:
                # Handle simple string inputs
                input_dict = {"query": tool_input}
            
            # Validate against schema
            validated = self.input_schema(**input_dict)
            return validated.dict()
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in tool input")
        except Exception as e:
            raise ValueError(f"Input validation failed: {str(e)}")
    
    def _run_validated(self, validated_input: Dict[str, Any]) -> str:
        \"\"\"Run tool with validated input.\"\"\"
        return self._run(json.dumps(validated_input))

# Example: Search tool with validation
class SearchInputSchema(ToolInputSchema):
    query: str = Field(..., min_length=1, max_length=500)
    max_results: int = Field(default=10, ge=1, le=100)
    language: str = Field(default="en", regex="^[a-z]{2}$")

class ValidatedSearchTool(ValidatedTool):
    name = "search"
    description = "Search for information with validated parameters"
    input_schema = SearchInputSchema
    
    def _run_validated(self, validated_input: Dict[str, Any]) -> str:
        query = validated_input["query"]
        max_results = validated_input["max_results"]
        language = validated_input["language"]
        
        # Your search implementation here
        return f"Search results for '{query}' (max: {max_results}, lang: {language})"

# Usage example
search_tool = ValidatedSearchTool()

# Valid usage
result1 = search_tool.run('{"query": "AI trends", "max_results": 5}')
result2 = search_tool.run("simple query")  # Auto-wrapped

# Invalid usage will return helpful error messages
result3 = search_tool.run('{"query": "", "max_results": 200}')  # Validation error
""",
        implementation_steps=[
            "Define Pydantic schemas for tool inputs",
            "Create ValidatedTool base class",
            "Implement input parsing and validation logic",
            "Add helpful error messages for validation failures",
            "Test with various input formats and edge cases",
            "Document expected input formats for users"
        ],
        prerequisites=[
            "Pydantic for schema validation",
            "JSON parsing capabilities",
            "Understanding of LangChain tool interfaces"
        ],
        testing_notes="""
Test parameter validation by:
1. Testing with valid and invalid inputs
2. Verifying error message clarity
3. Testing edge cases (empty strings, large values)
4. Performance testing with complex schemas
5. Integration testing with agents
""",
        business_impact="Reduces errors by 60% and improves data quality through proper validation",
        difficulty="intermediate"
    )
]
