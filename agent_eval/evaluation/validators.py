"""
Input validation and error handling for AgentEval CLI.

Provides comprehensive validation with helpful error messages and format guidance.
"""

import json
import yaml
from typing import Any, Dict, List, Union, Optional, Tuple
from pathlib import Path


class ValidationError(Exception):
    """Custom exception for validation errors with helpful context."""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        self.message = message
        self.suggestions = suggestions or []
        super().__init__(message)


class InputValidator:
    """Comprehensive input validation with helpful error messages."""
    
    @staticmethod
    def validate_json_input(data: str, source: str = "input") -> Tuple[Any, List[str]]:
        """
        Validate and parse JSON input with detailed error reporting.
        
        Args:
            data: Raw JSON string
            source: Source description (for error messages)
            
        Returns:
            (parsed_data, warnings)
            
        Raises:
            ValidationError: If validation fails
        """
        warnings = []
        
        # Parse JSON
        try:
            parsed_data = json.loads(data)
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {source}"
            if hasattr(e, 'lineno'):
                error_msg += f" at line {e.lineno}"
            if hasattr(e, 'colno'):
                error_msg += f", column {e.colno}"
            
            suggestions = [
                "Check for missing quotes, commas, or brackets",
                "Validate JSON syntax at https://jsonlint.com",
                "See examples/sample_agent_outputs.json for correct format",
                "Run 'arc-eval --help-input' for format documentation"
            ]
            raise ValidationError(f"{error_msg}: {e.msg}", suggestions)
        
        # Validate structure
        if isinstance(parsed_data, list):
            # Validate each item in list
            for i, item in enumerate(parsed_data):
                item_warnings = InputValidator._validate_single_output(item, f"item {i+1}")
                warnings.extend(item_warnings)
        elif isinstance(parsed_data, dict):
            # Validate single output
            item_warnings = InputValidator._validate_single_output(parsed_data, "input")
            warnings.extend(item_warnings)
        else:
            suggestions = [
                "Input should be a JSON object or array of objects",
                "Example: {\"output\": \"agent response here\"}",
                "Example: [{\"output\": \"response 1\"}, {\"output\": \"response 2\"}]"
            ]
            raise ValidationError("Invalid input format: expected JSON object or array", suggestions)
        
        return parsed_data, warnings
    
    @staticmethod
    def _validate_single_output(data: Dict[str, Any], context: str) -> List[str]:
        """Validate a single output object and return warnings."""
        warnings = []
        
        if not isinstance(data, dict):
            raise ValidationError(
                f"Invalid {context}: expected JSON object, got {type(data).__name__}",
                ["Each item should be a JSON object with an 'output' field"]
            )
        
        # Check for required fields (flexible approach)
        has_output_field = any(key in data for key in [
            "output", "response", "content", "text", "llm_output", "workflow_output"
        ])
        
        # Check for framework-specific output patterns
        framework_patterns = [
            # AutoGen: messages with author/content
            ("messages" in data and isinstance(data.get("messages"), list) and 
             len(data["messages"]) > 0 and "content" in data["messages"][-1]),
            # Google ADK: content with parts
            ("content" in data and isinstance(data.get("content"), dict) and 
             "parts" in data["content"]),
            # OpenAI: choices with message
            ("choices" in data and isinstance(data.get("choices"), list)),
            # LangGraph: messages with type
            ("messages" in data and "graph_state" in data),
            # NVIDIA AIQ: workflow_output or agent_state
            ("workflow_output" in data or "agent_state" in data),
        ]
        
        has_framework_pattern = any(framework_patterns)
        
        if not has_output_field and not has_framework_pattern:
            available_fields = list(data.keys()) if data.keys() else ["none"]
            suggestions = [
                "Add an 'output' field with the agent's response",
                "Supported fields: 'output', 'response', 'content', 'text'",
                "Example: {\"output\": \"Transaction approved\"}",
                "Or use a supported framework format (run 'arc-eval --help-input')",
                f"Current fields in {context}: {', '.join(available_fields)}",
                "💡 Tip: Use examples/complete-datasets/ for format references"
            ]
            raise ValidationError(f"Missing valid output field in {context}", suggestions)
        
        # Warn about empty outputs
        output_fields = ["output", "response", "content", "text", "llm_output", "workflow_output"]
        for field in output_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str) and not value.strip():
                    warnings.append(f"Empty {field} field in {context}")
                elif value is None:
                    warnings.append(f"Null {field} field in {context}")
                break
        
        # Warn about unexpected structure for known frameworks
        if "choices" in data and not isinstance(data.get("choices"), list):
            warnings.append(f"OpenAI format detected but 'choices' is not a list in {context}")
        
        if "messages" in data and not isinstance(data.get("messages"), list):
            warnings.append(f"Multi-agent format detected but 'messages' is not a list in {context}")
        
        return warnings
    
    @staticmethod
    def suggest_format_help() -> str:
        """Generate helpful format suggestions."""
        return """
Supported input formats:

Basic format:
  {"output": "Agent response here"}

OpenAI format:
  {"choices": [{"message": {"content": "Response"}}]}

Anthropic format:
  {"content": [{"type": "text", "text": "Response"}]}

AutoGen format:
  {"messages": [{"author": "agent", "content": "Response"}]}

Google ADK format:
  {"content": {"parts": [{"text": "Response"}]}}

NVIDIA AIQ format:
  {"workflow_output": "Response"}

For multiple outputs, use an array:
  [{"output": "Response 1"}, {"output": "Response 2"}]

See examples/ directory for complete examples.
"""


