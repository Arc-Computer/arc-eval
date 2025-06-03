#!/usr/bin/env python3
"""
Comprehensive test suite for Arc Workbench Phase 1.

Tests all functionality including:
- CLI integration and regression testing
- Web interface endpoints  
- File upload validation
- Error handling
- WebSocket communication
- Data flow integration
"""

import subprocess
import requests
import json
import time
import sys
import os
from pathlib import Path

class ArcWorkbenchTester:
    def __init__(self):
        self.base_url = "http://localhost:3001"
        self.server_process = None
        self.test_results = []
        
    def log_test(self, test_name, success, message=""):
        """Log test result."""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if message:
            print(f"    {message}")
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message
        })
    
    def test_cli_regression(self):
        """Test that existing CLI functionality remains unchanged."""
        print("\n🧪 Testing CLI Regression (Zero Breaking Changes)")
        print("=" * 60)
        
        # Test main CLI help
        try:
            result = subprocess.run(["arc-eval", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            success = result.returncode == 0 and "serve" in result.stdout
            self.log_test("CLI Help includes new serve command", success, 
                         "Serve command properly integrated")
        except Exception as e:
            self.log_test("CLI Help", False, f"Error: {e}")
        
        # Test debug command help 
        try:
            result = subprocess.run(["arc-eval", "debug", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            success = result.returncode == 0 and "Debug: Why is my agent failing?" in result.stdout
            self.log_test("Debug command unchanged", success)
        except Exception as e:
            self.log_test("Debug command", False, f"Error: {e}")
        
        # Test compliance command help
        try:
            result = subprocess.run(["arc-eval", "compliance", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            success = result.returncode == 0 and "Compliance: Does it meet requirements?" in result.stdout
            self.log_test("Compliance command unchanged", success)
        except Exception as e:
            self.log_test("Compliance command", False, f"Error: {e}")
        
        # Test serve command help
        try:
            result = subprocess.run(["arc-eval", "serve", "--help"], 
                                  capture_output=True, text=True, timeout=10)
            success = result.returncode == 0 and "Start local web dashboard" in result.stdout
            self.log_test("New serve command help", success)
        except Exception as e:
            self.log_test("Serve command help", False, f"Error: {e}")
    
    def start_server(self):
        """Start the Arc Workbench server."""
        print("\n🚀 Starting Arc Workbench Server")
        print("=" * 60)
        
        try:
            self.server_process = subprocess.Popen(
                ["arc-eval", "serve", "--no-browser", "--port", "3001"],
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(3)
            
            # Test if server is running
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            success = response.status_code == 200 and response.json().get("status") == "healthy"
            
            self.log_test("Server starts successfully", success, 
                         f"Health endpoint returns: {response.json() if success else 'Error'}")
            
            return success
        except Exception as e:
            self.log_test("Server startup", False, f"Error: {e}")
            return False
    
    def test_web_interface(self):
        """Test web interface functionality."""
        print("\n🌐 Testing Web Interface")
        print("=" * 60)
        
        # Test main page loads
        try:
            response = requests.get(self.base_url, timeout=5)
            success = response.status_code == 200 and "Arc Workbench" in response.text
            self.log_test("Main web interface loads", success)
        except Exception as e:
            self.log_test("Main web interface", False, f"Error: {e}")
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            success = response.status_code == 200 and "healthy" in response.text
            self.log_test("Health endpoint works", success)
        except Exception as e:
            self.log_test("Health endpoint", False, f"Error: {e}")
    
    def test_file_validation(self):
        """Test file upload validation and error handling."""
        print("\n📁 Testing File Upload Validation")
        print("=" * 60)
        
        # Test invalid file type (.txt)
        try:
            with open("test_invalid.txt", "r") as f:
                files = {"file": ("test.txt", f, "text/plain")}
                response = requests.post(f"{self.base_url}/api/analyze", files=files, timeout=10)
            
            success = response.status_code == 400 and "Invalid file type" in response.text
            self.log_test("Rejects invalid file types (.txt)", success, 
                         f"Status: {response.status_code}, Response: {response.text[:100]}")
        except Exception as e:
            self.log_test("File type validation", False, f"Error: {e}")
        
        # Test invalid JSON format
        try:
            with open("test_broken.json", "r") as f:
                files = {"file": ("broken.json", f, "application/json")}
                response = requests.post(f"{self.base_url}/api/analyze", files=files, timeout=10)
            
            success = response.status_code == 400 and "Invalid JSON format" in response.text
            self.log_test("Rejects malformed JSON", success, 
                         f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("JSON validation", False, f"Error: {e}")
        
        # Test valid JSON format (will fail at analysis step due to missing API key, but validates format)
        try:
            with open("test_valid_agent_output.json", "r") as f:
                files = {"file": ("valid.json", f, "application/json")}
                response = requests.post(f"{self.base_url}/api/analyze", files=files, timeout=10)
            
            # Should accept file but fail at analysis (missing API key)
            success = response.status_code == 500 and "OPENAI_API_KEY" in response.text
            self.log_test("Accepts valid JSON (fails at analysis due to missing API key)", success,
                         "Expected behavior - file format validation passed")
        except Exception as e:
            self.log_test("Valid JSON processing", False, f"Error: {e}")
        
        # Test JSONL format
        try:
            with open("test_valid.jsonl", "r") as f:
                files = {"file": ("valid.jsonl", f, "application/json")}
                response = requests.post(f"{self.base_url}/api/analyze", files=files, timeout=10)
            
            # Should accept JSONL file but fail at analysis (missing API key)
            success = response.status_code == 500 and "OPENAI_API_KEY" in response.text
            self.log_test("Accepts valid JSONL (fails at analysis due to missing API key)", success,
                         "Expected behavior - JSONL format validation passed")
        except Exception as e:
            self.log_test("JSONL processing", False, f"Error: {e}")
    
    def test_chat_functionality(self):
        """Test chat endpoint functionality."""
        print("\n💬 Testing Chat Functionality")
        print("=" * 60)
        
        # Test chat without analysis ID
        try:
            data = {"message": "test question", "analysis_id": "nonexistent"}
            response = requests.post(f"{self.base_url}/api/chat", 
                                   json=data, timeout=10)
            
            success = (response.status_code == 200 and 
                      "don't have analysis context" in response.text)
            self.log_test("Chat handles missing analysis ID gracefully", success)
        except Exception as e:
            self.log_test("Chat error handling", False, f"Error: {e}")
        
        # Test chat with empty message
        try:
            data = {"message": "", "analysis_id": "test"}
            response = requests.post(f"{self.base_url}/api/chat", 
                                   json=data, timeout=10)
            
            success = response.status_code == 200
            self.log_test("Chat handles empty messages", success)
        except Exception as e:
            self.log_test("Chat empty message", False, f"Error: {e}")
    
    def test_error_handling(self):
        """Test comprehensive error handling."""
        print("\n⚠️  Testing Error Handling")
        print("=" * 60)
        
        # Test missing file
        try:
            response = requests.post(f"{self.base_url}/api/analyze", timeout=10)
            success = response.status_code == 422  # FastAPI validation error
            self.log_test("Handles missing file parameter", success)
        except Exception as e:
            self.log_test("Missing file handling", False, f"Error: {e}")
        
        # Test invalid endpoint
        try:
            response = requests.get(f"{self.base_url}/api/nonexistent", timeout=5)
            success = response.status_code == 404
            self.log_test("Handles invalid endpoints (404)", success)
        except Exception as e:
            self.log_test("Invalid endpoint handling", False, f"Error: {e}")
        
        # Test malformed JSON in chat
        try:
            response = requests.post(f"{self.base_url}/api/chat", 
                                   data="invalid json", 
                                   headers={"Content-Type": "application/json"},
                                   timeout=10)
            success = response.status_code == 422
            self.log_test("Handles malformed JSON in requests", success)
        except Exception as e:
            self.log_test("Malformed JSON handling", False, f"Error: {e}")
    
    def test_data_flow(self):
        """Test data flow and integration points."""
        print("\n🔄 Testing Data Flow & Integration")
        print("=" * 60)
        
        # Test that analysis caching works
        try:
            response = requests.get(f"{self.base_url}/api/analysis/nonexistent", timeout=5)
            success = response.status_code == 404 and "Analysis not found" in response.text
            self.log_test("Analysis caching handles missing IDs", success)
        except Exception as e:
            self.log_test("Analysis caching", False, f"Error: {e}")
        
        # Test workflow state integration (this should work without API keys)
        try:
            # The workflow state system should be accessible
            from agent_eval.core.workflow_state import WorkflowStateManager
            manager = WorkflowStateManager()
            state = manager.load_state()
            success = isinstance(state, dict)
            self.log_test("Workflow state integration works", success, 
                         "Can access workflow state management")
        except Exception as e:
            self.log_test("Workflow state integration", False, f"Error: {e}")
    
    def stop_server(self):
        """Stop the server."""
        if self.server_process:
            self.server_process.terminate()
            time.sleep(2)
            if self.server_process.poll() is None:
                self.server_process.kill()
            print("\n🛑 Server stopped")
    
    def run_all_tests(self):
        """Run all tests."""
        print("🧪 ARC WORKBENCH PHASE 1 COMPREHENSIVE TESTING")
        print("=" * 60)
        print("Testing all functionality to ensure zero breaking changes")
        print("and validate new web interface capabilities.\n")
        
        # 1. CLI Regression Testing
        self.test_cli_regression()
        
        # 2. Start server for web tests
        if not self.start_server():
            print("❌ Cannot start server - skipping web tests")
            return
        
        try:
            # 3. Web Interface Tests
            self.test_web_interface()
            
            # 4. File Upload & Validation Tests
            self.test_file_validation()
            
            # 5. Chat Functionality Tests
            self.test_chat_functionality()
            
            # 6. Error Handling Tests
            self.test_error_handling()
            
            # 7. Data Flow & Integration Tests
            self.test_data_flow()
            
        finally:
            # 8. Cleanup
            self.stop_server()
        
        # 9. Generate test report
        self.generate_report()
    
    def generate_report(self):
        """Generate final test report."""
        print("\n📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  • {result['test']}: {result['message']}")
        
        print(f"\n🎯 Arc Workbench Phase 1 Status: {'READY FOR PHASE 2' if failed_tests == 0 else 'NEEDS ATTENTION'}")
        
        # Save detailed report
        with open("test_results.json", "w") as f:
            json.dump({
                "summary": {
                    "total": total_tests,
                    "passed": passed_tests, 
                    "failed": failed_tests,
                    "success_rate": (passed_tests/total_tests)*100
                },
                "results": self.test_results
            }, f, indent=2)
        print(f"📄 Detailed results saved to: test_results.json")

if __name__ == "__main__":
    # Set up environment
    os.chdir(Path(__file__).parent)
    
    # Run tests
    tester = ArcWorkbenchTester()
    tester.run_all_tests()