"""
Serve command implementation for ARC-Eval CLI.

Handles the serve workflow: Start local web dashboard.
Launches FastAPI server and opens browser automatically.
"""

import webbrowser
import socket
from pathlib import Path
from typing import Optional
from rich.console import Console
from agent_eval.commands.base import BaseCommandHandler


class ServeCommand(BaseCommandHandler):
    """Handles serve command execution with local web server."""
    
    def __init__(self) -> None:
        """Initialize serve command with console."""
        self.console = Console()
    
    def execute(
        self,
        port: int = 3000,
        open_browser: bool = True,
        host: str = "localhost",
        dev: bool = False
    ) -> int:
        """
        Execute serve command to start local web dashboard.

        Args:
            port: Port to run the server on (default: 3000)
            open_browser: Whether to auto-open browser (default: True)
            host: Host to bind to (default: localhost)
            dev: Development mode with auto-reload

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        self.console.print("\n[bold blue]🚀 ARC-Eval Workbench[/bold blue]")
        self.console.print("=" * 60)
        
        try:
            # Check if port is available
            if not self._is_port_available(host, port):
                self.console.print(f"[red]❌ Port {port} is already in use[/red]")
                self.console.print(f"\n[yellow]💡 Try a different port:[/yellow]")
                self.console.print(f"  [green]arc-eval serve --port {port + 1}[/green]")
                return 1
            
            # Import FastAPI server here to avoid startup overhead
            from agent_eval.web.app import start_server
            
            url = f"http://{host}:{port}"
            self.console.print(f"[green]🌐 Starting local web server...[/green]")
            self.console.print(f"[green]📍 URL: {url}[/green]")
            
            if dev:
                self.console.print("[yellow]🔧 Development mode: Auto-reload enabled[/yellow]")
            
            # Open browser before starting server
            if open_browser:
                self.console.print("[green]🔗 Opening browser...[/green]")
                webbrowser.open(url)
            else:
                self.console.print(f"[dim]💡 Open browser manually: {url}[/dim]")
            
            self.console.print("\n[bold cyan]✨ Arc Workbench is ready![/bold cyan]")
            self.console.print("[cyan]Drag & drop your agent outputs to get started[/cyan]")
            self.console.print("\n[dim]Press Ctrl+C to stop the server[/dim]")
            
            # Start the server (this will block)
            start_server(host=host, port=port, dev=dev)
            
            return 0
            
        except ImportError as e:
            self.console.print(f"[red]❌ Missing web dependencies:[/red] {e}")
            self.console.print("\n[yellow]💡 Install web dependencies:[/yellow]")
            self.console.print("  [green]pip install fastapi uvicorn websockets[/green]")
            return 1
        except KeyboardInterrupt:
            self.console.print("\n\n[dim]🛑 Server stopped by user[/dim]")
            return 0
        except Exception as e:
            self.console.print(f"[red]❌ Server failed to start:[/red] {e}")
            self.console.print("\n[yellow]💡 Troubleshooting:[/yellow]")
            self.console.print(f"  • Check if port {port} is available")
            self.console.print(f"  • Try different port: [green]arc-eval serve --port {port + 1}[/green]")
            self.console.print("  • Check firewall settings")
            if dev:
                self.console.print_exception()
            return 1
    
    def _is_port_available(self, host: str, port: int) -> bool:
        """Check if port is available for binding."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                return result != 0  # Port is available if connection fails
        except Exception:
            return False