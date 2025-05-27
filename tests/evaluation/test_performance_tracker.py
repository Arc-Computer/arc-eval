"""
Unit tests for PerformanceTracker.

Tests performance monitoring, context management, and metrics collection.
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock
from agent_eval.evaluation.performance_tracker import PerformanceTracker


class TestPerformanceTracker:
    """Test suite for PerformanceTracker class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.tracker = PerformanceTracker()
    
    def test_initialization(self):
        """Test PerformanceTracker initialization."""
        assert self.tracker is not None
        assert self.tracker.start_time is None
        assert self.tracker.end_time is None
        assert self.tracker.total_cost == 0.0
        assert self.tracker.scenario_times == []
        assert self.tracker.agent_total_time == 0.0
        assert self.tracker.judge_total_time == 0.0
        assert self.tracker.memory_samples == []
        assert self.tracker.cpu_samples == []
        assert self.tracker._monitoring is False
        assert self.tracker._monitor_thread is None
        assert self.tracker.scenario_count == 0
    
    def test_context_manager_protocol(self):
        """Test context manager enter and exit."""
        # Test __enter__
        result = self.tracker.__enter__()
        assert result is self.tracker
        assert self.tracker.start_time is not None
        assert self.tracker._monitor_thread is not None
        assert self.tracker._monitoring is True
        
        # Test __exit__
        self.tracker.__exit__(None, None, None)
        assert self.tracker.end_time is not None
        assert self.tracker._monitoring is False
    
    def test_add_cost(self):
        """Test cost tracking."""
        initial_cost = self.tracker.total_cost
        
        self.tracker.add_cost(10.50)
        assert self.tracker.total_cost == initial_cost + 10.50
        
        self.tracker.add_cost(5.25)
        assert self.tracker.total_cost == initial_cost + 15.75
    
    def test_track_scenario_completion(self):
        """Test scenario timing tracking."""
        assert len(self.tracker.scenario_times) == 0
        assert self.tracker.scenario_count == 0
        
        self.tracker.track_scenario_completion(1.5)
        assert len(self.tracker.scenario_times) == 1
        assert self.tracker.scenario_times[0] == 1.5
        assert self.tracker.scenario_count == 1
        
        self.tracker.track_scenario_completion(2.3)
        assert len(self.tracker.scenario_times) == 2
        assert self.tracker.scenario_times[1] == 2.3
        assert self.tracker.scenario_count == 2
    
    def test_track_judge_execution(self):
        """Test judge execution timing with context manager."""
        initial_judge_time = self.tracker.judge_total_time
        
        with self.tracker.track_judge_execution():
            # Simulate judge work
            time.sleep(0.05)  # 50ms
        
        # Should have added time to judge_total_time
        time_added = self.tracker.judge_total_time - initial_judge_time
        assert 0.04 <= time_added <= 0.15  # Allow some tolerance
    
    def test_with_statement(self):
        """Test context manager with 'with' statement."""
        with self.tracker:
            # Check that tracking has started
            assert self.tracker.start_time is not None
            assert self.tracker._monitoring is True
            
            # Simulate some work
            time.sleep(0.05)
            
        # After exiting context
        assert self.tracker.end_time is not None
        assert self.tracker._monitoring is False
        
        # Check that some time was recorded
        runtime = self.tracker.end_time - self.tracker.start_time
        assert runtime > 0.04
        assert runtime < 1.0
    
    def test_get_performance_summary_empty(self):
        """Test performance summary with no data."""
        summary = self.tracker.get_performance_summary()
        
        # Should return some kind of metrics object
        assert summary is not None
        # The exact structure depends on implementation
    
    @patch('psutil.Process')
    def test_get_performance_summary_with_data(self, mock_process):
        """Test performance summary generation with sample data."""
        # Mock psutil Process
        mock_proc = MagicMock()
        mock_process.return_value = mock_proc
        
        # Add some test data
        self.tracker.total_cost = 15.75
        self.tracker.scenario_times = [1.2, 1.8, 2.1, 1.5]
        self.tracker.scenario_count = 4
        self.tracker.agent_total_time = 5.0
        self.tracker.judge_total_time = 3.0
        self.tracker.memory_samples = [100.0, 110.0, 105.0]
        self.tracker.cpu_samples = [25.0, 30.0, 28.0]
        
        with self.tracker:
            time.sleep(0.05)
        
        summary = self.tracker.get_performance_summary()
        
        # Basic validation that summary was generated
        assert summary is not None
    
    def test_concurrent_access_safety(self):
        """Test that multiple threads can safely use the tracker."""
        results = []
        
        def worker():
            try:
                self.tracker.add_cost(1.0)
                self.tracker.track_scenario_completion(0.5)
                results.append("success")
            except Exception as e:
                results.append(f"error: {e}")
        
        # Start multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All threads should complete successfully
        assert len(results) == 3
        assert all(result == "success" for result in results)
        
        # Check that data was recorded from all threads
        assert self.tracker.total_cost == 3.0
        assert len(self.tracker.scenario_times) == 3
        assert self.tracker.scenario_count == 3
    
    def test_exception_handling_in_context_manager(self):
        """Test that exceptions in context manager are handled properly."""
        try:
            with self.tracker:
                self.tracker.add_cost(5.0)
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception
        
        # Tracking should be properly stopped even after exception
        assert self.tracker.end_time is not None
        assert self.tracker._monitoring is False
        assert self.tracker.total_cost == 5.0
    
    @patch('psutil.Process')
    def test_resource_monitoring_error_handling(self, mock_process):
        """Test handling of psutil errors during monitoring."""
        # Mock process to raise exception
        mock_proc = MagicMock()
        mock_proc.memory_info.side_effect = Exception("psutil error")
        mock_proc.cpu_percent.side_effect = Exception("psutil error")
        mock_process.return_value = mock_proc
        
        # Create new tracker with mocked process
        tracker = PerformanceTracker()
        
        # Should not crash even if psutil fails
        with tracker:
            time.sleep(0.05)
        
        # Should complete without errors
        assert tracker.end_time is not None