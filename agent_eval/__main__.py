"""
ARC-Eval package entry point for module execution.

Allows running the package with: python -m agent_eval
"""

from agent_eval.cli import cli

if __name__ == "__main__":
    cli()