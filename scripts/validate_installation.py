#!/usr/bin/env python3
"""
Simple test script to validate AgentEval CLI functionality.
"""

import subprocess
import json
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path(__file__).parent)
    return result.returncode, result.stdout, result.stderr


def test_basic_functionality():
    """Test basic CLI functionality."""
    print("🧪 Testing AgentEval CLI...")
    
    # Activate venv and test help
    cmd = ["bash", "-c", "source venv/bin/activate && agent-eval --help"]
    exit_code, stdout, stderr = run_command(cmd)
    assert exit_code == 0, f"Help command failed: {stderr}"
    assert "AgentEval: Domain-specific evaluation" in stdout
    print("✅ Help command works")
    
    # Test with sample data
    cmd = ["bash", "-c", "source venv/bin/activate && agent-eval --domain finance --input examples/sample_agent_outputs.json --output json"]
    exit_code, stdout, stderr = run_command(cmd)
    assert exit_code in [0, 1], f"Sample evaluation failed: {stderr}"  # May have failures
    
    # Parse JSON output
    try:
        results = json.loads(stdout)
        assert len(results) == 5, f"Expected 5 results, got {len(results)}"
        assert all("scenario_id" in r for r in results), "Missing scenario_id in results"
        print("✅ JSON output format correct")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON output: {stdout[:200]}")
        return False
    
    # Test with failing data
    cmd = ["bash", "-c", "source venv/bin/activate && agent-eval --domain finance --input examples/failing_agent_outputs.json --output json"]
    exit_code, stdout, stderr = run_command(cmd)
    assert exit_code == 1, f"Expected exit code 1 for failures, got {exit_code}"
    
    # Parse failing results
    try:
        results = json.loads(stdout)
        failed_results = [r for r in results if not r["passed"]]
        assert len(failed_results) > 0, "Expected some failures in failing data"
        print(f"✅ Detected {len(failed_results)} failures correctly")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON output for failing data: {stdout[:200]}")
        return False
    
    # Test PDF export
    cmd = ["bash", "-c", "source venv/bin/activate && agent-eval --domain finance --input examples/failing_agent_outputs.json --export pdf"]
    exit_code, stdout, stderr = run_command(cmd)
    assert exit_code == 1, f"PDF export failed: {stderr}"
    output = stdout + stderr  # Check both stdout and stderr
    assert "📄 Audit Report:" in output, f"PDF export message not found in: {output[-200:]}"
    print("✅ PDF export works")
    
    # Test CSV export
    cmd = ["bash", "-c", "source venv/bin/activate && agent-eval --domain finance --input examples/failing_agent_outputs.json --export csv"]
    exit_code, stdout, stderr = run_command(cmd)
    assert exit_code == 1, f"CSV export failed: {stderr}"
    output = stdout + stderr  # Check both stdout and stderr
    assert "📊 Data Export:" in output, f"CSV export message not found in: {output[-200:]}"
    print("✅ CSV export works")
    
    print("🎉 All tests passed! AgentEval CLI is working correctly.")
    return True


if __name__ == "__main__":
    try:
        success = test_basic_functionality()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        sys.exit(1)