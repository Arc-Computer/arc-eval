#!/usr/bin/env python3
"""
Main entry point for arc-eval when run as a module.
This prevents the reimport warning.
"""

if __name__ == "__main__":
    from agent_eval.cli import main
    main()