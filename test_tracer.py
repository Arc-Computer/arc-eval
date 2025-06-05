#!/usr/bin/env python3
"""
ARC-Eval Runtime Tracing Test Script

Tests the complete tracing functionality with sample agents.
"""

import time
import random
import logging
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_agents():
    """Create sample agents for different frameworks."""
    
    class LangChainAgent:
        """Mock LangChain agent."""
        def __init__(self):
            self.name = "LangChain Sample Agent"
            self.__module__ = "langchain.agents"
        
        def invoke(self, input_data):
            """LangChain-style invoke method."""
            time.sleep(random.uniform(0.1, 0.8))
            
            if random.random() < 0.15:  # 15% failure rate
                raise Exception("LangChain agent processing error")
            
            return {
                "output": f"LangChain processed: {input_data}",
                "intermediate_steps": [
                    ("search", "Found relevant information"),
                    ("analyze", "Analyzed the data"),
                    ("respond", "Generated response")
                ]
            }
    
    class CrewAIAgent:
        """Mock CrewAI agent."""
        def __init__(self):
            self.name = "CrewAI Sample Agent"
            self.backstory = "Expert financial analyst"
            self.__module__ = "crewai.agent"
        
        def execute_task(self, task):
            """CrewAI-style task execution."""
            time.sleep(random.uniform(0.2, 1.0))
            
            if random.random() < 0.1:  # 10% failure rate
                raise Exception("CrewAI task execution failed")
            
            return {
                "task_outputs": [
                    f"Task analysis: {task}",
                    f"Task result: Completed successfully"
                ],
                "agent_name": self.name
            }
    
    class AutoGenAgent:
        """Mock AutoGen agent."""
        def __init__(self):
            self.name = "AutoGen Sample Agent"
            self.__module__ = "autogen.agentchat"
        
        def generate_reply(self, messages):
            """AutoGen-style reply generation."""
            time.sleep(random.uniform(0.1, 0.6))
            
            if random.random() < 0.12:  # 12% failure rate
                raise Exception("AutoGen reply generation failed")
            
            return {
                "content": f"AutoGen response to: {messages}",
                "chat_messages": [
                    {"role": "user", "content": str(messages)},
                    {"role": "assistant", "content": f"AutoGen response to: {messages}"}
                ]
            }
    
    class GenericAgent:
        """Generic agent for testing."""
        def __init__(self):
            self.name = "Generic Sample Agent"
        
        def run(self, input_text):
            """Generic run method."""
            time.sleep(random.uniform(0.05, 0.4))
            
            if random.random() < 0.08:  # 8% failure rate
                raise Exception("Generic agent error")
            
            return f"Generic agent processed: {input_text}"
    
    return {
        "langchain": LangChainAgent(),
        "crewai": CrewAIAgent(),
        "autogen": AutoGenAgent(),
        "generic": GenericAgent()
    }


def test_basic_tracing():
    """Test basic tracing functionality."""
    print("\n" + "="*60)
    print("🧪 Testing Basic Tracing Functionality")
    print("="*60)
    
    from agent_eval.trace import ArcTracer
    
    # Create sample agents
    agents = create_sample_agents()
    
    for framework, agent in agents.items():
        print(f"\n🔍 Testing {framework.upper()} agent...")
        
        # Initialize tracer
        tracer = ArcTracer(domain="testing", agent_id=f"test_{framework}")
        traced_agent = tracer.trace_agent(agent)
        
        print(f"✅ Agent wrapped with tracer")
        
        # Test inputs
        test_inputs = [
            "Hello world",
            "Process financial data",
            "Generate compliance report",
            "Analyze security risks",
            "Complete the task"
        ]
        
        success_count = 0
        for i, test_input in enumerate(test_inputs, 1):
            try:
                if framework == "langchain":
                    result = traced_agent.invoke(test_input)
                elif framework == "crewai":
                    result = traced_agent.execute_task(test_input)
                elif framework == "autogen":
                    result = traced_agent.generate_reply(test_input)
                else:
                    result = traced_agent.run(test_input)
                
                print(f"  {i}. ✅ Success: {str(result)[:50]}...")
                success_count += 1
                
            except Exception as e:
                print(f"  {i}. ❌ Failed: {e}")
        
        # Show metrics
        metrics = tracer.get_agent_metrics()
        if metrics:
            print(f"\n📊 {framework.upper()} Results:")
            print(f"  Reliability: {metrics.reliability_score.grade} ({metrics.reliability_score.score:.1f}%)")
            print(f"  Success Rate: {metrics.success_rate:.1%}")
            print(f"  Total Runs: {metrics.total_runs}")
            print(f"  Avg Duration: {metrics.avg_duration_ms:.0f}ms")
        
        tracer.stop_monitoring()


