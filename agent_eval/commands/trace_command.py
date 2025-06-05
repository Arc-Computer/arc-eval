"""
Trace command implementation for ARC-Eval CLI.

Handles the trace workflow: "Monitor your agent in real-time"
"""

import time
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich import box

from agent_eval.trace import ArcTracer, TraceAPIServer
from agent_eval.trace.storage import TraceStorage

logger = logging.getLogger(__name__)
console = Console()


class TraceCommand:
    """Handles trace command execution with real-time monitoring."""
    
    def __init__(self):
        """Initialize trace command."""
        self.console = console
        self.storage = TraceStorage()
        self.api_server = None
        
    def execute(
        self,
        agent_id: Optional[str] = None,
        domain: str = "general",
        live: bool = False,
        dashboard: bool = False,
        server: bool = False,
        port: int = 8000,
        export_format: str = "console",
        show_costs: bool = True,
        show_traces: bool = True,
        limit: int = 10
    ) -> int:
        """Execute trace command.
        
        Args:
            agent_id: Agent identifier to monitor
            domain: Domain for specialized monitoring
            live: Enable live monitoring mode
            dashboard: Show interactive dashboard
            server: Start API server
            port: API server port
            export_format: Export format (console, json, csv)
            show_costs: Include cost information
            show_traces: Include trace details
            limit: Limit number of traces to show
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        try:
            if server:
                return self._start_api_server(port)
            elif dashboard and agent_id:
                return self._show_dashboard(agent_id, live)
            elif agent_id:
                return self._show_agent_status(agent_id, export_format, show_costs, show_traces, limit)
            else:
                return self._show_help()
                
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")
            return 0
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            logger.error(f"Trace command failed: {e}")
            return 1
    
    def _start_api_server(self, port: int) -> int:
        """Start the trace API server."""
        self.console.print(f"\n[bold blue]🚀 Starting ARC-Eval Trace API Server[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Check if FastAPI is available
            try:
                from agent_eval.trace.api_server import TraceAPIServer
            except ImportError:
                self.console.print("[red]❌ FastAPI not installed. Install with:[/red]")
                self.console.print("[cyan]pip install fastapi uvicorn[/cyan]")
                return 1
            
            # Initialize and start server
            self.api_server = TraceAPIServer(storage=self.storage, port=port)
            
            self.console.print(f"[green]✅ Server starting on http://localhost:{port}[/green]")
            self.console.print("\n[bold]Available endpoints:[/bold]")
            self.console.print(f"  • Dashboard: http://localhost:{port}/")
            self.console.print(f"  • Health: http://localhost:{port}/health")
            self.console.print(f"  • Docs: http://localhost:{port}/docs")
            self.console.print("\n[yellow]Press Ctrl+C to stop the server[/yellow]")
            
            # Start server (this blocks)
            self.api_server.start_server()
            
            return 0
            
        except Exception as e:
            self.console.print(f"[red]Failed to start server: {e}[/red]")
            return 1
    
    def _show_dashboard(self, agent_id: str, live: bool) -> int:
        """Show interactive dashboard for an agent."""
        self.console.print(f"\n[bold blue]📊 Agent Dashboard: {agent_id}[/bold blue]")
        self.console.print("=" * 60)
        
        if live:
            return self._show_live_dashboard(agent_id)
        else:
            return self._show_static_dashboard(agent_id)
    
    def _show_live_dashboard(self, agent_id: str) -> int:
        """Show live updating dashboard."""
        self.console.print("[yellow]Starting live monitoring... Press Ctrl+C to stop[/yellow]")
        
        def generate_dashboard():
            """Generate dashboard content."""
            metrics = self.storage.get_agent_metrics(agent_id)
            if not metrics:
                return Panel("Agent not found", title="Error", border_style="red")
            
            # Create dashboard layout
            dashboard_table = Table(title=f"Agent: {agent_id}", box=box.ROUNDED)
            dashboard_table.add_column("Metric", style="cyan")
            dashboard_table.add_column("Value", style="white")
            dashboard_table.add_column("Trend", style="green")
            
            dashboard_table.add_row("Reliability", f"{metrics.reliability_score.grade} ({metrics.reliability_score.score:.1f}%)", metrics.reliability_score.trend)
            dashboard_table.add_row("Success Rate", f"{metrics.success_rate:.1%}", "→")
            dashboard_table.add_row("Total Runs", str(metrics.total_runs), "→")
            dashboard_table.add_row("Avg Duration", f"{metrics.avg_duration_ms:.0f}ms", metrics.performance_trend)
            dashboard_table.add_row("Total Cost", f"${metrics.total_cost:.4f}", metrics.cost_trend)
            dashboard_table.add_row("Last Updated", metrics.last_updated.strftime("%H:%M:%S"), "→")
            
            return dashboard_table
        
        # Live updating display
        try:
            with Live(generate_dashboard(), refresh_per_second=1) as live:
                while True:
                    time.sleep(1)
                    live.update(generate_dashboard())
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Live monitoring stopped[/yellow]")
        
        return 0
    
    def _show_static_dashboard(self, agent_id: str) -> int:
        """Show static dashboard snapshot."""
        metrics = self.storage.get_agent_metrics(agent_id)
        if not metrics:
            self.console.print(f"[red]Agent '{agent_id}' not found[/red]")
            return 1
        
        # Reliability summary
        reliability_panel = Panel(
            f"[bold green]{metrics.reliability_score.grade}[/bold green] "
            f"({metrics.reliability_score.score:.1f}%)\n"
            f"Trend: {metrics.reliability_score.trend} "
            f"({metrics.reliability_score.sample_size} runs)",
            title="🎯 Reliability Score",
            border_style="green"
        )
        
        # Performance summary
        performance_panel = Panel(
            f"Success Rate: [bold]{metrics.success_rate:.1%}[/bold]\n"
            f"Avg Duration: [bold]{metrics.avg_duration_ms:.0f}ms[/bold]\n"
            f"Total Runs: [bold]{metrics.total_runs}[/bold]",
            title="⚡ Performance",
            border_style="blue"
        )
        
        # Cost summary
        cost_per_run = metrics.total_cost / max(metrics.total_runs, 1)
        cost_panel = Panel(
            f"Total Cost: [bold]${metrics.total_cost:.4f}[/bold]\n"
            f"Cost per Run: [bold]${cost_per_run:.4f}[/bold]\n"
            f"Trend: {metrics.cost_trend}",
            title="💰 Cost Tracking",
            border_style="yellow"
        )
        
        # Display panels
        self.console.print(reliability_panel)
        self.console.print(performance_panel)
        self.console.print(cost_panel)
        
        # Recent failures
        if metrics.recent_failures:
            self.console.print("\n[bold red]⚠️ Recent Failures:[/bold red]")
            failure_table = Table(box=box.SIMPLE)
            failure_table.add_column("Type", style="red")
            failure_table.add_column("Frequency", style="yellow")
            failure_table.add_column("Last Seen", style="dim")
            failure_table.add_column("Fix Available", style="green")
            
            for failure in metrics.recent_failures[:5]:
                failure_table.add_row(
                    failure.failure_type,
                    str(failure.frequency),
                    failure.last_occurrence.strftime("%Y-%m-%d %H:%M"),
                    "✅" if failure.fix_available else "❌"
                )
            
            self.console.print(failure_table)
        
        # Recent traces
        recent_traces = self.storage.get_recent_traces(agent_id, limit=5)
        if recent_traces:
            self.console.print("\n[bold blue]📋 Recent Traces:[/bold blue]")
            trace_table = Table(box=box.SIMPLE)
            trace_table.add_column("Trace ID", style="cyan")
            trace_table.add_column("Success", style="green")
            trace_table.add_column("Duration", style="yellow")
            trace_table.add_column("Framework", style="blue")
            trace_table.add_column("Timestamp", style="dim")
            
            for trace in recent_traces:
                success_icon = "✅" if trace.success else "❌"
                trace_table.add_row(
                    trace.trace_id[:8] + "...",
                    success_icon,
                    f"{trace.duration_ms:.0f}ms",
                    trace.framework or "unknown",
                    trace.start_time.strftime("%H:%M:%S")
                )
            
            self.console.print(trace_table)
        
        return 0
    
    def _show_agent_status(
        self, 
        agent_id: str, 
        export_format: str, 
        show_costs: bool, 
        show_traces: bool, 
        limit: int
    ) -> int:
        """Show agent status and metrics."""
        metrics = self.storage.get_agent_metrics(agent_id)
        if not metrics:
            self.console.print(f"[red]Agent '{agent_id}' not found[/red]")
            return 1
        
        if export_format == "json":
            return self._export_json(agent_id, metrics, show_costs, show_traces, limit)
        elif export_format == "csv":
            return self._export_csv(agent_id, metrics, show_costs, show_traces, limit)
        else:
            return self._show_console_status(agent_id, metrics, show_costs, show_traces, limit)
    
    def _show_console_status(
        self, 
        agent_id: str, 
        metrics, 
        show_costs: bool, 
        show_traces: bool, 
        limit: int
    ) -> int:
        """Show status in console format."""
        self.console.print(f"\n[bold blue]📊 Agent Status: {agent_id}[/bold blue]")
        self.console.print("=" * 60)
        
        # Basic metrics
        status_table = Table(title="Agent Metrics", box=box.ROUNDED)
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Reliability Score", f"{metrics.reliability_score.grade} ({metrics.reliability_score.score:.1f}%)")
        status_table.add_row("Success Rate", f"{metrics.success_rate:.1%}")
        status_table.add_row("Total Runs", str(metrics.total_runs))
        status_table.add_row("Average Duration", f"{metrics.avg_duration_ms:.0f}ms")
        
        if show_costs:
            cost_per_run = metrics.total_cost / max(metrics.total_runs, 1)
            status_table.add_row("Total Cost", f"${metrics.total_cost:.4f}")
            status_table.add_row("Cost per Run", f"${cost_per_run:.4f}")
        
        status_table.add_row("Last Updated", metrics.last_updated.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.console.print(status_table)
        
        if show_traces:
            recent_traces = self.storage.get_recent_traces(agent_id, limit=limit)
            if recent_traces:
                self.console.print(f"\n[bold blue]Recent Traces (last {len(recent_traces)}):[/bold blue]")
                for i, trace in enumerate(recent_traces, 1):
                    status = "✅" if trace.success else "❌"
                    self.console.print(f"  {i}. {trace.trace_id[:12]}... {status} "
                                     f"{trace.duration_ms:.0f}ms "
                                     f"({trace.start_time.strftime('%H:%M:%S')})")
        
        return 0
    
    def _export_json(self, agent_id: str, metrics, show_costs: bool, show_traces: bool, limit: int) -> int:
        """Export data as JSON."""
        import json
        
        data = {
            "agent_id": agent_id,
            "reliability_score": {
                "score": metrics.reliability_score.score,
                "grade": metrics.reliability_score.grade,
                "trend": metrics.reliability_score.trend
            },
            "performance": {
                "success_rate": metrics.success_rate,
                "total_runs": metrics.total_runs,
                "avg_duration_ms": metrics.avg_duration_ms
            },
            "last_updated": metrics.last_updated.isoformat()
        }
        
        if show_costs:
            data["cost"] = {
                "total_cost": metrics.total_cost,
                "cost_per_run": metrics.total_cost / max(metrics.total_runs, 1)
            }
        
        if show_traces:
            recent_traces = self.storage.get_recent_traces(agent_id, limit=limit)
            data["recent_traces"] = [
                {
                    "trace_id": trace.trace_id,
                    "success": trace.success,
                    "duration_ms": trace.duration_ms,
                    "timestamp": trace.start_time.isoformat()
                }
                for trace in recent_traces
            ]
        
        print(json.dumps(data, indent=2))
        return 0
    
    def _export_csv(self, agent_id: str, metrics, show_costs: bool, show_traces: bool, limit: int) -> int:
        """Export data as CSV."""
        import csv
        import sys
        
        writer = csv.writer(sys.stdout)
        
        # Basic metrics
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Agent ID", agent_id])
        writer.writerow(["Reliability Score", metrics.reliability_score.score])
        writer.writerow(["Reliability Grade", metrics.reliability_score.grade])
        writer.writerow(["Success Rate", metrics.success_rate])
        writer.writerow(["Total Runs", metrics.total_runs])
        writer.writerow(["Average Duration (ms)", metrics.avg_duration_ms])
        
        if show_costs:
            writer.writerow(["Total Cost", metrics.total_cost])
            writer.writerow(["Cost per Run", metrics.total_cost / max(metrics.total_runs, 1)])
        
        # Traces
        if show_traces:
            writer.writerow([])  # Empty row
            writer.writerow(["Trace ID", "Success", "Duration (ms)", "Timestamp"])
            
            recent_traces = self.storage.get_recent_traces(agent_id, limit=limit)
            for trace in recent_traces:
                writer.writerow([
                    trace.trace_id,
                    trace.success,
                    trace.duration_ms,
                    trace.start_time.isoformat()
                ])
        
        return 0
    
    def _show_help(self) -> int:
        """Show help information."""
        self.console.print("\n[bold blue]🔍 ARC-Eval Runtime Tracing[/bold blue]")
        self.console.print("=" * 60)
        
        help_text = """
