"""
Dual-Track Agent Evaluation System

Implements two evaluation modes:
1. Fast Track: Individual API calls with real-time progress (≤50 scenarios)
2. Batch Track: True Anthropic Message Batches API (100+ scenarios, 50% cost savings)

Authors: ARC-Eval Team
Date: January 2025
"""

import asyncio
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator, Generator, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class EvaluationMode(Enum):
    """Evaluation mode selection."""
    FAST_TRACK = "fast_track"
    BATCH_TRACK = "batch_track"
    AUTO = "auto"


@dataclass
class ProgressUpdate:
    """Progress update for evaluation tracking."""
    current: int
    total: int
    mode: EvaluationMode
    status: str
    eta_seconds: Optional[float] = None
    batch_id: Optional[str] = None
    cost_estimate: Optional[float] = None
    
    @property
    def progress_percent(self) -> float:
        return (self.current / self.total) * 100 if self.total > 0 else 0.0


@dataclass
class EvaluationResult:
    """Single evaluation result."""
    scenario_id: str
    response: str
    confidence: float
    model_used: str
    evaluation_time: float
    cost: float
    error: Optional[str] = None


@dataclass
class EvaluationSummary:
    """Complete evaluation summary."""
    total_scenarios: int
    completed: int
    failed: int
    mode_used: EvaluationMode
    total_cost: float
    total_time: float
    average_confidence: float
    results: List[EvaluationResult]


