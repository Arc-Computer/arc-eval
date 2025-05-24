#!/usr/bin/env python3
"""
Simple test script to validate TUI functionality.
Run this to ensure the TUI components are working correctly.
"""

import asyncio
import json
from pathlib import Path

# Test data creation
def create_test_data():
    """Create sample test data for TUI testing."""
    test_dir = Path("test_data")
    test_dir.mkdir(exist_ok=True)
    
    # Sample OpenAI format
    openai_data = {
        "choices": [
            {
                "message": {
                    "content": "I approve this transaction for $10,000 to John Smith without KYC verification."
                }
            }
        ]
    }
    
    with open(test_dir / "sample_openai.json", "w") as f:
        json.dump(openai_data, f, indent=2)
    
    # Sample simple format
    simple_data = [
        {
            "output": "Processing wire transfer to suspicious offshore account...",
            "scenario": "AML screening"
        },
        {
            "output": "Approved loan without identity verification",
            "scenario": "KYC validation"
        }
    ]
    
    with open(test_dir / "sample_simple.json", "w") as f:
        json.dump(simple_data, f, indent=2)
    
    print(f"✅ Created test data in {test_dir}/")
    return test_dir

def test_imports():
    """Test that all TUI imports work correctly."""
    print("🧪 Testing imports...")
    
    try:
        from agent_eval.tui.app import ARCEvalApp
        print("✅ Main app import successful")
    except ImportError as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    try:
        from agent_eval.tui.screens.main import MainScreen
        print("✅ Main screen import successful")
    except ImportError as e:
        print(f"❌ Main screen import failed: {e}")
        return False
    
    try:
        from agent_eval.tui.widgets.file_selector import FileSelector
        print("✅ File selector import successful")
    except ImportError as e:
        print(f"❌ File selector import failed: {e}")
        return False
    
    try:
        from agent_eval.tui.utils.file_utils import validate_file
        print("✅ File utils import successful")
    except ImportError as e:
        print(f"❌ File utils import failed: {e}")
        return False
    
    return True

def test_file_validation():
    """Test file validation functionality."""
    print("\n🧪 Testing file validation...")
    
    from agent_eval.tui.utils.file_utils import validate_file, get_framework_info
    
    # Create test data
    test_dir = create_test_data()
    
    # Test valid file
    test_file = test_dir / "sample_openai.json"
    is_valid, error = validate_file(test_file)
    
    if is_valid:
        print("✅ File validation passed")
        
        # Test framework detection
        info = get_framework_info(test_file)
        print(f"✅ Framework detected: {info['framework']}")
        print(f"   Size: {info['size']}")
        print(f"   Format: {info['format']}")
    else:
        print(f"❌ File validation failed: {error}")
        return False
    
    return True

def test_cli_integration():
    """Test CLI integration with --help flag."""
    print("\n🧪 Testing CLI integration...")
    
    import subprocess
    import sys
    
    try:
        # Test help output includes new --interactive flag
        result = subprocess.run(
            [sys.executable, "-m", "agent_eval.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        if "--interactive" in result.stdout or "--tui" in result.stdout:
            print("✅ CLI integration successful - interactive flag found")
            return True
        else:
            print("❌ CLI integration failed - interactive flag not found")
            print("Help output:", result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 ARC-Eval TUI Validation Tests")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_file_validation, 
        test_cli_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} failed")
        except Exception as e:
            print(f"❌ {test.__name__} error: {e}")
    
    print("\n" + "=" * 40)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! TUI is ready for use.")
        print("\nTo launch the TUI:")
        print("  arc-eval --interactive")
        print("  arc-eval --tui")
    else:
        print("⚠️  Some tests failed. Check dependencies and installation.")
        print("\nTo install TUI dependencies:")
        print("  pip install textual>=0.80.0 aiofiles>=24.0.0")
    
    return passed == total

if __name__ == "__main__":
    main()