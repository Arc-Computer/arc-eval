"""
Serve command implementation for Arc Workbench.
"""

import webbrowser
import uvicorn
from rich.console import Console

from agent_eval.commands.base import BaseCommandHandler
# We'll need to import the app from agent_eval.web.app,
# but it's not created yet. We'll add a placeholder import for now.
# from agent_eval.web.app import app # Placeholder for FastAPI app

console = Console()

class ServeCommand(BaseCommandHandler):
    """Handles the `serve` command execution."""

    def execute(self, port: int = 3000, open_browser: bool = True, host: str = "127.0.0.1") -> int:
        """
        Start the FastAPI local web server for Arc Workbench.

        Args:
            port: Port to run the server on.
            open_browser: Whether to open the browser automatically.
            host: Host to bind the server to.

        Returns:
            Exit code (0 for success, 1 for failure).
        """
        console.print(f"🚀 Starting Arc Workbench at http://{host}:{port}")

        if open_browser:
            try:
                webbrowser.open(f"http://{host}:{port}")
                console.print(f"Opened browser to http://{host}:{port}")
            except Exception as e:
                console.print(f"[yellow]⚠️ Could not open browser automatically: {e}[/yellow]")
                console.print(f"Please navigate to http://{host}:{port} manually.")

        try:
            # Note: "agent_eval.web.app:app" assumes 'app' is the FastAPI instance
            # in agent_eval/web/app.py. This string format is standard for Uvicorn.
            # The actual FastAPI app object isn't directly passed to uvicorn.run here usually.
            # We will define the FastAPI 'app' instance in agent_eval/web/app.py later.
            uvicorn.run(
                "agent_eval.web.app:app",
                host=host,
                port=port,
                reload=True, # Reload for development convenience, can be configurable
                log_level="info"
            )
            return 0
        except ImportError:
            console.print("[red]❌ Error: Could not import the FastAPI application from agent_eval.web.app.[/red]")
            console.print("Please ensure 'agent_eval/web/app.py' exists and defines a FastAPI instance named 'app'.")
            return 1
        except Exception as e:
            console.print(f"[red]❌ Failed to start server: {e}[/red]")
            self.logger.exception("Server startup failed") # Log full traceback
            return 1
