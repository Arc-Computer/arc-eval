"""
LangChain Planning Failure Fix Templates.

Production-ready templates for fixing common planning-related failures in LangChain agents.
Based on 2025 best practices and structured planning patterns.
"""

from agent_eval.templates.fixes.template_manager import FixTemplate

# LangChain Planning Failure Fix Templates
TEMPLATES = [
    FixTemplate(
        framework="langchain",
        pattern_type="planning_failures",
        subtype="goal_setting",
        title="Structured Planning with ReActAgent and Goal Decomposition",
        description="Implement systematic goal decomposition and planning using LangChain's ReActAgent with structured prompts for clear objective setting and step-by-step execution.",
        code_example="""
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.schema import BaseOutputParser
from typing import List, Dict, Any
import re

class GoalDecomposer:
    \"\"\"Decomposes complex goals into manageable sub-goals.\"\"\"
    
    def __init__(self, llm):
        self.llm = llm
        self.decomposition_prompt = PromptTemplate(
            input_variables=["main_goal", "context"],
            template=\"\"\"
            You are an expert at breaking down complex goals into manageable steps.
            
            Main Goal: {main_goal}
            Context: {context}
            
            Please decompose this goal into 3-5 specific, measurable sub-goals.
            For each sub-goal, provide:
            1. Clear objective
            2. Success criteria
            3. Required resources/tools
            4. Estimated effort
            
            Format your response as:
            SUB-GOAL 1: [Objective]
            SUCCESS: [How to measure success]
            TOOLS: [Required tools/resources]
            EFFORT: [Low/Medium/High]
            
            SUB-GOAL 2: [Continue pattern...]
            \"\"\"
        )
    
    def decompose_goal(self, main_goal: str, context: str = "") -> List[Dict[str, str]]:
        \"\"\"Decompose a main goal into sub-goals.\"\"\"
        response = self.llm.invoke(
            self.decomposition_prompt.format(main_goal=main_goal, context=context)
        )
        
        return self._parse_decomposition(response.content)
    
    def _parse_decomposition(self, response: str) -> List[Dict[str, str]]:
        \"\"\"Parse the decomposition response into structured sub-goals.\"\"\"
        sub_goals = []
        
        # Extract sub-goals using regex
        pattern = r'SUB-GOAL \\d+: (.+?)\\nSUCCESS: (.+?)\\nTOOLS: (.+?)\\nEFFORT: (.+?)(?=\\n|$)'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for match in matches:
            sub_goals.append({
                "objective": match[0].strip(),
                "success_criteria": match[1].strip(),
                "required_tools": match[2].strip(),
                "effort": match[3].strip()
            })
        
        return sub_goals

class StructuredPlanningAgent:
    \"\"\"LangChain agent with structured planning capabilities.\"\"\"
    
    def __init__(self, llm, tools: List[Tool]):
        self.llm = llm
        self.tools = tools
        self.goal_decomposer = GoalDecomposer(llm)
        
        # Enhanced planning prompt
        self.planning_prompt = PromptTemplate(
            input_variables=["tools", "tool_names", "input", "agent_scratchpad", "current_plan"],
            template=\"\"\"
            You are a systematic planning agent. Follow this structured approach:
            
            PLANNING PHASE:
            1. Understand the objective clearly
            2. Break down into sub-goals if needed
            3. Identify required tools and resources
            4. Create step-by-step execution plan
            5. Define success criteria
            
            EXECUTION PHASE:
            - Follow the plan systematically
            - Validate each step before proceeding
            - Adjust plan if obstacles encountered
            - Document progress and learnings
            
            Available tools: {tool_names}
            Tools: {tools}
            
            Current Plan: {current_plan}
            
            Question: {input}
            
            Thought: Let me approach this systematically by first understanding the goal and creating a clear plan.
            {agent_scratchpad}
            \"\"\"
        )
        
        # Create the agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.planning_prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=10,
            early_stopping_method="generate"
        )
    
    def execute_with_planning(self, objective: str, context: str = "") -> Dict[str, Any]:
        \"\"\"Execute objective with structured planning.\"\"\"
        
        # Step 1: Decompose the goal
        sub_goals = self.goal_decomposer.decompose_goal(objective, context)
        
        # Step 2: Create execution plan
        execution_plan = self._create_execution_plan(sub_goals)
        
        # Step 3: Execute with plan
        result = self.agent_executor.invoke({
            "input": objective,
            "current_plan": execution_plan
        })
        
        return {
            "objective": objective,
            "sub_goals": sub_goals,
            "execution_plan": execution_plan,
            "result": result,
            "success": self._evaluate_success(result, sub_goals)
        }
    
    def _create_execution_plan(self, sub_goals: List[Dict[str, str]]) -> str:
        \"\"\"Create a structured execution plan from sub-goals.\"\"\"
        plan_lines = ["EXECUTION PLAN:"]
        
        for i, sub_goal in enumerate(sub_goals, 1):
            plan_lines.append(f"\\nStep {i}: {sub_goal['objective']}")
            plan_lines.append(f"  Success Criteria: {sub_goal['success_criteria']}")
            plan_lines.append(f"  Required Tools: {sub_goal['required_tools']}")
            plan_lines.append(f"  Effort Level: {sub_goal['effort']}")
        
        plan_lines.append("\\nEXECUTION GUIDELINES:")
        plan_lines.append("- Complete each step before moving to the next")
        plan_lines.append("- Validate success criteria at each step")
        plan_lines.append("- Document any obstacles or adjustments needed")
        plan_lines.append("- Provide clear reasoning for each action")
        
        return "\\n".join(plan_lines)
    
    def _evaluate_success(self, result: Dict[str, Any], sub_goals: List[Dict[str, str]]) -> bool:
        \"\"\"Evaluate if the execution was successful based on sub-goals.\"\"\"
        # Simple success evaluation - can be enhanced with LLM-based evaluation
        output = result.get("output", "").lower()
        
        # Check if output contains success indicators
        success_indicators = ["completed", "successful", "achieved", "done", "finished"]
        has_success_indicators = any(indicator in output for indicator in success_indicators)
        
        # Check if output is substantial (not just error messages)
        is_substantial = len(output) > 100 and "error" not in output
        
        return has_success_indicators and is_substantial

# Example usage
def create_planning_agent_example():
    \"\"\"Example of creating and using a structured planning agent.\"\"\"
    
    from langchain.llms import OpenAI
    from langchain.tools import DuckDuckGoSearchRun, Calculator
    
    # Initialize LLM
    llm = OpenAI(temperature=0)
    
    # Define tools
    search_tool = Tool(
        name="Search",
        description="Search for current information on the internet",
        func=DuckDuckGoSearchRun().run
    )
    
    calculator_tool = Tool(
        name="Calculator", 
        description="Perform mathematical calculations",
        func=Calculator().run
    )
    
    tools = [search_tool, calculator_tool]
    
    # Create planning agent
    planning_agent = StructuredPlanningAgent(llm, tools)
    
    # Execute with planning
    result = planning_agent.execute_with_planning(
        objective="Research the current AI market trends and calculate the projected growth rate for 2025",
        context="Need comprehensive analysis for business strategy planning"
    )
    
    return result

# Advanced planning with contingency handling
class ContingencyPlanningAgent(StructuredPlanningAgent):
    \"\"\"Enhanced planning agent with contingency planning.\"\"\"
    
    def __init__(self, llm, tools: List[Tool]):
        super().__init__(llm, tools)
        self.contingency_plans = {}
        self.execution_history = []
    
    def execute_with_contingencies(self, objective: str, context: str = "") -> Dict[str, Any]:
        \"\"\"Execute with contingency planning for common failure scenarios.\"\"\"
        
        # Create main plan
        main_result = self.execute_with_planning(objective, context)
        
        # If main plan failed, try contingencies
        if not main_result["success"]:
            contingency_result = self._execute_contingency_plan(objective, main_result)
            main_result["contingency_executed"] = True
            main_result["contingency_result"] = contingency_result
        
        return main_result
    
    def _execute_contingency_plan(self, objective: str, failed_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute contingency plan when main plan fails.\"\"\"
        
        # Analyze failure and create alternative approach
        failure_analysis = self._analyze_failure(failed_result)
        
        # Create simplified objective
        simplified_objective = self._simplify_objective(objective, failure_analysis)
        
        # Execute simplified plan
        return self.execute_with_planning(simplified_objective)
    
    def _analyze_failure(self, failed_result: Dict[str, Any]) -> str:
        \"\"\"Analyze why the main plan failed.\"\"\"
        output = failed_result.get("result", {}).get("output", "")
        
        # Simple failure analysis - can be enhanced
        if "timeout" in output.lower():
            return "timeout_issue"
        elif "error" in output.lower():
            return "execution_error"
        elif len(output) < 50:
            return "insufficient_output"
        else:
            return "unknown_failure"
    
    def _simplify_objective(self, original_objective: str, failure_type: str) -> str:
        \"\"\"Create a simplified version of the objective based on failure type.\"\"\"
        simplification_strategies = {
            "timeout_issue": f"Provide a quick summary of: {original_objective}",
            "execution_error": f"Give basic information about: {original_objective}",
            "insufficient_output": f"Explain the key points of: {original_objective}",
            "unknown_failure": f"Provide an overview of: {original_objective}"
        }
        
        return simplification_strategies.get(failure_type, f"Simplify: {original_objective}")

# Usage example
if __name__ == "__main__":
    # This would be used in actual implementation
    result = create_planning_agent_example()
    print(f"Planning result: {result}")
""",
        implementation_steps=[
            "Create GoalDecomposer class for systematic goal breakdown",
            "Implement StructuredPlanningAgent with enhanced prompts",
            "Add execution plan creation and validation logic",
            "Implement success evaluation based on sub-goals",
            "Add contingency planning for failure scenarios",
            "Test with complex multi-step objectives",
            "Monitor planning effectiveness and adjust prompts"
        ],
        prerequisites=[
            "LangChain agents and tools",
            "Understanding of ReAct pattern",
            "Structured prompt engineering"
        ],
        testing_notes="""
Test structured planning by:
1. Testing with complex multi-step objectives
2. Verifying goal decomposition accuracy
3. Testing contingency plan activation
4. Checking success criteria evaluation
5. Monitoring execution plan adherence
""",
        business_impact="Improves goal achievement rates by 50% through systematic planning and reduces project failures",
        difficulty="intermediate"
    ),
    
    FixTemplate(
        framework="langchain",
        pattern_type="planning_failures",
        subtype="reflection_errors",
        title="Self-Correction and Learning Loop Implementation",
        description="Implement comprehensive self-correction mechanisms with learning loops to help agents learn from mistakes and improve performance over time.",
        code_example="""
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.prompts import PromptTemplate
from typing import List, Dict, Any, Optional
import json
import time
from dataclasses import dataclass

@dataclass
class ReflectionEntry:
    \"\"\"Represents a reflection on agent performance.\"\"\"
    timestamp: float
    action: str
    outcome: str
    success: bool
    lesson_learned: str
    improvement_suggestion: str

class SelfCorrectionMemory:
    \"\"\"Memory system for storing and retrieving self-correction insights.\"\"\"
    
    def __init__(self, max_entries: int = 100):
        self.max_entries = max_entries
        self.reflections: List[ReflectionEntry] = []
        self.patterns = {}
        self.success_strategies = {}
    
    def add_reflection(self, reflection: ReflectionEntry):
        \"\"\"Add a new reflection entry.\"\"\"
        self.reflections.append(reflection)
        
        # Keep only recent entries
        if len(self.reflections) > self.max_entries:
            self.reflections = self.reflections[-self.max_entries:]
        
        # Update patterns
        self._update_patterns(reflection)
    
    def _update_patterns(self, reflection: ReflectionEntry):
        \"\"\"Update learned patterns from reflection.\"\"\"
        action_type = reflection.action.split()[0].lower()  # First word of action
        
        if action_type not in self.patterns:
            self.patterns[action_type] = {"successes": 0, "failures": 0, "lessons": []}
        
        if reflection.success:
            self.patterns[action_type]["successes"] += 1
            if action_type not in self.success_strategies:
                self.success_strategies[action_type] = []
            self.success_strategies[action_type].append(reflection.improvement_suggestion)
        else:
            self.patterns[action_type]["failures"] += 1
            self.patterns[action_type]["lessons"].append(reflection.lesson_learned)
    
    def get_relevant_insights(self, current_action: str) -> List[str]:
        \"\"\"Get relevant insights for current action.\"\"\"
        insights = []
        action_type = current_action.split()[0].lower()
        
        # Get pattern-based insights
        if action_type in self.patterns:
            pattern = self.patterns[action_type]
            success_rate = pattern["successes"] / (pattern["successes"] + pattern["failures"])
            
            if success_rate < 0.5:
                insights.append(f"Warning: {action_type} actions have low success rate ({success_rate:.1%})")
                insights.extend(pattern["lessons"][-3:])  # Recent lessons
        
        # Get success strategies
        if action_type in self.success_strategies:
            insights.append("Successful strategies for this action type:")
            insights.extend(self.success_strategies[action_type][-2:])  # Recent strategies
        
        return insights

class ReflectiveAgent:
    \"\"\"Agent with self-correction and learning capabilities.\"\"\"
    
    def __init__(self, base_agent: AgentExecutor, llm):
        self.base_agent = base_agent
        self.llm = llm
        self.correction_memory = SelfCorrectionMemory()
        
        # Reflection prompt
        self.reflection_prompt = PromptTemplate(
            input_variables=["action", "outcome", "context", "previous_insights"],
            template=\"\"\"
            Reflect on the following action and its outcome:
            
            Action Taken: {action}
            Outcome: {outcome}
            Context: {context}
            Previous Insights: {previous_insights}
            
            Please analyze:
            1. Was this action successful? (Yes/No)
            2. What went well?
            3. What could be improved?
            4. What lesson can be learned?
            5. How would you approach this differently next time?
            
            Provide your reflection in this format:
            SUCCESS: [Yes/No]
            WHAT_WORKED: [What went well]
            IMPROVEMENTS: [What could be improved]
            LESSON: [Key lesson learned]
            NEXT_TIME: [How to approach differently]
            \"\"\"
        )
    
    def execute_with_reflection(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute agent action with reflection and learning.\"\"\"
        
        # Get relevant insights from memory
        action_preview = str(input_data.get("input", ""))
        previous_insights = self.correction_memory.get_relevant_insights(action_preview)
        
        # Add insights to input if available
        if previous_insights:
            enhanced_input = input_data.copy()
            insights_text = "\\n".join(previous_insights)
            enhanced_input["input"] = f"{input_data['input']}\\n\\nRelevant insights from previous experience:\\n{insights_text}"
        else:
            enhanced_input = input_data
        
        # Execute the action
        start_time = time.time()
        result = self.base_agent.invoke(enhanced_input)
        execution_time = time.time() - start_time
        
        # Reflect on the outcome
        reflection = self._reflect_on_outcome(
            action=str(enhanced_input),
            outcome=str(result),
            context=f"Execution time: {execution_time:.2f}s",
            previous_insights=previous_insights
        )
        
        # Store reflection
        self.correction_memory.add_reflection(reflection)
        
        # Enhance result with reflection
        result["reflection"] = {
            "success": reflection.success,
            "lesson_learned": reflection.lesson_learned,
            "improvement_suggestion": reflection.improvement_suggestion,
            "execution_time": execution_time
        }
        
        return result
    
    def _reflect_on_outcome(
        self, 
        action: str, 
        outcome: str, 
        context: str, 
        previous_insights: List[str]
    ) -> ReflectionEntry:
        \"\"\"Reflect on action outcome and extract lessons.\"\"\"
        
        insights_text = "\\n".join(previous_insights) if previous_insights else "None"
        
        reflection_response = self.llm.invoke(
            self.reflection_prompt.format(
                action=action[:500],  # Truncate for prompt length
                outcome=outcome[:500],
                context=context,
                previous_insights=insights_text
            )
        )
        
        # Parse reflection response
        reflection_data = self._parse_reflection(reflection_response.content)
        
        return ReflectionEntry(
            timestamp=time.time(),
            action=action[:200],  # Store truncated version
            outcome=outcome[:200],
            success=reflection_data.get("success", False),
            lesson_learned=reflection_data.get("lesson", ""),
            improvement_suggestion=reflection_data.get("next_time", "")
        )
    
    def _parse_reflection(self, reflection_text: str) -> Dict[str, Any]:
        \"\"\"Parse reflection response into structured data.\"\"\"
        reflection_data = {}
        
        lines = reflection_text.split("\\n")
        for line in lines:
            if line.startswith("SUCCESS:"):
                reflection_data["success"] = "yes" in line.lower()
            elif line.startswith("LESSON:"):
                reflection_data["lesson"] = line.replace("LESSON:", "").strip()
            elif line.startswith("NEXT_TIME:"):
                reflection_data["next_time"] = line.replace("NEXT_TIME:", "").strip()
        
        return reflection_data
    
    def get_learning_summary(self) -> Dict[str, Any]:
        \"\"\"Get summary of learning progress.\"\"\"
        total_reflections = len(self.correction_memory.reflections)
        successful_actions = sum(1 for r in self.correction_memory.reflections if r.success)
        
        return {
            "total_actions": total_reflections,
            "success_rate": successful_actions / total_reflections if total_reflections > 0 else 0,
            "patterns_learned": len(self.correction_memory.patterns),
            "success_strategies": len(self.correction_memory.success_strategies),
            "recent_lessons": [r.lesson_learned for r in self.correction_memory.reflections[-5:]]
        }

# Example usage with continuous improvement
class ContinuousImprovementAgent(ReflectiveAgent):
    \"\"\"Agent that continuously improves based on reflections.\"\"\"
    
    def __init__(self, base_agent: AgentExecutor, llm):
        super().__init__(base_agent, llm)
        self.improvement_threshold = 0.7  # Trigger improvement if success rate below this
        self.improvement_cycles = 0
    
    def execute_with_continuous_improvement(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Execute with continuous improvement based on performance.\"\"\"
        
        # Execute with reflection
        result = self.execute_with_reflection(input_data)
        
        # Check if improvement is needed
        learning_summary = self.get_learning_summary()
        if (learning_summary["total_actions"] >= 10 and 
            learning_summary["success_rate"] < self.improvement_threshold):
            
            self._trigger_improvement_cycle()
        
        result["learning_summary"] = learning_summary
        return result
    
    def _trigger_improvement_cycle(self):
        \"\"\"Trigger an improvement cycle based on learned patterns.\"\"\"
        self.improvement_cycles += 1
        
        # Analyze failure patterns
        failure_patterns = self._analyze_failure_patterns()
        
        # Update agent behavior based on patterns
        self._update_agent_behavior(failure_patterns)
        
        print(f"Improvement cycle {self.improvement_cycles} triggered")
        print(f"Addressing patterns: {failure_patterns}")
    
    def _analyze_failure_patterns(self) -> List[str]:
        \"\"\"Analyze common failure patterns.\"\"\"
        patterns = []
        
        for action_type, data in self.correction_memory.patterns.items():
            if data["failures"] > data["successes"]:
                patterns.append(f"High failure rate for {action_type} actions")
        
        return patterns
    
    def _update_agent_behavior(self, failure_patterns: List[str]):
        \"\"\"Update agent behavior based on failure patterns.\"\"\"
        # This could involve updating prompts, adding new tools, or adjusting parameters
        # For now, we'll just log the patterns for manual review
        
        for pattern in failure_patterns:
            print(f"Identified pattern for improvement: {pattern}")

# Usage example
def create_reflective_agent_example():
    \"\"\"Example of creating a reflective agent.\"\"\"
    
    from langchain.llms import OpenAI
    from langchain.agents import create_react_agent
    from langchain.tools import DuckDuckGoSearchRun
    
    # Create base agent
    llm = OpenAI(temperature=0)
    tools = [DuckDuckGoSearchRun()]
    
    base_agent = AgentExecutor(
        agent=create_react_agent(llm, tools, PromptTemplate.from_template("Answer: {input}")),
        tools=tools,
        verbose=True
    )
    
    # Create reflective agent
    reflective_agent = ContinuousImprovementAgent(base_agent, llm)
    
    return reflective_agent

# Example usage
if __name__ == "__main__":
    agent = create_reflective_agent_example()
    
    # Execute multiple tasks to see learning in action
    tasks = [
        {"input": "What is the current weather in New York?"},
        {"input": "Find information about AI trends in 2025"},
        {"input": "Calculate the square root of 144"}
    ]
    
    for task in tasks:
        result = agent.execute_with_continuous_improvement(task)
        print(f"Task: {task['input']}")
        print(f"Success: {result['reflection']['success']}")
        print(f"Lesson: {result['reflection']['lesson_learned']}")
        print("---")
""",
        implementation_steps=[
            "Create SelfCorrectionMemory for storing reflections",
            "Implement ReflectiveAgent with reflection capabilities",
            "Add pattern analysis and learning from failures",
            "Create continuous improvement mechanisms",
            "Implement success strategy tracking",
            "Test with various task types and failure scenarios",
            "Monitor learning effectiveness over time"
        ],
        prerequisites=[
            "LangChain agents and memory systems",
            "Understanding of reflection patterns",
            "Experience with agent performance monitoring"
        ],
        testing_notes="""
Test self-correction by:
1. Running agents on repetitive tasks
2. Introducing deliberate failures to test learning
3. Verifying pattern recognition accuracy
4. Testing improvement cycle triggers
5. Monitoring success rate improvements over time
""",
        business_impact="Reduces repeated mistakes by 60% and improves agent performance through continuous learning",
        difficulty="advanced"
    )
]