[bold]One-line agent monitoring and reliability tracking[/bold]

[yellow]Quick Start:[/yellow]
1. Wrap your agent: [cyan]tracer = ArcTracer("finance"); agent = tracer.trace_agent(your_agent)[/cyan]
2. View dashboard: [cyan]arc-eval trace --agent-id your_agent_id --dashboard[/cyan]
3. Start API server: [cyan]arc-eval trace --server[/cyan]

[yellow]Common Commands:[/yellow]
• [cyan]arc-eval trace --agent-id my_agent --dashboard[/cyan]     Show agent dashboard
• [cyan]arc-eval trace --agent-id my_agent --live[/cyan]         Live monitoring
• [cyan]arc-eval trace --server --port 8000[/cyan]              Start API server
• [cyan]arc-eval trace --agent-id my_agent --export json[/cyan]  Export data as JSON

[yellow]Example Integration:[/yellow]
```python
from agent_eval.trace import ArcTracer

# One line to add monitoring
tracer = ArcTracer("finance")
agent = tracer.trace_agent(your_langchain_agent)

# Your agent is now monitored!
response = agent.run("Process this transaction")
```

[yellow]Dashboard URL:[/yellow] http://localhost:8000/agents/your_agent_id/dashboard
"""
        
        self.console.print(help_text)
        return 0


def create_sample_agent():
    """Create a sample agent for testing."""
    class SampleAgent:
        def __init__(self, name="sample_agent"):
            self.name = name
        
        def run(self, input_text):
            """Simulate agent execution."""
            import time
            import random
            
            # Simulate processing time
            time.sleep(random.uniform(0.1, 0.5))
            
            # Simulate occasional failures
            if random.random() < 0.1:  # 10% failure rate
                raise Exception("Sample agent error")
            
            return f"Processed: {input_text}"
        
        def invoke(self, input_text):
            """Alternative method name for compatibility."""
            return self.run(input_text)
    
    return SampleAgent()


# Helper function for testing
def test_tracer():
    """Test the tracer with a sample agent."""
    from agent_eval.trace import ArcTracer
    
    console.print("\n[bold blue]🧪 Testing ARC-Eval Tracer[/bold blue]")
    console.print("=" * 60)
    
    # Create sample agent
    agent = create_sample_agent()
    
    # Initialize tracer
    tracer = ArcTracer(domain="testing", agent_id="test_agent")
    traced_agent = tracer.trace_agent(agent)
    
    console.print("[green]✅ Agent wrapped with tracer[/green]")
    
    # Run some tests
    test_inputs = [
        "Hello world",
        "Process this data",
        "Generate a report",
        "Analyze the results",
        "Complete the task"
    ]
    
    console.print(f"[yellow]Running {len(test_inputs)} test executions...[/yellow]")
    
    for i, test_input in enumerate(test_inputs, 1):
        try:
            result = traced_agent.run(test_input)
            console.print(f"  {i}. ✅ {test_input[:20]}... → {result[:30]}...")
        except Exception as e:
            console.print(f"  {i}. ❌ {test_input[:20]}... → Error: {e}")
    
    # Show results
    metrics = tracer.get_agent_metrics()
    if metrics:
        console.print(f"\n[bold green]Test Results:[/bold green]")
        console.print(f"  Reliability: {metrics.reliability_score.grade} ({metrics.reliability_score.score:.1f}%)")
        console.print(f"  Success Rate: {metrics.success_rate:.1%}")
        console.print(f"  Total Runs: {metrics.total_runs}")
        console.print(f"  Avg Duration: {metrics.avg_duration_ms:.0f}ms")
    
    console.print(f"\n[cyan]View dashboard with:[/cyan] arc-eval trace --agent-id test_agent --dashboard")
    
    return 0 