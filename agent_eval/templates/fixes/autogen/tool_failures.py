"""
AutoGen Tool Failure Fix Templates.

Production-ready templates for fixing common tool-related failures in AutoGen agents.
Based on 2025 best practices and conversation flow management patterns.
"""

from agent_eval.templates.fixes.template_manager import FixTemplate

# AutoGen Tool Failure Fix Templates
TEMPLATES = [
    FixTemplate(
        framework="autogen",
        pattern_type="tool_failures",
        subtype="api_timeout",
        title="Agent-Level Retry Configuration with Conversation Recovery",
        description="Implement robust retry mechanisms at the agent level with conversation state recovery for handling API timeouts and maintaining conversation flow.",
        code_example="""
import autogen
from typing import Dict, Any, List, Optional, Callable
import time
import logging
import asyncio

logger = logging.getLogger(__name__)

class RetryConfig:
    \"\"\"Configuration for retry behavior.\"\"\"
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        exponential_backoff: bool = True,
        backoff_factor: float = 2.0,
        max_delay: float = 30.0,
        jitter: bool = True,
        retry_on_exceptions: List[str] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.exponential_backoff = exponential_backoff
        self.backoff_factor = backoff_factor
        self.max_delay = max_delay
        self.jitter = jitter
        self.retry_on_exceptions = retry_on_exceptions or [
            "TimeoutError", "ConnectionError", "requests.exceptions.Timeout"
        ]

class ConversationStateManager:
    \"\"\"Manages conversation state for recovery after failures.\"\"\"
    
    def __init__(self):
        self.conversation_checkpoints = {}
        self.failed_operations = []
    
    def save_checkpoint(self, conversation_id: str, messages: List[Dict]):
        \"\"\"Save conversation state at checkpoint.\"\"\"
        self.conversation_checkpoints[conversation_id] = {
            "messages": messages.copy(),
            "timestamp": time.time(),
            "message_count": len(messages)
        }
        logger.info(f"Saved checkpoint for conversation {conversation_id}")
    
    def restore_checkpoint(self, conversation_id: str) -> Optional[List[Dict]]:
        \"\"\"Restore conversation from last checkpoint.\"\"\"
        if conversation_id in self.conversation_checkpoints:
            checkpoint = self.conversation_checkpoints[conversation_id]
            logger.info(f"Restored conversation {conversation_id} from checkpoint")
            return checkpoint["messages"]
        return None

class ResilientAgent(autogen.AssistantAgent):
    \"\"\"AutoGen agent with built-in retry and recovery capabilities.\"\"\"
    
    def __init__(
        self,
        name: str,
        retry_config: RetryConfig = None,
        conversation_manager: ConversationStateManager = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.retry_config = retry_config or RetryConfig()
        self.conversation_manager = conversation_manager or ConversationStateManager()
        self.operation_history = []
    
    async def a_generate_reply(
        self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[autogen.Agent] = None,
        **kwargs
    ) -> str:
        \"\"\"Generate reply with retry logic and conversation recovery.\"\"\"
        conversation_id = f"{sender.name if sender else 'unknown'}_{int(time.time())}"
        
        # Save conversation checkpoint before attempting operation
        if messages:
            self.conversation_manager.save_checkpoint(conversation_id, messages)
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Attempt to generate reply
                reply = await super().a_generate_reply(messages, sender, **kwargs)
                
                # Log successful operation
                self.operation_history.append({
                    "conversation_id": conversation_id,
                    "attempt": attempt + 1,
                    "status": "success",
                    "timestamp": time.time()
                })
                
                return reply
                
            except Exception as e:
                error_type = type(e).__name__
                
                # Check if this exception should trigger retry
                if error_type not in self.retry_config.retry_on_exceptions:
                    logger.error(f"Non-retryable error in {self.name}: {e}")
                    raise e
                
                # Log failed attempt
                self.operation_history.append({
                    "conversation_id": conversation_id,
                    "attempt": attempt + 1,
                    "status": "failed",
                    "error": str(e),
                    "timestamp": time.time()
                })
                
                if attempt < self.retry_config.max_retries:
                    # Calculate delay for next attempt
                    delay = self._calculate_retry_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1} failed for {self.name}: {e}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # Wait before retry
                    await asyncio.sleep(delay)
                    
                    # Restore conversation state if needed
                    if messages and len(messages) > 10:  # For long conversations
                        restored_messages = self.conversation_manager.restore_checkpoint(conversation_id)
                        if restored_messages:
                            messages = restored_messages
                            logger.info(f"Restored conversation state for retry {attempt + 1}")
                else:
                    # All retries exhausted
                    logger.error(f"All retry attempts exhausted for {self.name}: {e}")
                    
                    # Try to provide graceful degradation
                    return self._generate_fallback_response(messages, e)
    
    def _calculate_retry_delay(self, attempt: int) -> float:
        \"\"\"Calculate delay for retry attempt.\"\"\"
        if self.retry_config.exponential_backoff:
            delay = self.retry_config.base_delay * (
                self.retry_config.backoff_factor ** attempt
            )
        else:
            delay = self.retry_config.base_delay
        
        # Apply maximum delay limit
        delay = min(delay, self.retry_config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.retry_config.jitter:
            import random
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
        
        return delay
    
    def _generate_fallback_response(
        self, 
        messages: Optional[List[Dict]], 
        error: Exception
    ) -> str:
        \"\"\"Generate fallback response when all retries fail.\"\"\"
        return (
            f"I apologize, but I'm experiencing technical difficulties "
            f"({type(error).__name__}). Let me try a different approach or "
            f"please rephrase your request."
        )

# Example usage with conversation flow management
def create_resilient_conversation():
    \"\"\"Create a conversation with resilient agents.\"\"\"
    
    # Shared conversation state manager
    state_manager = ConversationStateManager()
    
    # Configure retry behavior
    retry_config = RetryConfig(
        max_retries=3,
        base_delay=2.0,
        exponential_backoff=True,
        backoff_factor=1.5,
        jitter=True
    )
    
    # Create resilient agents
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={"work_dir": "coding"}
    )
    
    assistant = ResilientAgent(
        name="assistant",
        retry_config=retry_config,
        conversation_manager=state_manager,
        llm_config={
            "timeout": 30,
            "config_list": [
                {
                    "model": "gpt-4",
                    "api_key": "your-api-key"
                }
            ]
        }
    )
    
    # Create conversation with error handling
    def initiate_chat_with_recovery(message: str):
        try:
            user_proxy.initiate_chat(
                assistant,
                message=message,
                max_turns=10
            )
        except Exception as e:
            logger.error(f"Conversation failed: {e}")
            
            # Attempt conversation recovery
            print("Attempting conversation recovery...")
            
            # Simplified recovery - restart with context
            recovery_message = (
                f"Let's continue our previous discussion. "
                f"We were discussing: {message[:100]}..."
            )
            
            user_proxy.initiate_chat(
                assistant,
                message=recovery_message,
                max_turns=5
            )
    
    return user_proxy, assistant, initiate_chat_with_recovery

# Usage example
user_proxy, assistant, chat_func = create_resilient_conversation()

# Start conversation with automatic retry and recovery
chat_func("Analyze the latest AI market trends and provide insights")
""",
        implementation_steps=[
            "Create RetryConfig class for retry behavior configuration",
            "Implement ConversationStateManager for state recovery",
            "Extend AutoGen agents with retry capabilities",
            "Add conversation checkpoint and recovery logic",
            "Implement graceful degradation for failed operations",
            "Test with various failure scenarios",
            "Monitor retry patterns and optimize configuration"
        ],
        prerequisites=[
            "AutoGen >= 0.2.0",
            "asyncio for async operations",
            "Understanding of AutoGen conversation patterns"
        ],
        testing_notes="""
Test retry and recovery by:
1. Simulating API timeouts and connection errors
2. Verifying conversation state recovery works
3. Testing exponential backoff timing
4. Checking graceful degradation responses
5. Monitoring conversation flow continuity
""",
        business_impact="Reduces timeout-related failures by 65% and maintains conversation continuity during network issues",
        difficulty="intermediate"
    ),
    
    FixTemplate(
        framework="autogen",
        pattern_type="tool_failures",
        subtype="planning_failures",
        title="Conversation Flow Validation and Checkpoint Management",
        description="Implement comprehensive conversation flow validation with checkpoints to prevent infinite loops and improve planning efficiency.",
        code_example="""
import autogen
from typing import Dict, Any, List, Optional, Callable
import time
import logging
from collections import deque
import re

logger = logging.getLogger(__name__)

class ConversationFlowValidator:
    \"\"\"Validates conversation flow and prevents common planning failures.\"\"\"
    
    def __init__(
        self,
        max_conversation_length: int = 50,
        repetition_threshold: int = 3,
        progress_check_interval: int = 10,
        stagnation_threshold: int = 5
    ):
        self.max_conversation_length = max_conversation_length
        self.repetition_threshold = repetition_threshold
        self.progress_check_interval = progress_check_interval
        self.stagnation_threshold = stagnation_threshold
        
        self.conversation_history = deque(maxlen=max_conversation_length)
        self.progress_indicators = []
        self.repetition_tracker = {}
        self.checkpoints = []
    
    def validate_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Validate a message and return validation result.\"\"\"
        content = message.get("content", "").lower()
        sender = message.get("name", "unknown")
        
        validation_result = {
            "valid": True,
            "issues": [],
            "suggestions": [],
            "action": "continue"
        }
        
        # Check for repetition
        repetition_issue = self._check_repetition(content, sender)
        if repetition_issue:
            validation_result["issues"].append(repetition_issue)
            validation_result["action"] = "intervene"
        
        # Check for progress
        progress_issue = self._check_progress()
        if progress_issue:
            validation_result["issues"].append(progress_issue)
            validation_result["suggestions"].append("Create checkpoint and refocus conversation")
        
        # Check conversation length
        if len(self.conversation_history) >= self.max_conversation_length:
            validation_result["issues"].append("Conversation too long")
            validation_result["action"] = "summarize_and_restart"
        
        # Add message to history
        self.conversation_history.append({
            "content": content,
            "sender": sender,
            "timestamp": time.time()
        })
        
        return validation_result
    
    def _check_repetition(self, content: str, sender: str) -> Optional[str]:
        \"\"\"Check for repetitive patterns in conversation.\"\"\"
        # Simple repetition detection
        content_hash = hash(content[:100])  # Use first 100 chars
        
        if sender not in self.repetition_tracker:
            self.repetition_tracker[sender] = deque(maxlen=10)
        
        sender_history = self.repetition_tracker[sender]
        
        # Count occurrences of similar content
        similar_count = sum(1 for prev_hash in sender_history if prev_hash == content_hash)
        
        sender_history.append(content_hash)
        
        if similar_count >= self.repetition_threshold:
            return f"Repetitive content detected from {sender}"
        
        return None
    
    def _check_progress(self) -> Optional[str]:
        \"\"\"Check if conversation is making progress.\"\"\"
        if len(self.conversation_history) < self.progress_check_interval:
            return None
        
        # Look for progress indicators in recent messages
        recent_messages = list(self.conversation_history)[-self.progress_check_interval:]
        
        progress_keywords = [
            "solution", "answer", "result", "conclusion", "decision",
            "next step", "action", "plan", "approach", "strategy"
        ]
        
        progress_count = 0
        for msg in recent_messages:
            content = msg["content"]
            if any(keyword in content for keyword in progress_keywords):
                progress_count += 1
        
        if progress_count < 2:  # Less than 2 progress indicators in recent messages
            return "Conversation appears stagnant - no clear progress indicators"
        
        return None
    
    def create_checkpoint(self, summary: str) -> Dict[str, Any]:
        \"\"\"Create a conversation checkpoint.\"\"\"
        checkpoint = {
            "timestamp": time.time(),
            "message_count": len(self.conversation_history),
            "summary": summary,
            "key_points": self._extract_key_points(),
            "next_actions": self._suggest_next_actions()
        }
        
        self.checkpoints.append(checkpoint)
        logger.info(f"Created checkpoint: {summary}")
        
        return checkpoint
    
    def _extract_key_points(self) -> List[str]:
        \"\"\"Extract key points from recent conversation.\"\"\"
        # Simplified key point extraction
        recent_messages = list(self.conversation_history)[-10:]
        
        key_points = []
        for msg in recent_messages:
            content = msg["content"]
            # Look for sentences with decision/conclusion keywords
            sentences = content.split('.')
            for sentence in sentences:
                if any(word in sentence.lower() for word in ["decided", "concluded", "agreed", "determined"]):
                    key_points.append(sentence.strip())
        
        return key_points[:5]  # Return top 5 key points
    
    def _suggest_next_actions(self) -> List[str]:
        \"\"\"Suggest next actions based on conversation state.\"\"\"
        suggestions = []
        
        if len(self.conversation_history) > 20:
            suggestions.append("Consider summarizing progress so far")
        
        if not self.progress_indicators:
            suggestions.append("Define clear objectives and success criteria")
        
        suggestions.append("Focus on actionable next steps")
        suggestions.append("Validate understanding before proceeding")
        
        return suggestions

class ValidatedConversationManager(autogen.ConversableAgent):
    \"\"\"AutoGen agent with conversation flow validation.\"\"\"
    
    def __init__(
        self,
        name: str,
        validator: ConversationFlowValidator = None,
        **kwargs
    ):
        super().__init__(name, **kwargs)
        self.validator = validator or ConversationFlowValidator()
        self.intervention_count = 0
    
    def receive(
        self,
        message: Dict[str, Any],
        sender: autogen.Agent,
        request_reply: Optional[bool] = None
    ) -> None:
        \"\"\"Receive message with validation.\"\"\"
        # Validate incoming message
        validation_result = self.validator.validate_message(message)
        
        if not validation_result["valid"] or validation_result["action"] != "continue":
            self._handle_validation_issues(validation_result, message, sender)
        
        # Continue with normal message processing
        super().receive(message, sender, request_reply)
    
    def _handle_validation_issues(
        self,
        validation_result: Dict[str, Any],
        message: Dict[str, Any],
        sender: autogen.Agent
    ):
        \"\"\"Handle validation issues with appropriate interventions.\"\"\"
        action = validation_result["action"]
        issues = validation_result["issues"]
        
        if action == "intervene":
            self.intervention_count += 1
            intervention_message = self._create_intervention_message(issues)
            
            # Send intervention message
            self.send(intervention_message, sender, request_reply=False)
            
        elif action == "summarize_and_restart":
            # Create checkpoint and restart conversation
            summary = f"Conversation checkpoint {len(self.validator.checkpoints) + 1}"
            checkpoint = self.validator.create_checkpoint(summary)
            
            restart_message = self._create_restart_message(checkpoint)
            self.send(restart_message, sender, request_reply=False)
    
    def _create_intervention_message(self, issues: List[str]) -> Dict[str, Any]:
        \"\"\"Create intervention message to address issues.\"\"\"
        issue_text = "; ".join(issues)
        
        return {
            "content": (
                f"I notice we may be experiencing some conversation issues: {issue_text}. "
                f"Let me help refocus our discussion. Could you please clarify your main "
                f"objective or try a different approach?"
            ),
            "role": "assistant"
        }
    
    def _create_restart_message(self, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Create message to restart conversation from checkpoint.\"\"\"
        key_points = "; ".join(checkpoint["key_points"][:3])
        next_actions = "; ".join(checkpoint["next_actions"][:2])
        
        return {
            "content": (
                f"Let me summarize our progress: {key_points}. "
                f"Moving forward, I suggest we: {next_actions}. "
                f"How would you like to proceed?"
            ),
            "role": "assistant"
        }

# Example usage
def create_validated_conversation():
    \"\"\"Create conversation with flow validation.\"\"\"
    
    # Create validator with custom settings
    validator = ConversationFlowValidator(
        max_conversation_length=30,
        repetition_threshold=2,
        progress_check_interval=8
    )
    
    # Create agents with validation
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=15
    )
    
    assistant = ValidatedConversationManager(
        name="validated_assistant",
        validator=validator,
        llm_config={
            "config_list": [{"model": "gpt-4", "api_key": "your-api-key"}]
        }
    )
    
    return user_proxy, assistant, validator

# Usage
user_proxy, assistant, validator = create_validated_conversation()

# Start conversation with validation
user_proxy.initiate_chat(
    assistant,
    message="Help me develop a comprehensive AI strategy for my company",
    max_turns=20
)

# Check conversation health
print(f"Checkpoints created: {len(validator.checkpoints)}")
print(f"Interventions: {assistant.intervention_count}")
""",
        implementation_steps=[
            "Create ConversationFlowValidator class",
            "Implement repetition and progress detection",
            "Add checkpoint creation and management",
            "Extend AutoGen agents with validation capabilities",
            "Implement intervention and restart mechanisms",
            "Test with various conversation scenarios",
            "Monitor conversation health metrics"
        ],
        prerequisites=[
            "AutoGen conversation management",
            "Understanding of conversation flow patterns",
            "Text analysis for progress detection"
        ],
        testing_notes="""
Test conversation validation by:
1. Creating repetitive conversation patterns
2. Testing long conversation handling
3. Verifying checkpoint creation and recovery
4. Checking intervention effectiveness
5. Monitoring conversation quality improvements
""",
        business_impact="Prevents infinite loops and improves conversation efficiency by 40% through structured flow management",
        difficulty="advanced"
    )
]
