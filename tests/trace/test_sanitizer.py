"""Tests for trace data sanitizer."""

import pytest
from agent_eval.trace.sanitizer import TraceSanitizer, RedactionRule, create_sanitizer
import re


class TestTraceSanitizer:
    """Test the trace sanitizer functionality."""
    
    def test_sanitize_pii(self):
        """Test PII sanitization."""
        sanitizer = TraceSanitizer()
        
        # Test SSN
        assert sanitizer.sanitize_string("My SSN is 123-45-6789") == "My SSN is [REDACTED_SSN]"
        assert sanitizer.sanitize_string("SSN: 123456789") == "SSN: [REDACTED_SSN]"
        
        # Test credit card
        assert sanitizer.sanitize_string("Card: 1234 5678 9012 3456") == "Card: [REDACTED_CREDIT_CARD]"
        
        # Test email
        assert sanitizer.sanitize_string("Email: test@example.com") == "Email: [REDACTED_EMAIL]"
        
        # Test phone
        assert sanitizer.sanitize_string("Call me at (555) 123-4567") == "Call me at [REDACTED_PHONE]"
        
        # Test IP
        assert sanitizer.sanitize_string("Server IP: 192.168.1.1") == "Server IP: [REDACTED_IP_ADDRESS]"
    
    def test_sanitize_credentials(self):
        """Test credential sanitization."""
        sanitizer = TraceSanitizer()
        
        # Test API key
        assert "[REDACTED_API_KEY]" in sanitizer.sanitize_string("api_key: sk-1234567890abcdefghij")
        assert "[REDACTED_API_KEY]" in sanitizer.sanitize_string('{"api-key": "abcdefghijklmnopqrstuvwxyz123456"}')
        
        # Test bearer token
        assert "[REDACTED_BEARER_TOKEN]" in sanitizer.sanitize_string("Authorization: Bearer abc123xyz")
        
        # Test password
        assert "[REDACTED_PASSWORD]" in sanitizer.sanitize_string("password: mysecret123")
        assert "[REDACTED_PASSWORD]" in sanitizer.sanitize_string('{"passwd": "hidden"}')
        
        # Test OpenAI key
        assert sanitizer.sanitize_string("sk-1234567890123456789012345678901234567890123456789012") == "[REDACTED_OPENAI_KEY]"
        
        # Test Anthropic key
        assert sanitizer.sanitize_string("sk-ant-1234567890abcdefghijklmnopqrstuvwxyz1234") == "[REDACTED_ANTHROPIC_KEY]"
    
    def test_sanitize_dict(self):
        """Test dictionary sanitization."""
        sanitizer = TraceSanitizer()
        
        data = {
            "email": "user@example.com",
            "api_key": "secret123456789012345",
            "safe_data": "This is fine",
            "nested": {
                "password": "hidden",
                "ssn": "123-45-6789"
            }
        }
        
        result = sanitizer.sanitize_dict(data)
        
        assert result["email"] == "[REDACTED_EMAIL]"
        assert "[REDACTED_API_KEY]" in result["api_key"]
        assert result["safe_data"] == "This is fine"
        assert "[REDACTED_PASSWORD]" in result["nested"]["password"]
        assert result["nested"]["ssn"] == "[REDACTED_SSN]"
    
    def test_sanitize_list(self):
        """Test list sanitization."""
        sanitizer = TraceSanitizer()
        
        data = [
            "Safe string",
            "Email: test@example.com",
            {"password": "secret"},
            ["nested", "123-45-6789"]
        ]
        
        result = sanitizer.sanitize_list(data)
        
        assert result[0] == "Safe string"
        assert result[1] == "Email: [REDACTED_EMAIL]"
        assert "[REDACTED_PASSWORD]" in result[2]["password"]
        assert result[3][1] == "[REDACTED_SSN]"
    
    def test_domain_specific_patterns(self):
        """Test domain-specific sanitization."""
        # Finance domain
        finance_sanitizer = TraceSanitizer(domain="finance")
        assert "[REDACTED_ACCOUNT_NUMBER]" in finance_sanitizer.sanitize_string("Account: 12345678")
        assert "[REDACTED_ROUTING_NUMBER]" in finance_sanitizer.sanitize_string("Routing: 123456789")
        
        # Security domain
        security_sanitizer = TraceSanitizer(domain="security")
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        assert "[REDACTED_JWT]" in security_sanitizer.sanitize_string(f"Token: {jwt}")
        
        # ML domain
        ml_sanitizer = TraceSanitizer(domain="ml")
        assert "[REDACTED_HF_TOKEN]" in ml_sanitizer.sanitize_string("hf_abcdefghijklmnopqrstuvwxyz123456")
    
    def test_custom_rules(self):
        """Test custom redaction rules."""
        custom_rules = [
            RedactionRule(
                name="internal_id",
                pattern=re.compile(r'INTERNAL-\d{8}'),
                replacement="[CUSTOM_ID]"
            )
        ]
        
        sanitizer = TraceSanitizer(custom_rules=custom_rules)
        assert sanitizer.sanitize_string("ID: INTERNAL-12345678") == "ID: [CUSTOM_ID]"
    
    def test_no_op_sanitizer(self):
        """Test that sanitization can be disabled."""
        sanitizer = create_sanitizer(enable_sanitization=False)
        
        sensitive_data = "My SSN is 123-45-6789 and my password is secret123"
        assert sanitizer.sanitize(sensitive_data) == sensitive_data
        
        sensitive_dict = {"api_key": "secret", "ssn": "123-45-6789"}
        assert sanitizer.sanitize_dict(sensitive_dict) == sensitive_dict
    
    def test_sanitize_trace_data(self):
        """Test complete trace data sanitization."""
        sanitizer = TraceSanitizer()
        
        trace_data = {
            "trace_id": "abc123",
            "input": {"password": "secret", "data": "process this"},
            "output": "Result with email@example.com",
            "tool_calls": [
                {
                    "tool_input": {"api_key": "sk-123456789012345678901234567890"},
                    "tool_output": "Contains SSN: 123-45-6789"
                }
            ],
            "execution_timeline": [
                {
                    "data": {"args": "password=hidden123"}
                }
            ]
        }
        
        result = sanitizer.sanitize_trace_data(trace_data)
        
        # Check sanitization was applied
        assert "[REDACTED_PASSWORD]" in str(result["input"])
        assert "[REDACTED_EMAIL]" in result["output"]
        assert "[REDACTED_API_KEY]" in str(result["tool_calls"][0]["tool_input"])
        assert "[REDACTED_SSN]" in result["tool_calls"][0]["tool_output"]
        assert "[REDACTED_PASSWORD]" in str(result["execution_timeline"][0]["data"])
        
        # Check structure is preserved
        assert result["trace_id"] == "abc123"
        assert isinstance(result["tool_calls"], list)
        assert isinstance(result["execution_timeline"], list)