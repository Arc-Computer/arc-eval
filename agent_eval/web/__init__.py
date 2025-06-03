"""
Web interface module for ARC-Eval.

This module provides the local-first web UI that transforms the CLI
into an interactive debugging companion. Built with FastAPI backend
and React frontend.
"""

from .app import start_server

__all__ = ['start_server']