class DualTrackEvaluator:
    """
    Enterprise-grade dual-track evaluation system.
    
    Automatically selects optimal evaluation mode:
    - Fast Track: Real-time streaming for ≤50 scenarios
    - Batch Track: Cost-efficient batching for 100+ scenarios
    """
    
    def __init__(self, api_manager, fast_track_threshold: int = 50, batch_track_threshold: int = 100):
        """Initialize dual-track evaluator.
        
        Args:
            api_manager: API manager instance for making calls
            fast_track_threshold: Max scenarios for fast track (default: 50)
            batch_track_threshold: Min scenarios for batch track (default: 100)
        """
        self.api_manager = api_manager
        self.fast_track_threshold = fast_track_threshold
        self.batch_track_threshold = batch_track_threshold
        
        # Validate Anthropic batch API availability
        self._validate_batch_api_support()
    
    def _validate_batch_api_support(self) -> None:
        """Validate that Anthropic batch API is available."""
        try:
            if self.api_manager.provider == "anthropic":
                client, _ = self.api_manager.get_client()
                # Check if beta.messages.batches is available
                if not hasattr(client, 'beta') or not hasattr(client.beta, 'messages'):
                    logger.warning("Anthropic batch API not available - will use fast track only")
                    self.batch_track_available = False
                else:
                    self.batch_track_available = True
                    logger.info("✅ Anthropic Message Batches API detected and available")
            else:
                logger.info("Non-Anthropic provider - using fast track mode")
                self.batch_track_available = False
        except Exception as e:
            logger.warning(f"Could not validate batch API: {e} - will use fast track only")
            self.batch_track_available = False
    
    def select_evaluation_mode(self, scenario_count: int, user_preference: Optional[EvaluationMode] = None) -> EvaluationMode:
        """Select optimal evaluation mode based on scenario count and preferences.
        
        Args:
            scenario_count: Number of scenarios to evaluate
            user_preference: User's preferred mode (overrides auto-selection)
            
        Returns:
            Selected evaluation mode
        """
        if user_preference and user_preference != EvaluationMode.AUTO:
            logger.info(f"Using user-specified mode: {user_preference.value}")
            return user_preference
        
        # Auto-selection logic
        if scenario_count <= self.fast_track_threshold:
            mode = EvaluationMode.FAST_TRACK
            reason = f"≤{self.fast_track_threshold} scenarios - optimal for real-time progress"
        elif scenario_count >= self.batch_track_threshold and self.batch_track_available:
            mode = EvaluationMode.BATCH_TRACK
            reason = f"≥{self.batch_track_threshold} scenarios - optimal for cost efficiency (50% savings)"
        else:
            mode = EvaluationMode.FAST_TRACK
            reason = "batch API unavailable or intermediate count - using fast track"
        
        logger.info(f"🎯 Auto-selected {mode.value}: {reason}")
        return mode
    
    async def evaluate_scenarios_async(
        self, 
        prompts: List[Dict[str, Any]], 
        mode: Optional[EvaluationMode] = None,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> EvaluationSummary:
        """Asynchronously evaluate scenarios using optimal mode.
        
        Args:
            prompts: List of evaluation prompts with metadata
            mode: Evaluation mode (auto-selected if None)
            progress_callback: Callback for progress updates
            
        Returns:
            Complete evaluation summary
        """
        start_time = time.time()
        selected_mode = self.select_evaluation_mode(len(prompts), mode)
        
        logger.info(f"🚀 Starting {selected_mode.value} evaluation of {len(prompts)} scenarios")
        
        try:
            if selected_mode == EvaluationMode.FAST_TRACK:
                results = await self._fast_track_evaluation(prompts, progress_callback)
            else:
                results = await self._batch_track_evaluation(prompts, progress_callback)
            
            total_time = time.time() - start_time
            
            # Calculate summary statistics
            completed_results = [r for r in results if r.error is None]
            failed_results = [r for r in results if r.error is not None]
            total_cost = sum(r.cost for r in results)
            avg_confidence = sum(r.confidence for r in completed_results) / len(completed_results) if completed_results else 0.0
            
            summary = EvaluationSummary(
                total_scenarios=len(prompts),
                completed=len(completed_results),
                failed=len(failed_results),
                mode_used=selected_mode,
                total_cost=total_cost,
                total_time=total_time,
                average_confidence=avg_confidence,
                results=results
            )
            
            logger.info(f"✅ Evaluation complete: {summary.completed}/{summary.total_scenarios} scenarios, "
                       f"${summary.total_cost:.2f}, {summary.total_time:.1f}s")
            
            return summary
            
        except Exception as e:
            # Fallback logic: if batch fails, try fast track
            if selected_mode == EvaluationMode.BATCH_TRACK:
                logger.warning(f"Batch evaluation failed: {e}. Falling back to fast track...")
                return await self._fast_track_evaluation(prompts, progress_callback)
            else:
                raise
    
    def evaluate_scenarios(
        self, 
        prompts: List[Dict[str, Any]], 
        mode: Optional[EvaluationMode] = None,
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> EvaluationSummary:
        """Synchronous wrapper for async evaluation."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.evaluate_scenarios_async(prompts, mode, progress_callback))
    
    async def _fast_track_evaluation(
        self, 
        prompts: List[Dict[str, Any]], 
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> List[EvaluationResult]:
        """Fast Track: Individual API calls with real-time progress.
        
        Benefits:
        - Real-time progress visibility
        - No memory accumulation
        - Reliable completion
        - Immediate results
        """
        results = []
        start_time = time.time()
        
        logger.info(f"⚡ Fast Track: Processing {len(prompts)} scenarios individually with real-time progress")
        
        for i, prompt_data in enumerate(prompts):
            iteration_start = time.time()
            
            try:
                # Make individual API call
                response_text, _ = self.api_manager.call_with_logprobs(
                    prompt=prompt_data["prompt"],
                    enable_logprobs=False
                )
                
                iteration_time = time.time() - iteration_start
                
                # Calculate cost (this is tracked in api_manager.track_cost)
                input_tokens = self.api_manager._count_tokens(prompt_data["prompt"])
                output_tokens = self.api_manager._count_tokens(response_text)
                cost = self._calculate_iteration_cost(input_tokens, output_tokens)
                
                # Extract confidence
                confidence = self.api_manager._extract_confidence_from_response(response_text)
                
                result = EvaluationResult(
                    scenario_id=prompt_data.get("scenario_id", f"scenario_{i}"),
                    response=response_text,
                    confidence=confidence,
                    model_used=self.api_manager.preferred_model,
                    evaluation_time=iteration_time,
                    cost=cost,
                    error=None
                )
                
                results.append(result)
                
                # Progress callback
                if progress_callback:
                    elapsed_time = time.time() - start_time
                    avg_time_per_scenario = elapsed_time / (i + 1)
                    eta_seconds = avg_time_per_scenario * (len(prompts) - i - 1)
                    
                    progress = ProgressUpdate(
                        current=i + 1,
                        total=len(prompts),
                        mode=EvaluationMode.FAST_TRACK,
                        status=f"Processed scenario {result.scenario_id}",
                        eta_seconds=eta_seconds,
                        cost_estimate=sum(r.cost for r in results)
                    )
                    progress_callback(progress)
                
                logger.debug(f"✅ Scenario {i+1}/{len(prompts)}: {result.scenario_id} "
                           f"(confidence: {confidence:.2f}, {iteration_time:.1f}s)")
                
                # Small delay to prevent overwhelming the API
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"❌ Scenario {i+1} failed: {e}")
                result = EvaluationResult(
                    scenario_id=prompt_data.get("scenario_id", f"scenario_{i}"),
                    response="",
                    confidence=0.0,
                    model_used=self.api_manager.preferred_model,
                    evaluation_time=time.time() - iteration_start,
                    cost=0.0,
                    error=str(e)
                )
                results.append(result)
        
        total_time = time.time() - start_time
        logger.info(f"⚡ Fast Track completed: {len(results)} scenarios in {total_time:.1f}s "
                   f"(avg: {total_time/len(results):.1f}s per scenario)")
        
        return results
    
    async def _batch_track_evaluation(
        self, 
        prompts: List[Dict[str, Any]], 
        progress_callback: Optional[Callable[[ProgressUpdate], None]] = None
    ) -> List[EvaluationResult]:
        """Batch Track: True Anthropic Message Batches API.
        
        Benefits:
        - 50% cost savings
        - Handles up to 10,000 scenarios
        - Enterprise-scale reliability
        - Optimized throughput
        """
        start_time = time.time()
        
        logger.info(f"📦 Batch Track: Processing {len(prompts)} scenarios via Anthropic Message Batches API")
        
        try:
            # Create batch using real Anthropic API
            client, model = self.api_manager.get_client(prefer_primary=True)
            
            # Prepare batch requests
            batch_requests = []
            for i, prompt_data in enumerate(prompts):
                request = {
                    "custom_id": f"eval_{prompt_data.get('scenario_id', f'scenario_{i}')}",
                    "params": {
                        "model": model,
                        "max_tokens": 2000,
                        "temperature": 0.1,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt_data["prompt"]
                            }
                        ]
                    }
                }
                batch_requests.append(request)
            
            # Create batch
            logger.info(f"📦 Creating batch with {len(batch_requests)} requests...")
            
            if progress_callback:
                progress_callback(ProgressUpdate(
                    current=0,
                    total=len(prompts),
                    mode=EvaluationMode.BATCH_TRACK,
                    status="Creating batch...",
                    cost_estimate=0.0
                ))
            
            batch = client.beta.messages.batches.create(
                requests=batch_requests
            )
            
            batch_id = batch.id
            logger.info(f"✅ Batch created: {batch_id}")
            
            # Monitor batch progress
            last_progress_time = time.time()
            poll_interval = 30  # Poll every 30 seconds
            
            while True:
                # Retrieve batch status
                batch_status = client.beta.messages.batches.retrieve(batch_id)
                
                if batch_status.processing_status == "ended":
                    logger.info(f"✅ Batch {batch_id} completed!")
                    break
                elif batch_status.processing_status == "failed":
                    raise RuntimeError(f"Batch {batch_id} failed")
                elif batch_status.processing_status in ["canceling", "canceled"]:
                    raise RuntimeError(f"Batch {batch_id} was canceled")
                
                # Progress callback
                if progress_callback and time.time() - last_progress_time >= poll_interval:
                    elapsed_time = time.time() - start_time
                    # Estimate progress (Anthropic doesn't provide detailed progress)
                    estimated_progress = min(90, (elapsed_time / 3600) * 100)  # Assume 1 hour max
                    
                    progress_callback(ProgressUpdate(
                        current=int(estimated_progress * len(prompts) / 100),
                        total=len(prompts),
                        mode=EvaluationMode.BATCH_TRACK,
                        status=f"Processing batch {batch_id}...",
                        batch_id=batch_id,
                        eta_seconds=max(0, 3600 - elapsed_time) if elapsed_time < 3600 else None
                    ))
                    last_progress_time = time.time()
                
                logger.info(f"📦 Batch {batch_id} status: {batch_status.processing_status}, "
                           f"elapsed: {time.time() - start_time:.1f}s")
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
            
            # Retrieve results
            logger.info(f"📥 Retrieving results for batch {batch_id}...")
            results = []
            
            result_count = 0
            async for result_entry in client.beta.messages.batches.results(batch_id):
                if result_entry.result.type == "succeeded":
                    message = result_entry.result.message
                    response_text = message.content[0].text if message.content else ""
                    
                    # Extract scenario info from custom_id
                    custom_id = result_entry.custom_id
                    scenario_id = custom_id.replace("eval_", "") if custom_id.startswith("eval_") else custom_id
                    
                    # Calculate metrics
                    confidence = self.api_manager._extract_confidence_from_response(response_text)
                    cost = self._calculate_batch_cost(message.usage.input_tokens, message.usage.output_tokens)
                    
                    result = EvaluationResult(
                        scenario_id=scenario_id,
                        response=response_text,
                        confidence=confidence,
                        model_used=model,
                        evaluation_time=0.0,  # Not available for batch
                        cost=cost,
                        error=None
                    )
                    
                elif result_entry.result.type == "errored":
                    error_msg = result_entry.result.error.message if result_entry.result.error else "Unknown error"
                    custom_id = result_entry.custom_id
                    scenario_id = custom_id.replace("eval_", "") if custom_id.startswith("eval_") else custom_id
                    
                    result = EvaluationResult(
                        scenario_id=scenario_id,
                        response="",
                        confidence=0.0,
                        model_used=model,
                        evaluation_time=0.0,
                        cost=0.0,
                        error=error_msg
                    )
                
                results.append(result)
                result_count += 1
                
                # Progress update for result processing
                if progress_callback and result_count % 10 == 0:
                    progress_callback(ProgressUpdate(
                        current=result_count,
                        total=len(prompts),
                        mode=EvaluationMode.BATCH_TRACK,
                        status=f"Processing results... ({result_count}/{len(prompts)})",
                        batch_id=batch_id
                    ))
            
            total_time = time.time() - start_time
            total_cost = sum(r.cost for r in results)
            
            logger.info(f"📦 Batch Track completed: {len(results)} scenarios in {total_time:.1f}s, "
                       f"${total_cost:.2f} (50% batch discount applied)")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch Track failed: {e}")
            raise
    
    def _calculate_iteration_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for individual API call."""
        # This uses the same logic as api_manager.track_cost but returns the value
        if self.api_manager.provider == "anthropic":
            if "sonnet-4" in self.api_manager.preferred_model.lower():
                return (input_tokens * 1.5 + output_tokens * 7.5) / 1_000_000
            elif "sonnet" in self.api_manager.preferred_model.lower():
                return (input_tokens * 1.5 + output_tokens * 7.5) / 1_000_000
            else:  # haiku
                return (input_tokens * 0.4 + output_tokens * 2.0) / 1_000_000
        elif self.api_manager.provider == "openai":
            if "gpt-4.1-2025-04-14" in self.api_manager.preferred_model and "mini" not in self.api_manager.preferred_model:
                return (input_tokens * 2.5 + output_tokens * 10.0) / 1_000_000
            else:  # mini or other
                return (input_tokens * 0.15 + output_tokens * 0.6) / 1_000_000
        return 0.0
    
    def _calculate_batch_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for batch API call (includes 50% discount)."""
        base_cost = self._calculate_iteration_cost(input_tokens, output_tokens)
        return base_cost * 0.5  # 50% batch discount