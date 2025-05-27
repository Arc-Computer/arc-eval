"""Performance tracking for agent evaluation runtime, memory, and cost metrics."""

import time
import psutil
import threading
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for agent evaluation."""
    
    # Runtime metrics
    total_execution_time: float  # Total wall clock time in seconds
    agent_execution_time: float  # Time spent on agent operations
    judge_execution_time: float  # Time spent on Agent-as-a-Judge evaluation
    
    # Memory metrics
    peak_memory_mb: float  # Peak memory usage in MB
    avg_memory_mb: float   # Average memory usage in MB
    memory_samples: int    # Number of memory samples taken
    
    # Throughput metrics
    scenarios_per_second: float     # Evaluation throughput
    tokens_per_second: Optional[float]  # Token processing rate
    
    # Cost efficiency metrics
    cost_per_scenario: float        # Cost per evaluation scenario
    cost_efficiency_score: float    # Cost per second of execution
    
    # Resource utilization
    cpu_usage_percent: float        # Average CPU usage during evaluation
    
    # Performance quality indicators
    latency_p50: float             # 50th percentile latency
    latency_p95: float             # 95th percentile latency
    latency_p99: float             # 99th percentile latency


class PerformanceTracker:
    """Context manager for tracking agent evaluation performance metrics."""
    
    def __init__(self, sample_interval: float = 0.1):
        """Initialize performance tracker.
        
        Args:
            sample_interval: How often to sample memory/CPU metrics (seconds)
        """
        self.sample_interval = sample_interval
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.agent_start_time: Optional[float] = None
        self.agent_total_time: float = 0.0
        self.judge_start_time: Optional[float] = None
        self.judge_total_time: float = 0.0
        
        # Memory and CPU tracking
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.scenario_times: List[float] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        
        # Cost tracking
        self.total_cost: float = 0.0
        self.scenario_count: int = 0
        
        # Process reference
        self.process = psutil.Process()
        
    def __enter__(self):
        """Start performance tracking."""
        self.start_time = time.time()
        self._monitoring = True
        
        # Start background monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self._monitor_thread.start()
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop performance tracking."""
        self.end_time = time.time()
        self._monitoring = False
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
    
    @contextmanager
    def track_agent_execution(self):
        """Context manager for tracking agent-specific execution time."""
        agent_start = time.time()
        try:
            yield
        finally:
            agent_end = time.time()
            self.agent_total_time += (agent_end - agent_start)
    
    @contextmanager
    def track_judge_execution(self):
        """Context manager for tracking Agent-as-a-Judge execution time."""
        judge_start = time.time()
        try:
            yield
        finally:
            judge_end = time.time()
            self.judge_total_time += (judge_end - judge_start)
    
    def track_scenario_completion(self, execution_time: float):
        """Track completion of individual scenario."""
        self.scenario_times.append(execution_time)
        self.scenario_count += 1
    
    def add_cost(self, cost: float):
        """Add to total cost tracking."""
        self.total_cost += cost
    
    def _monitor_resources(self):
        """Background thread to monitor memory and CPU usage."""
        while self._monitoring:
            try:
                # Sample memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                self.memory_samples.append(memory_mb)
                
                # Sample CPU usage
                cpu_percent = self.process.cpu_percent()
                self.cpu_samples.append(cpu_percent)
                
                time.sleep(self.sample_interval)
                
            except (psutil.NoSuchProcess, psutil.AccessDenied, Exception) as e:
                logger.warning(f"Resource monitoring error: {e}")
                break
    
    def _calculate_percentiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate percentile statistics from a list of values."""
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        def percentile(p: float) -> float:
            index = int(n * p / 100)
            if index >= n:
                index = n - 1
            return sorted_values[index]
        
        return {
            "p50": percentile(50),
            "p95": percentile(95),
            "p99": percentile(99)
        }
    
    def get_metrics(self) -> PerformanceMetrics:
        """Calculate and return comprehensive performance metrics."""
        if not self.start_time or not self.end_time:
            # Return default metrics when tracking not started/completed
            return PerformanceMetrics(
                total_execution_time=0.0,
                agent_execution_time=0.0,
                judge_execution_time=0.0,
                peak_memory_mb=0.0,
                avg_memory_mb=0.0,
                memory_samples=0,
                scenarios_per_second=0.0,
                tokens_per_second=None,
                cost_per_scenario=0.0,
                cost_efficiency_score=0.0,
                cpu_usage_percent=0.0,
                latency_p50=0.0,
                latency_p95=0.0,
                latency_p99=0.0
            )
        
        total_time = self.end_time - self.start_time
        
        # Memory metrics
        peak_memory = max(self.memory_samples) if self.memory_samples else 0.0
        avg_memory = sum(self.memory_samples) / len(self.memory_samples) if self.memory_samples else 0.0
        
        # CPU metrics
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        
        # Throughput metrics
        scenarios_per_second = self.scenario_count / total_time if total_time > 0 else 0.0
        
        # Cost efficiency
        cost_per_scenario = self.total_cost / self.scenario_count if self.scenario_count > 0 else 0.0
        cost_efficiency = self.total_cost / total_time if total_time > 0 else 0.0
        
        # Latency percentiles
        percentiles = self._calculate_percentiles(self.scenario_times)
        
        # Token processing rate estimation (if available)
        # This is a rough estimation - can be enhanced with actual token counts
        tokens_per_second = None
        if self.scenario_count > 0 and total_time > 0:
            # Rough estimation: ~100 tokens per scenario (can be refined)
            estimated_tokens = self.scenario_count * 100
            tokens_per_second = estimated_tokens / total_time
        
        return PerformanceMetrics(
            total_execution_time=total_time,
            agent_execution_time=self.agent_total_time,
            judge_execution_time=self.judge_total_time,
            peak_memory_mb=peak_memory,
            avg_memory_mb=avg_memory,
            memory_samples=len(self.memory_samples),
            scenarios_per_second=scenarios_per_second,
            tokens_per_second=tokens_per_second,
            cost_per_scenario=cost_per_scenario,
            cost_efficiency_score=cost_efficiency,
            cpu_usage_percent=avg_cpu,
            latency_p50=percentiles["p50"],
            latency_p95=percentiles["p95"],
            latency_p99=percentiles["p99"]
        )
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics as a dictionary for easy serialization."""
        metrics = self.get_metrics()
        
        return {
            "runtime": {
                "total_execution_time": round(metrics.total_execution_time, 2),
                "agent_execution_time": round(metrics.agent_execution_time, 2),
                "judge_execution_time": round(metrics.judge_execution_time, 2),
                "scenarios_per_second": round(metrics.scenarios_per_second, 2)
            },
            "memory": {
                "peak_memory_mb": round(metrics.peak_memory_mb, 1),
                "avg_memory_mb": round(metrics.avg_memory_mb, 1),
                "samples_collected": metrics.memory_samples
            },
            "latency": {
                "p50_seconds": round(metrics.latency_p50, 3),
                "p95_seconds": round(metrics.latency_p95, 3),
                "p99_seconds": round(metrics.latency_p99, 3)
            },
            "cost_efficiency": {
                "cost_per_scenario": round(metrics.cost_per_scenario, 4),
                "cost_per_second": round(metrics.cost_efficiency_score, 4),
                "total_cost": round(self.total_cost, 4)
            },
            "resources": {
                "avg_cpu_percent": round(metrics.cpu_usage_percent, 1),
                "tokens_per_second": round(metrics.tokens_per_second, 1) if metrics.tokens_per_second else None
            }
        }


@contextmanager
def track_performance(sample_interval: float = 0.1):
    """Convenience context manager for performance tracking."""
    tracker = PerformanceTracker(sample_interval)
    with tracker:
        yield tracker