class CLIValidator:
    """Validation for CLI arguments and usage patterns."""
    
    @staticmethod
    def validate_domain(domain: str) -> None:
        """Validate domain selection."""
        valid_domains = ["finance", "security", "ml"]
        if domain not in valid_domains:
            raise ValidationError(
                f"Invalid domain: {domain}",
                [f"Valid domains: {', '.join(valid_domains)}"]
            )
    
    @staticmethod
    def validate_export_format(export_format: str) -> None:
        """Validate export format."""
        valid_formats = ["pdf", "csv", "json"]
        if export_format not in valid_formats:
            raise ValidationError(
                f"Invalid export format: {export_format}",
                [f"Valid formats: {', '.join(valid_formats)}"]
            )
    
    @staticmethod
    def validate_file_path(file_path: Path) -> None:
        """Validate file path exists and is readable."""
        if not file_path.exists():
            suggestions = [
                f"Check that the file path is correct: {file_path}",
                "Use absolute or relative path from current directory",
                "Ensure the file exists and is readable"
            ]
            raise ValidationError(f"File not found: {file_path}", suggestions)
        
        if not file_path.is_file():
            raise ValidationError(
                f"Path is not a file: {file_path}",
                ["Ensure the path points to a file, not a directory"]
            )
    
    @staticmethod
    def validate_output_format(output_format: str) -> None:
        """Validate CLI output format."""
        valid_formats = ["table", "json", "csv"]
        if output_format not in valid_formats:
            raise ValidationError(
                f"Invalid output format: {output_format}",
                [f"Valid formats: {', '.join(valid_formats)}"]
            )


class DomainValidator:
    """Domain pack validation utilities."""
    
    @staticmethod
    def validate_domain_pack(file_path: Path) -> None:
        """
        Validate domain pack YAML structure and required fields.
        
        Args:
            file_path: Path to the domain pack YAML file
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValidationError(
                f"Invalid YAML syntax in {file_path.name}: {e}",
                [
                    "Check YAML syntax with an online validator",
                    "Ensure proper indentation (use spaces, not tabs)",
                    "Verify all quotes and brackets are properly closed"
                ]
            )
        except FileNotFoundError:
            raise ValidationError(
                f"Domain pack file not found: {file_path}",
                [
                    "Check if the file exists in the correct location",
                    "Verify the domain name is correct (finance, security, ml)"
                ]
            )
        
        # Validate top-level structure
        if not isinstance(data, dict):
            raise ValidationError(
                f"Domain pack must be a YAML object in {file_path.name}",
                ["Ensure the file starts with valid YAML object structure"]
            )
        
        # Validate eval_pack section
        if 'eval_pack' not in data:
            raise ValidationError(
                f"Missing 'eval_pack' section in {file_path.name}",
                [
                    "Add 'eval_pack:' section with name, version, description",
                    "See examples/domain-specific/ for reference format"
                ]
            )
        
        eval_pack = data['eval_pack']
        required_fields = ['name', 'version', 'description', 'compliance_frameworks']
        
        for field in required_fields:
            if field not in eval_pack:
                raise ValidationError(
                    f"Missing required field '{field}' in eval_pack section of {file_path.name}",
                    [f"Add '{field}:' under the eval_pack section"]
                )
        
        # Validate scenarios section
        if 'scenarios' not in data:
            raise ValidationError(
                f"Missing 'scenarios' section in {file_path.name}",
                [
                    "Add 'scenarios:' section with evaluation scenarios",
                    "Each scenario should have id, name, severity, test_type, etc."
                ]
            )
        
        scenarios = data['scenarios']
        if not isinstance(scenarios, list) or len(scenarios) == 0:
            raise ValidationError(
                f"'scenarios' must be a non-empty list in {file_path.name}",
                ["Add at least one scenario to the scenarios list"]
            )
        
        # Validate each scenario
        required_scenario_fields = ['id', 'name', 'severity', 'test_type', 'description']
        
        for i, scenario in enumerate(scenarios):
            if not isinstance(scenario, dict):
                raise ValidationError(
                    f"Scenario {i+1} must be an object in {file_path.name}",
                    ["Each scenario should be a YAML object with required fields"]
                )
            
            for field in required_scenario_fields:
                if field not in scenario:
                    raise ValidationError(
                        f"Scenario {i+1} missing required field '{field}' in {file_path.name}",
                        [f"Add '{field}:' to scenario {i+1}"]
                    )
            
            # Validate severity values
            valid_severities = ['critical', 'high', 'medium', 'low']
            if scenario.get('severity') not in valid_severities:
                raise ValidationError(
                    f"Invalid severity '{scenario.get('severity')}' in scenario {i+1} of {file_path.name}",
                    [f"Use one of: {', '.join(valid_severities)}"]
                )
            
            # Validate test_type values
            valid_test_types = ['negative', 'positive', 'boundary']
            if scenario.get('test_type') not in valid_test_types:
                raise ValidationError(
                    f"Invalid test_type '{scenario.get('test_type')}' in scenario {i+1} of {file_path.name}",
                    [f"Use one of: {', '.join(valid_test_types)}"]
                )


def format_validation_error(error: ValidationError) -> str:
    """Format validation error with suggestions for CLI display."""
    message = f"[red]Error:[/red] {error.message}"
    
    if error.suggestions:
        message += "\n\n[yellow]Suggestions:[/yellow]"
        for suggestion in error.suggestions:
            message += f"\n  • {suggestion}"
    
    return message