#!/usr/bin/env python3
"""
ARC-Eval Flywheel Research Experiment - Entry Point

This script provides a clean entry point for running the research experiment
from the research directory.

Usage:
    python3 run_experiment.py                    # Full research mode
    python3 run_experiment.py --test             # Test mode (5 examples)
    python3 run_experiment.py --small-test       # Small test (20 examples)
"""

import sys
import os
from pathlib import Path

# Add arc-eval root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Change to src directory for proper execution
src_dir = Path(__file__).parent / "src"
os.chdir(src_dir)

# Add src to path for imports
sys.path.insert(0, str(src_dir))

# Import and run the experiment
from flywheel_experiment import main

if __name__ == "__main__":
    sys.exit(main())