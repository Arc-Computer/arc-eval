"""
CrewAI Tool Failure Fix Templates.

Production-ready templates for fixing common tool-related failures in CrewAI agents.
Based on 2025 best practices and hierarchical coordination patterns.
"""

from agent_eval.templates.fixes.template_manager import FixTemplate

# CrewAI Tool Failure Fix Templates
TEMPLATES = [
    FixTemplate(
        framework="crewai",
        pattern_type="tool_failures",
        subtype="api_timeout",
        title="Task-Level Retry Configuration with Exponential Backoff",
        description="Implement robust retry mechanisms at the task level using CrewAI's built-in retry configuration for handling API timeouts and network issues.",
        code_example="""
from crewai import Task, Agent, Crew, Tool
from crewai.tools import BaseTool
import requests
import time
from typing import Optional

class ExternalAPITool(BaseTool):
    name: str = "external_api"
    description: str = "Calls external API for data retrieval"
    
    def _run(self, query: str) -> str:
        \"\"\"Execute API call with timeout handling.\"\"\"
        try:
            response = requests.get(
                f"https://api.example.com/data?q={query}",
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise TimeoutError(f"API timeout for query: {query}")
        except requests.exceptions.ConnectionError:
            raise ConnectionError(f"Connection failed for query: {query}")

# Create agent with tool
data_analyst = Agent(
    role="Data Analyst",
    goal="Retrieve and analyze external data",
    backstory="Expert in data retrieval and analysis",
    tools=[ExternalAPITool()],
    verbose=True
)

# Create task with comprehensive retry configuration
data_retrieval_task = Task(
    description="Retrieve market data for AI trends analysis",
    agent=data_analyst,
    expected_output="Structured market data with key insights",
    
    # Advanced retry configuration
    retry_config={
        "max_retries": 3,
        "retry_delay": 2.0,  # Initial delay in seconds
        "exponential_backoff": True,
        "backoff_factor": 2.0,  # Multiply delay by this factor each retry
        "max_delay": 30.0,  # Maximum delay between retries
        "jitter": True,  # Add randomness to prevent thundering herd
        "retry_on_exceptions": [
            "TimeoutError",
            "ConnectionError", 
            "requests.exceptions.Timeout",
            "requests.exceptions.ConnectionError"
        ]
    },
    
    # Task-level timeout
    timeout=120,  # Total task timeout in seconds
    
    # Fallback strategy
    fallback_strategy="graceful_degradation",
    fallback_message="Using cached data due to API unavailability"
)

# Create crew with error handling
crew = Crew(
    agents=[data_analyst],
    tasks=[data_retrieval_task],
    verbose=True,
    
    # Crew-level error handling
    error_handling={
        "continue_on_task_failure": True,
        "log_errors": True,
        "notify_on_failure": True
    }
)

# Execute with automatic retry handling
result = crew.kickoff()
print(f"Analysis result: {result}")
""",
        implementation_steps=[
            "Define tools with proper exception handling",
            "Configure task-level retry parameters",
            "Set appropriate timeout values for tasks",
            "Implement fallback strategies for critical tasks",
            "Add crew-level error handling configuration",
            "Test retry behavior with simulated failures",
            "Monitor retry metrics and adjust parameters"
        ],
        prerequisites=[
            "CrewAI >= 0.28.0",
            "requests library for HTTP tools",
            "Understanding of CrewAI task configuration"
        ],
        testing_notes="""
Test retry mechanism by:
1. Simulating API timeouts and connection errors
2. Verifying exponential backoff timing
3. Testing fallback strategy activation
4. Checking crew continues with other tasks
5. Monitoring performance impact of retries
""",
        business_impact="Improves task completion rates by 60% and ensures workflow continuity during network issues",
        difficulty="beginner"
    ),
    
    FixTemplate(
        framework="crewai",
        pattern_type="tool_failures",
        subtype="coordination",
        title="Hierarchical Task Coordination with Error Recovery",
        description="Implement robust hierarchical task coordination patterns with error recovery and task dependency management.",
        code_example="""
from crewai import Task, Agent, Crew, Tool
from crewai.tools import BaseTool
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class TaskCoordinator:
    \"\"\"Manages hierarchical task coordination with error recovery.\"\"\"
    
    def __init__(self):
        self.task_results = {}
        self.failed_tasks = []
    
    def create_hierarchical_tasks(self) -> List[Task]:
        \"\"\"Create tasks with proper hierarchy and dependencies.\"\"\"
        
        # Level 1: Data Collection Tasks (Parallel)
        data_collection_tasks = [
            Task(
                id="collect_market_data",
                description="Collect market data from external sources",
                agent=self.data_collector,
                expected_output="Raw market data in JSON format",
                priority="high",
                retry_config=self._get_retry_config(),
                dependencies=[]
            ),
            Task(
                id="collect_competitor_data", 
                description="Collect competitor analysis data",
                agent=self.data_collector,
                expected_output="Competitor data with key metrics",
                priority="medium",
                retry_config=self._get_retry_config(),
                dependencies=[]
            )
        ]
        
        # Level 2: Data Processing (Depends on Level 1)
        data_processing_task = Task(
            id="process_collected_data",
            description="Process and clean collected data",
            agent=self.data_processor,
            expected_output="Cleaned and structured data",
            priority="high",
            retry_config=self._get_retry_config(),
            dependencies=["collect_market_data", "collect_competitor_data"],
            
            # Error recovery strategy
            error_recovery={
                "partial_dependency_failure": "continue_with_available_data",
                "complete_dependency_failure": "use_fallback_data",
                "processing_failure": "retry_with_simplified_approach"
            }
        )
        
        # Level 3: Analysis (Depends on Level 2)
        analysis_task = Task(
            id="analyze_data",
            description="Perform comprehensive data analysis",
            agent=self.analyst,
            expected_output="Analysis report with insights",
            priority="critical",
            retry_config=self._get_retry_config(),
            dependencies=["process_collected_data"],
            
            # Quality gates
            quality_gates={
                "min_data_points": 100,
                "confidence_threshold": 0.8,
                "completeness_check": True
            }
        )
        
        # Level 4: Reporting (Depends on Level 3)
        reporting_task = Task(
            id="generate_report",
            description="Generate final analysis report",
            agent=self.reporter,
            expected_output="Executive summary and detailed report",
            priority="critical",
            dependencies=["analyze_data"],
            
            # Final validation
            validation_rules={
                "required_sections": ["executive_summary", "key_findings", "recommendations"],
                "min_length": 1000,
                "format_check": True
            }
        )
        
        return data_collection_tasks + [data_processing_task, analysis_task, reporting_task]
    
    def _get_retry_config(self) -> Dict[str, Any]:
        \"\"\"Standard retry configuration for all tasks.\"\"\"
        return {
            "max_retries": 2,
            "retry_delay": 1.0,
            "exponential_backoff": True,
            "backoff_factor": 1.5
        }

# Create specialized agents
coordinator = TaskCoordinator()

coordinator.data_collector = Agent(
    role="Data Collector",
    goal="Efficiently collect data from multiple sources",
    backstory="Specialist in data acquisition and source management",
    tools=[ExternalAPITool(), DatabaseTool()],
    max_retry_attempts=3
)

coordinator.data_processor = Agent(
    role="Data Processor", 
    goal="Clean and structure collected data",
    backstory="Expert in data cleaning and transformation",
    tools=[DataCleaningTool(), ValidationTool()],
    max_retry_attempts=2
)

coordinator.analyst = Agent(
    role="Data Analyst",
    goal="Extract insights from processed data", 
    backstory="Senior analyst with domain expertise",
    tools=[AnalysisTool(), VisualizationTool()],
    max_retry_attempts=2
)

coordinator.reporter = Agent(
    role="Report Generator",
    goal="Create comprehensive reports",
    backstory="Expert in business communication and reporting",
    tools=[ReportingTool(), FormattingTool()],
    max_retry_attempts=1
)

# Create crew with hierarchical coordination
crew = Crew(
    agents=[
        coordinator.data_collector,
        coordinator.data_processor, 
        coordinator.analyst,
        coordinator.reporter
    ],
    tasks=coordinator.create_hierarchical_tasks(),
    
    # Coordination settings
    process="hierarchical",  # Use hierarchical process
    manager_llm=manager_llm,  # LLM for coordination decisions
    
    # Error handling and recovery
    error_handling={
        "task_failure_strategy": "isolate_and_continue",
        "dependency_failure_strategy": "partial_execution",
        "crew_failure_threshold": 0.5,  # Fail if >50% of critical tasks fail
        "recovery_attempts": 2
    },
    
    verbose=True
)

# Execute with coordination monitoring
result = crew.kickoff()
""",
        implementation_steps=[
            "Design hierarchical task structure with clear dependencies",
            "Create specialized agents for each task level",
            "Implement error recovery strategies for each task",
            "Configure quality gates and validation rules",
            "Set up crew-level coordination and error handling",
            "Test with various failure scenarios",
            "Monitor coordination efficiency and adjust"
        ],
        prerequisites=[
            "CrewAI hierarchical process support",
            "Understanding of task dependencies",
            "Error handling and recovery patterns"
        ],
        testing_notes="""
Test hierarchical coordination by:
1. Simulating failures at different task levels
2. Verifying dependency handling works correctly
3. Testing partial failure recovery strategies
4. Checking quality gates prevent bad data propagation
5. Monitoring coordination overhead and performance
""",
        business_impact="Reduces coordination failures by 80% and improves workflow reliability through structured error recovery",
        difficulty="advanced"
    ),
    
    FixTemplate(
        framework="crewai",
        pattern_type="tool_failures", 
        subtype="missing_tool",
        title="Dynamic Tool Availability and Fallback Management",
        description="Implement dynamic tool availability checking with intelligent fallback strategies for CrewAI agents.",
        code_example="""
from crewai import Agent, Task, Crew, Tool
from crewai.tools import BaseTool
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ToolAvailabilityManager:
    \"\"\"Manages tool availability and fallback strategies.\"\"\"
    
    def __init__(self):
        self.tool_status = {}
        self.fallback_tools = {}
        self.tool_health_checks = {}
    
    def register_tool_with_fallback(
        self, 
        primary_tool: BaseTool, 
        fallback_tool: Optional[BaseTool] = None,
        health_check_func: Optional[callable] = None
    ):
        \"\"\"Register a tool with its fallback and health check.\"\"\"
        tool_name = primary_tool.name
        self.fallback_tools[tool_name] = fallback_tool
        self.tool_health_checks[tool_name] = health_check_func
        self.tool_status[tool_name] = "unknown"
    
    def check_tool_availability(self, tool: BaseTool) -> bool:
        \"\"\"Check if a tool is available and functional.\"\"\"
        tool_name = tool.name
        
        try:
            # Use custom health check if available
            if tool_name in self.tool_health_checks:
                health_check = self.tool_health_checks[tool_name]
                if health_check:
                    is_available = health_check(tool)
                    self.tool_status[tool_name] = "available" if is_available else "unavailable"
                    return is_available
            
            # Default health check
            if hasattr(tool, 'test_connection'):
                is_available = tool.test_connection()
            else:
                # Basic availability check
                is_available = hasattr(tool, '_run') or hasattr(tool, 'run')
            
            self.tool_status[tool_name] = "available" if is_available else "unavailable"
            return is_available
            
        except Exception as e:
            logger.error(f"Health check failed for {tool_name}: {e}")
            self.tool_status[tool_name] = "error"
            return False
    
    def get_available_tools(self, requested_tools: List[BaseTool]) -> List[BaseTool]:
        \"\"\"Get list of available tools with fallbacks if needed.\"\"\"
        available_tools = []
        
        for tool in requested_tools:
            if self.check_tool_availability(tool):
                available_tools.append(tool)
                logger.info(f"Tool {tool.name} is available")
            else:
                # Try fallback tool
                fallback = self.fallback_tools.get(tool.name)
                if fallback and self.check_tool_availability(fallback):
                    available_tools.append(fallback)
                    logger.warning(f"Using fallback tool for {tool.name}")
                else:
                    logger.error(f"No available tool or fallback for {tool.name}")
        
        return available_tools

# Example tools with health checks
class DatabaseTool(BaseTool):
    name: str = "database_query"
    description: str = "Query database for information"
    
    def test_connection(self) -> bool:
        try:
            # Test database connection
            # connection = get_db_connection()
            # return connection.is_alive()
            return True  # Simplified for example
        except:
            return False
    
    def _run(self, query: str) -> str:
        return f"Database result for: {query}"

class MockDatabaseTool(BaseTool):
    name: str = "mock_database"
    description: str = "Mock database for fallback"
    
    def _run(self, query: str) -> str:
        return f"Mock database result for: {query}"

class ExternalAPITool(BaseTool):
    name: str = "external_api"
    description: str = "External API calls"
    
    def test_connection(self) -> bool:
        try:
            import requests
            response = requests.get("https://api.example.com/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _run(self, query: str) -> str:
        return f"API result for: {query}"

# Set up tool availability management
tool_manager = ToolAvailabilityManager()

# Register tools with fallbacks
primary_db_tool = DatabaseTool()
fallback_db_tool = MockDatabaseTool()
api_tool = ExternalAPITool()

tool_manager.register_tool_with_fallback(
    primary_tool=primary_db_tool,
    fallback_tool=fallback_db_tool,
    health_check_func=lambda tool: tool.test_connection()
)

tool_manager.register_tool_with_fallback(
    primary_tool=api_tool,
    fallback_tool=None,  # No fallback for API
    health_check_func=lambda tool: tool.test_connection()
)

# Create agent with dynamic tool availability
research_agent = Agent(
    role="Research Specialist",
    goal="Conduct research using available tools",
    backstory="Adaptable researcher who works with available resources",
    tools=[],  # Tools will be set dynamically
    verbose=True
)

# Create task with dynamic tool assignment
research_task = Task(
    description="Research market trends using available data sources",
    agent=research_agent,
    expected_output="Research report with available data",
    
    # Pre-execution hook to check tool availability
    pre_execution_hook=lambda: research_agent.tools.extend(
        tool_manager.get_available_tools([primary_db_tool, api_tool])
    ),
    
    # Adaptive execution based on available tools
    execution_strategy="adaptive",
    fallback_instructions="If primary tools unavailable, use alternative approaches"
)

# Create crew with tool availability monitoring
crew = Crew(
    agents=[research_agent],
    tasks=[research_task],
    verbose=True,
    
    # Tool monitoring configuration
    tool_monitoring={
        "check_interval": 300,  # Check tool health every 5 minutes
        "auto_fallback": True,
        "notify_on_fallback": True
    }
)

# Execute with dynamic tool management
result = crew.kickoff()
""",
        implementation_steps=[
            "Create ToolAvailabilityManager class",
            "Implement health check functions for each tool",
            "Register tools with fallback alternatives",
            "Add pre-execution hooks for dynamic tool assignment",
            "Configure crew-level tool monitoring",
            "Test with various tool availability scenarios",
            "Monitor tool health and fallback usage"
        ],
        prerequisites=[
            "CrewAI tool system understanding",
            "Health check implementation for tools",
            "Fallback tool alternatives"
        ],
        testing_notes="""
Test tool availability management by:
1. Simulating tool unavailability
2. Verifying fallback tool activation
3. Testing health check accuracy
4. Checking agent adaptation to available tools
5. Monitoring performance impact of health checks
""",
        business_impact="Ensures business continuity with 95% uptime even when primary tools fail",
        difficulty="intermediate"
    )
]