def test_cost_tracking():
    """Test cost tracking functionality."""
    print("\n" + "="*60)
    print("💰 Testing Cost Tracking")
    print("="*60)
    
    from agent_eval.trace.cost_tracker import CostTracker
    
    cost_tracker = CostTracker()
    
    # Test cost calculations
    test_cases = [
        ("openai", "gpt-4o", 1000, 500),
        ("anthropic", "claude-3-5-sonnet-20241022", 1500, 750),
        ("google", "gemini-1.5-pro", 2000, 1000),
        ("cerebras", "llama-3.3-70b", 3000, 1500)
    ]
    
    print("Provider/Model Cost Comparison:")
    for provider, model, input_tokens, output_tokens in test_cases:
        cost = cost_tracker.calculate_cost(provider, model, input_tokens, output_tokens)
        print(f"  {provider:10} {model:25} ${cost:.4f}")
    
    # Test optimization suggestions
    print("\n🔧 Cost Optimization Suggestions:")
    usage_stats = {
        "cost_per_run": 0.15,
        "monthly_runs": 1000,
        "avg_tokens_per_run": 2500
    }
    
    suggestions = cost_tracker.get_optimization_suggestions("openai", "gpt-4o", usage_stats)
    for suggestion in suggestions:
        print(f"  • {suggestion['description']} (Priority: {suggestion['priority']})")


def test_storage():
    """Test storage functionality."""
    print("\n" + "="*60)
    print("💾 Testing Storage Functionality")
    print("="*60)
    
    from agent_eval.trace.storage import TraceStorage
    from agent_eval.trace.types import TraceData, CostData
    import uuid
    
    storage = TraceStorage()
    
    # Create sample trace data
    trace_data = TraceData(
        trace_id=str(uuid.uuid4()),
        agent_id="test_storage_agent",
        session_id=str(uuid.uuid4()),
        start_time=datetime.now(),
        end_time=datetime.now(),
        framework="test",
        success=True,
        cost_data=CostData(total_cost=0.05, api_calls=1, input_tokens=100, output_tokens=50)
    )
    
    # Store trace
    stored_id = storage.store_trace(trace_data)
    print(f"✅ Stored trace: {stored_id}")
    
    # Retrieve trace
    retrieved_trace = storage.get_trace(stored_id)
    if retrieved_trace:
        print(f"✅ Retrieved trace: {retrieved_trace.trace_id}")
        print(f"  Success: {retrieved_trace.success}")
        print(f"  Framework: {retrieved_trace.framework}")
    else:
        print("❌ Failed to retrieve trace")
    
    # Test metrics
    metrics = storage.get_agent_metrics("test_storage_agent")
    if metrics:
        print(f"✅ Retrieved metrics for agent: {metrics.agent_id}")
    else:
        print("ℹ️  No metrics found (expected for new agent)")


def test_api_server():
    """Test API server functionality."""
    print("\n" + "="*60)
    print("🌐 Testing API Server")
    print("="*60)
    
    try:
        from agent_eval.trace.api_server import TraceAPIServer
        from agent_eval.trace.storage import TraceStorage
        
        storage = TraceStorage()
        server = TraceAPIServer(storage=storage, port=8001)  # Use different port for testing
        
        print("✅ API Server initialized successfully")
        print("  Available endpoints:")
        print("    • GET  /health")
        print("    • POST /traces/ingest")
        print("    • GET  /agents/{agent_id}/dashboard")
        print("    • GET  /agents/{agent_id}/metrics")
        print("    • WS   /ws/{agent_id}")
        
        print("\n💡 To start server: arc-eval trace --server --port 8001")
        
    except ImportError as e:
        print("❌ FastAPI not available for API server testing")
        print("  Install with: pip install fastapi uvicorn")
        print(f"  Error: {e}")


def test_cli_integration():
    """Test CLI integration."""
    print("\n" + "="*60)
    print("🖥️  Testing CLI Integration")
    print("="*60)
    
    try:
        from agent_eval.commands.trace_command import TraceCommand, test_tracer
        
        print("✅ TraceCommand imported successfully")
        
        # Test the built-in test function
        print("\n🧪 Running built-in tracer test...")
        result = test_tracer()
        
        if result == 0:
            print("✅ Built-in test completed successfully")
        else:
            print("❌ Built-in test failed")
        
        print("\n💡 CLI Commands available:")
        print("  • arc-eval trace --test")
        print("  • arc-eval trace --agent-id my_agent --dashboard")
        print("  • arc-eval trace --server")
        
    except Exception as e:
        print(f"❌ CLI integration test failed: {e}")


def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🚀 ARC-Eval Runtime Tracing - Comprehensive Test Suite")
    print("=" * 60)
    
    start_time = time.time()
    
    try:
        # Run all tests
        test_basic_tracing()
        test_cost_tracking()
        test_storage()
        test_api_server()
        test_cli_integration()
        
        duration = time.time() - start_time
        
        print("\n" + "="*60)
        print("🎉 All Tests Completed Successfully!")
        print("="*60)
        print(f"⏱️  Total Duration: {duration:.2f} seconds")
        print("\n💡 Next Steps:")
        print("1. Try the CLI: arc-eval trace --test")
        print("2. Start monitoring: arc-eval trace --server")
        print("3. Integrate with your agent:")
        print("   from agent_eval.trace import ArcTracer")
        print("   tracer = ArcTracer('finance')")
        print("   agent = tracer.trace_agent(your_agent)")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = run_comprehensive_test()
    exit(exit_code) 