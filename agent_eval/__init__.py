"""
ARC-Eval: Agentic Workflow Reliability Platform.

Three simple workflows for the complete agent improvement lifecycle:
- debug: Why is my agent failing?
- compliance: Does it meet requirements?
- improve: How do I make it better?

A CLI-first platform that lets teams prove whether their agents are safe, 
reliable, and compliant with one command, then get actionable recommendations 
and shareable audit reports.
"""

__version__ = "0.2.7"
__author__ = "ARC-Eval Team"

# Export main CLI entry point
from agent_eval.cli import main as cli_main