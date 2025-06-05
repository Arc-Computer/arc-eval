"""
Data sanitizer for removing sensitive information from traces.

Detects and redacts PII, credentials, and other sensitive data.
"""

import re
import logging
from typing import Any, Dict, List, Pattern, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RedactionRule:
    """Defines a pattern to detect and redact."""
    name: str
    pattern: Pattern
    replacement: str = "[REDACTED]"
    
    def apply(self, text: str) -> str:
        """Apply redaction rule to text."""
        return self.pattern.sub(self.replacement, text)


class TraceSanitizer:
    """Sanitizes sensitive data from trace information."""
    
    # Common PII patterns
    PII_PATTERNS = {
        "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b'),
        "credit_card": re.compile(r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'),
        "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'),
        "ip_address": re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    }
    
    # Credential patterns
    CREDENTIAL_PATTERNS = {
        "api_key": re.compile(r'(?i)(api[_\-]?key|apikey|api_token)[\s:="\']+([a-zA-Z0-9\-_]{20,})'),
        "bearer_token": re.compile(r'(?i)bearer\s+([a-zA-Z0-9\-_.]+)'),
        "basic_auth": re.compile(r'(?i)basic\s+([a-zA-Z0-9+/=]+)'),
        "password": re.compile(r'(?i)(password|passwd|pwd)[\s:="\']+([^\s"\']+)'),
        "secret": re.compile(r'(?i)(secret|private[_\-]?key)[\s:="\']+([^\s"\']+)'),
        "aws_key": re.compile(r'(?i)(AKIA[0-9A-Z]{16}|aws_secret_access_key[\s:="\']+[a-zA-Z0-9+/]{40})'),
        "openai_key": re.compile(r'sk-[a-zA-Z0-9]{48}'),
        "anthropic_key": re.compile(r'sk-ant-[a-zA-Z0-9\-]{40,}'),
    }
    
    # Domain-specific patterns
    DOMAIN_PATTERNS = {
        "finance": {
            "account_number": re.compile(r'\b\d{8,12}\b'),
            "routing_number": re.compile(r'\b\d{9}\b'),
            "iban": re.compile(r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'),
        },
        "security": {
            "jwt": re.compile(r'eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+'),
            "private_key": re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA )?PRIVATE KEY-----'),
        },
        "ml": {
            "wandb_key": re.compile(r'[a-zA-Z0-9]{40}'),
            "hf_token": re.compile(r'hf_[a-zA-Z0-9]{30,}'),
        }
    }
    
    def __init__(self, domain: str = "general", custom_rules: List[RedactionRule] = None):
        """Initialize sanitizer with domain-specific rules.
        
        Args:
            domain: Domain for specialized sanitization rules
            custom_rules: Additional custom redaction rules
        """
        self.domain = domain
        self.custom_rules = custom_rules or []
        
        # Build rule set
        self.rules = self._build_rules()
        
    def _build_rules(self) -> List[RedactionRule]:
        """Build complete set of redaction rules."""
        rules = []
        
        # Add PII rules
        for name, pattern in self.PII_PATTERNS.items():
            rules.append(RedactionRule(
                name=f"pii_{name}",
                pattern=pattern,
                replacement=f"[REDACTED_{name.upper()}]"
            ))
        
        # Add credential rules
        for name, pattern in self.CREDENTIAL_PATTERNS.items():
            rules.append(RedactionRule(
                name=f"cred_{name}",
                pattern=pattern,
                replacement=f"[REDACTED_{name.upper()}]"
            ))
        
        # Add domain-specific rules
        if self.domain in self.DOMAIN_PATTERNS:
            for name, pattern in self.DOMAIN_PATTERNS[self.domain].items():
                rules.append(RedactionRule(
                    name=f"domain_{name}",
                    pattern=pattern,
                    replacement=f"[REDACTED_{name.upper()}]"
                ))
        
        # Add custom rules
        rules.extend(self.custom_rules)
        
        return rules
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize a string value."""
        if not isinstance(text, str):
            return text
            
        sanitized = text
        for rule in self.rules:
            try:
                sanitized = rule.apply(sanitized)
            except Exception as e:
                logger.warning(f"Failed to apply rule {rule.name}: {e}")
                
        return sanitized
    
    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively sanitize dictionary values."""
        if not isinstance(data, dict):
            return data
            
        sanitized = {}
        for key, value in data.items():
            # Sanitize the key itself
            sanitized_key = self.sanitize_string(str(key))
            
            # Sanitize the value
            if isinstance(value, str):
                sanitized[sanitized_key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[sanitized_key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[sanitized_key] = self.sanitize_list(value)
            else:
                # For other types, convert to string and sanitize
                sanitized[sanitized_key] = self.sanitize_string(str(value))
                
        return sanitized
    
    def sanitize_list(self, data: List[Any]) -> List[Any]:
        """Recursively sanitize list values."""
        if not isinstance(data, list):
            return data
            
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(self.sanitize_string(item))
            elif isinstance(item, dict):
                sanitized.append(self.sanitize_dict(item))
            elif isinstance(item, list):
                sanitized.append(self.sanitize_list(item))
            else:
                # For other types, convert to string and sanitize
                sanitized.append(self.sanitize_string(str(item)))
                
        return sanitized
    
    def sanitize(self, data: Any) -> Any:
        """Sanitize any data type."""
        if isinstance(data, str):
            return self.sanitize_string(data)
        elif isinstance(data, dict):
            return self.sanitize_dict(data)
        elif isinstance(data, list):
            return self.sanitize_list(data)
        else:
            # For other types, convert to string and sanitize
            return self.sanitize_string(str(data))
    
    def sanitize_trace_data(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize complete trace data structure."""
        # Create a copy to avoid modifying original
        import copy
        sanitized_data = copy.deepcopy(trace_data)
        
        # Sanitize specific fields that are likely to contain sensitive data
        sensitive_fields = [
            "input", "output", "args", "kwargs", "result",
            "tool_input", "tool_output", "error", "metadata",
            "execution_timeline", "tool_calls"
        ]
        
        for field in sensitive_fields:
            if field in sanitized_data:
                sanitized_data[field] = self.sanitize(sanitized_data[field])
        
        # Recursively sanitize nested structures
        if "execution_timeline" in sanitized_data:
            for step in sanitized_data["execution_timeline"]:
                if isinstance(step, dict) and "data" in step:
                    step["data"] = self.sanitize(step["data"])
        
        if "tool_calls" in sanitized_data:
            for tool_call in sanitized_data["tool_calls"]:
                if isinstance(tool_call, dict):
                    if "tool_input" in tool_call:
                        tool_call["tool_input"] = self.sanitize(tool_call["tool_input"])
                    if "tool_output" in tool_call:
                        tool_call["tool_output"] = self.sanitize(tool_call["tool_output"])
        
        return sanitized_data


def create_sanitizer(domain: str = "general", enable_sanitization: bool = True, custom_rules: List[RedactionRule] = None) -> TraceSanitizer:
    """Factory function to create appropriate sanitizer.
    
    Args:
        domain: Domain for specialized rules
        enable_sanitization: Whether to enable sanitization (can be disabled for debugging)
        custom_rules: Additional custom redaction rules
    
    Returns:
        TraceSanitizer instance
    """
    if not enable_sanitization:
        # Return a no-op sanitizer
        class NoOpSanitizer(TraceSanitizer):
            def sanitize(self, data: Any) -> Any:
                return data
            def sanitize_trace_data(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
                return trace_data
        
        return NoOpSanitizer(domain)
    
    return TraceSanitizer(domain, custom_rules)