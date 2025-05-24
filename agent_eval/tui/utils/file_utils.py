"""
File handling utilities for TUI.

Provides file validation, framework detection, and other
file-related utility functions for the TUI interface.
"""

import json
from pathlib import Path
from typing import Dict, Optional, Tuple

from ...core.parser_registry import detect_and_extract


def validate_file(file_path: Path) -> Tuple[bool, Optional[str]]:
    """
    Validate file format and size.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, "File does not exist"
    
    if file_path.suffix not in ['.json', '.csv', '.jsonl']:
        return False, f"Unsupported file format: {file_path.suffix}"
    
    # Check file size (max 100MB)
    file_size = file_path.stat().st_size
    if file_size > 100 * 1024 * 1024:
        return False, f"File too large: {file_size / (1024*1024):.1f}MB (max 100MB)"
    
    # Try to validate JSON content
    if file_path.suffix == '.json':
        try:
            with open(file_path, 'r') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        except Exception as e:
            return False, f"Error reading file: {e}"
    
    return True, None


def get_framework_info(file_path: Path) -> Dict[str, str]:
    """
    Get framework information from a file.
    
    Returns:
        Dict[str, str]: A dictionary containing the following keys:
            - framework: The detected framework name or "Unknown" if not detected.
            - confidence: The confidence level of the framework detection ("High" or "Low").
            - size: The size of the file in a human-readable format (e.g., "1.2 MB").
            - file_format: The file format (e.g., "JSON", "CSV").
            - sample_output: A sample of the normalized output or an error message if applicable.
    """
    try:
        with open(file_path, 'r') as f:
            if file_path.suffix == '.json':
                data = json.load(f)
            else:
                # For CSV/JSONL, just take first line as sample
                first_line = f.readline().strip()
                if file_path.suffix == '.jsonl':
                    data = json.loads(first_line)
                else:
                    data = {"content": first_line}
        
        # Use existing framework detection
        framework, normalized_output = detect_and_extract(data)
        
        # Get file size for display
        file_size = file_path.stat().st_size
        if file_size < 1024:
            size_str = f"{file_size} bytes"
        elif file_size < 1024 * 1024:
            size_str = f"{file_size / 1024:.1f} KB"
        else:
            size_str = f"{file_size / (1024 * 1024):.1f} MB"
        
        return {
            "framework": framework or "Unknown",
            "confidence": "High" if framework else "Low",
            "size": size_str,
            "file_format": file_path.suffix.upper()[1:],  # Remove the dot
            "sample_output": normalized_output[:100] + "..." if normalized_output else "No content detected"
        }
        
    except Exception as e:
        return {
            "framework": "Error",
            "confidence": "N/A",
            "size": "Unknown",
            "file_format": file_path.suffix.upper()[1:],
            "sample_output": f"Error reading file: {e}"
        }


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"