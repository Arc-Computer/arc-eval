"""
Trace Storage: SQLite-based storage with Postgres-ready design.

Handles persistent storage of trace data, metrics, and analysis results.
"""

import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import contextmanager

from .types import TraceData, AgentMetrics, ReliabilityScore, FailureInfo

logger = logging.getLogger(__name__)


class TraceStorage:
    """SQLite storage for trace data with Postgres-ready design."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize trace storage.
        
        Args:
            db_path: Path to SQLite database file (default: ~/.arc-eval/traces.db)
        """
        if db_path is None:
            # Default to user's home directory
            home_dir = Path.home()
            arc_dir = home_dir / ".arc-eval"
            arc_dir.mkdir(exist_ok=True)
            db_path = str(arc_dir / "traces.db")
        
        self.db_path = db_path
        self._init_database()
        
        logger.info(f"TraceStorage initialized with database: {db_path}")
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            # Create tables
            conn.executescript("""
                -- Agents table
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    domain TEXT,
                    framework TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Traces table
                CREATE TABLE IF NOT EXISTS traces (
                    trace_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    session_id TEXT,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration_ms REAL,
                    framework TEXT,
                    success BOOLEAN,
                    error TEXT,
                    metadata TEXT,  -- JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                );
                
                -- Execution steps table
                CREATE TABLE IF NOT EXISTS execution_steps (
                    step_id TEXT PRIMARY KEY,
                    trace_id TEXT,
                    event_type TEXT,
                    timestamp TIMESTAMP,
                    duration_ms REAL,
                    data TEXT,  -- JSON
                    parent_step_id TEXT,
                    error TEXT,
                    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
                );
                
                -- Tool calls table
                CREATE TABLE IF NOT EXISTS tool_calls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    tool_name TEXT,
                    tool_input TEXT,  -- JSON
                    tool_output TEXT,
                    timestamp TIMESTAMP,
                    duration_ms REAL,
                    success BOOLEAN,
                    error TEXT,
                    cost REAL DEFAULT 0.0,
                    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
                );
                
                -- Cost data table
                CREATE TABLE IF NOT EXISTS cost_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trace_id TEXT,
                    total_cost REAL,
                    api_calls INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    cost_per_run REAL,
                    provider TEXT,
                    model TEXT,
                    FOREIGN KEY (trace_id) REFERENCES traces (trace_id)
                );
                
                -- Agent metrics table
                CREATE TABLE IF NOT EXISTS agent_metrics (
                    agent_id TEXT PRIMARY KEY,
                    total_runs INTEGER,
                    success_rate REAL,
                    avg_duration_ms REAL,
                    total_cost REAL,
                    reliability_score REAL,
                    reliability_grade TEXT,
                    reliability_trend TEXT,
                    cost_trend TEXT,
                    performance_trend TEXT,
                    last_updated TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                );
                
                -- Failure info table
                CREATE TABLE IF NOT EXISTS failure_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    failure_type TEXT,
                    frequency INTEGER,
                    last_occurrence TIMESTAMP,
                    description TEXT,
                    fix_available BOOLEAN,
                    fix_description TEXT,
                    FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
                );
                
                -- Create indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_traces_agent_id ON traces (agent_id);
                CREATE INDEX IF NOT EXISTS idx_traces_start_time ON traces (start_time);
                CREATE INDEX IF NOT EXISTS idx_execution_steps_trace_id ON execution_steps (trace_id);
                CREATE INDEX IF NOT EXISTS idx_tool_calls_trace_id ON tool_calls (trace_id);
                CREATE INDEX IF NOT EXISTS idx_cost_data_trace_id ON cost_data (trace_id);
            """)
            
            conn.commit()
            logger.debug("Database schema initialized")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def store_trace(self, trace_data: TraceData) -> str:
        """Store complete trace data.
        
        Args:
            trace_data: Trace data to store
            
        Returns:
            Trace ID
        """
        with self._get_connection() as conn:
            try:
                # Insert or update agent
                conn.execute("""
                    INSERT OR REPLACE INTO agents (agent_id, domain, framework, last_active)
                    VALUES (?, ?, ?, ?)
                """, (trace_data.agent_id, "general", trace_data.framework, datetime.now()))
                
                # Insert trace
                conn.execute("""
                    INSERT OR REPLACE INTO traces 
                    (trace_id, agent_id, session_id, start_time, end_time, duration_ms, 
                     framework, success, error, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trace_data.trace_id,
                    trace_data.agent_id,
                    trace_data.session_id,
                    trace_data.start_time,
                    trace_data.end_time,
                    trace_data.duration_ms,
                    trace_data.framework,
                    trace_data.success,
                    trace_data.error,
                    json.dumps(trace_data.metadata)
                ))
                
                # Insert execution steps
                for step in trace_data.execution_timeline:
                    conn.execute("""
                        INSERT INTO execution_steps 
                        (step_id, trace_id, event_type, timestamp, duration_ms, data, 
                         parent_step_id, error)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        step.step_id,
                        trace_data.trace_id,
                        step.event_type.value,
                        step.timestamp,
                        step.duration_ms,
                        json.dumps(step.data),
                        step.parent_step_id,
                        step.error
                    ))
                
                # Insert tool calls
                for tool_call in trace_data.tool_calls:
                    conn.execute("""
                        INSERT INTO tool_calls 
                        (trace_id, tool_name, tool_input, tool_output, timestamp, 
                         duration_ms, success, error, cost)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        trace_data.trace_id,
                        tool_call.tool_name,
                        json.dumps(tool_call.tool_input),
                        str(tool_call.tool_output),
                        tool_call.timestamp,
                        tool_call.duration_ms,
                        tool_call.success,
                        tool_call.error,
                        tool_call.cost
                    ))
                
                # Insert cost data
                cost_data = trace_data.cost_data
                conn.execute("""
                    INSERT INTO cost_data 
                    (trace_id, total_cost, api_calls, input_tokens, output_tokens, 
                     cost_per_run, provider, model)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trace_data.trace_id,
                    cost_data.total_cost,
                    cost_data.api_calls,
                    cost_data.input_tokens,
                    cost_data.output_tokens,
                    cost_data.cost_per_run,
                    cost_data.provider,
                    cost_data.model
                ))
                
                conn.commit()
                logger.debug(f"Stored trace: {trace_data.trace_id}")
                
                return trace_data.trace_id
                
            except Exception as e:
                conn.rollback()
                logger.error(f"Failed to store trace: {e}")
                raise
    
    def get_trace(self, trace_id: str) -> Optional[TraceData]:
        """Retrieve trace by ID.
        
        Args:
            trace_id: Trace identifier
            
        Returns:
            TraceData or None if not found
        """
        with self._get_connection() as conn:
            # Get main trace data
            trace_row = conn.execute("""
                SELECT * FROM traces WHERE trace_id = ?
            """, (trace_id,)).fetchone()
            
            if not trace_row:
                return None
            
            # Get execution steps
            step_rows = conn.execute("""
                SELECT * FROM execution_steps WHERE trace_id = ? 
                ORDER BY timestamp
            """, (trace_id,)).fetchall()
            
            # Get tool calls
            tool_rows = conn.execute("""
                SELECT * FROM tool_calls WHERE trace_id = ? 
                ORDER BY timestamp
            """, (trace_id,)).fetchall()
            
            # Get cost data
            cost_row = conn.execute("""
                SELECT * FROM cost_data WHERE trace_id = ?
            """, (trace_id,)).fetchone()
            
            # Reconstruct TraceData
            return self._reconstruct_trace_data(trace_row, step_rows, tool_rows, cost_row)
    
    def get_agent_metrics(self, agent_id: str) -> Optional[AgentMetrics]:
        """Get agent metrics.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            AgentMetrics or None if not found
        """
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT * FROM agent_metrics WHERE agent_id = ?
            """, (agent_id,)).fetchone()
            
            if not row:
                return None
            
            # Get recent failures
            failure_rows = conn.execute("""
                SELECT * FROM failure_info WHERE agent_id = ? 
                ORDER BY last_occurrence DESC LIMIT 5
            """, (agent_id,)).fetchall()
            
            recent_failures = [
                FailureInfo(
                    failure_type=f['failure_type'],
                    frequency=f['frequency'],
                    last_occurrence=datetime.fromisoformat(f['last_occurrence']),
                    description=f['description'],
                    fix_available=bool(f['fix_available']),
                    fix_description=f['fix_description']
                )
                for f in failure_rows
            ]
            
            return AgentMetrics(
                agent_id=row['agent_id'],
                total_runs=row['total_runs'],
                success_rate=row['success_rate'],
                avg_duration_ms=row['avg_duration_ms'],
                total_cost=row['total_cost'],
                reliability_score=ReliabilityScore(
                    score=row['reliability_score'],
                    grade=row['reliability_grade'],
                    trend=row['reliability_trend']
                ),
                recent_failures=recent_failures,
                cost_trend=row['cost_trend'],
                performance_trend=row['performance_trend'],
                last_updated=datetime.fromisoformat(row['last_updated'])
            )
    
    def update_agent_metrics(self, metrics: AgentMetrics) -> None:
        """Update agent metrics.
        
        Args:
            metrics: AgentMetrics to store
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO agent_metrics 
                (agent_id, total_runs, success_rate, avg_duration_ms, total_cost,
                 reliability_score, reliability_grade, reliability_trend,
                 cost_trend, performance_trend, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.agent_id,
                metrics.total_runs,
                metrics.success_rate,
                metrics.avg_duration_ms,
                metrics.total_cost,
                metrics.reliability_score.score,
                metrics.reliability_score.grade,
                metrics.reliability_score.trend,
                metrics.cost_trend,
                metrics.performance_trend,
                metrics.last_updated
            ))
            
            # Update failures
            for failure in metrics.recent_failures:
                conn.execute("""
                    INSERT OR REPLACE INTO failure_info 
                    (agent_id, failure_type, frequency, last_occurrence, 
                     description, fix_available, fix_description)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.agent_id,
                    failure.failure_type,
                    failure.frequency,
                    failure.last_occurrence,
                    failure.description,
                    failure.fix_available,
                    failure.fix_description
                ))
            
            conn.commit()
            logger.debug(f"Updated metrics for agent: {metrics.agent_id}")
    
    def get_recent_traces(self, agent_id: str, limit: int = 10) -> List[TraceData]:
        """Get recent traces for an agent.
        
        Args:
            agent_id: Agent identifier
            limit: Maximum number of traces to return
            
        Returns:
            List of recent TraceData objects
        """
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM traces WHERE agent_id = ? 
                ORDER BY start_time DESC LIMIT ?
            """, (agent_id, limit)).fetchall()
            
            traces = []
            for row in rows:
                trace_data = self._reconstruct_trace_data(row, [], [], None)
                traces.append(trace_data)
            
            return traces
    
    def get_cost_history(self, agent_id: str, days: int = 7) -> List[tuple]:
        """Get cost history for an agent.
        
        Args:
            agent_id: Agent identifier
            days: Number of days to look back
            
        Returns:
            List of (timestamp, cost) tuples
        """
        since_date = datetime.now() - timedelta(days=days)
        
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT t.start_time, c.total_cost 
                FROM traces t
                JOIN cost_data c ON t.trace_id = c.trace_id
                WHERE t.agent_id = ? AND t.start_time >= ?
                ORDER BY t.start_time
            """, (agent_id, since_date)).fetchall()
            
            return [(datetime.fromisoformat(row[0]), row[1]) for row in rows]
    
    def cleanup_old_traces(self, days: int = 30) -> int:
        """Clean up old traces to save space.
        
        Args:
            days: Keep traces newer than this many days
            
        Returns:
            Number of traces deleted
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with self._get_connection() as conn:
            # Get traces to delete
            old_traces = conn.execute("""
                SELECT trace_id FROM traces WHERE start_time < ?
            """, (cutoff_date,)).fetchall()
            
            trace_ids = [row[0] for row in old_traces]
            
            if not trace_ids:
                return 0
            
            # Delete related data
            placeholders = ','.join('?' * len(trace_ids))
            
            conn.execute(f"""
                DELETE FROM execution_steps WHERE trace_id IN ({placeholders})
            """, trace_ids)
            
            conn.execute(f"""
                DELETE FROM tool_calls WHERE trace_id IN ({placeholders})
            """, trace_ids)
            
            conn.execute(f"""
                DELETE FROM cost_data WHERE trace_id IN ({placeholders})
            """, trace_ids)
            
            conn.execute(f"""
                DELETE FROM traces WHERE trace_id IN ({placeholders})
            """, trace_ids)
            
            conn.commit()
            
            logger.info(f"Cleaned up {len(trace_ids)} old traces")
            return len(trace_ids)
    
    def _reconstruct_trace_data(self, trace_row, step_rows, tool_rows, cost_row) -> TraceData:
        """Reconstruct TraceData from database rows."""
        # This is a simplified reconstruction - in production, you'd fully rebuild all objects
        return TraceData(
            trace_id=trace_row['trace_id'],
            agent_id=trace_row['agent_id'],
            session_id=trace_row['session_id'],
            start_time=datetime.fromisoformat(trace_row['start_time']),
            end_time=datetime.fromisoformat(trace_row['end_time']) if trace_row['end_time'] else None,
            framework=trace_row['framework'],
            success=bool(trace_row['success']),
            error=trace_row['error'],
            metadata=json.loads(trace_row['metadata']) if trace_row['metadata'] else {}
        ) 