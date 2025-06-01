"""
Input Helper Functions for Easy JSON Ingestion

Simple utilities to make JSON input frictionless for users with smart file discovery,
clipboard support, and framework auto-detection.
"""

import json
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from rich.console import Console

console = Console()


class InputHelper:
    """Smart input utilities for JSON file discovery and validation."""
    
    @staticmethod
    def scan_directory(directory: str = ".") -> List[Path]:
        """Scan directory for potential agent output files."""
        directory = Path(directory)
        candidates = []
        
        # Common patterns for agent output files
        patterns = [
            "*.json",
            "*output*.json", 
            "*trace*.json",
            "*agent*.json",
            "*response*.json",
            "*result*.json"
        ]
        
        for pattern in patterns:
            candidates.extend(directory.glob(pattern))
        
        # Remove duplicates and sort by modification time
        unique_candidates = list(set(candidates))
        unique_candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        return unique_candidates
    
    @staticmethod
    def quick_validate_json(file_path: Path) -> Dict[str, Any]:
        """Quick validation of JSON file for common issues."""
        result = {
            "valid": False,
            "size_mb": 0.0,
            "entries": 0,
            "framework": "unknown",
            "issues": []
        }
        
        try:
            # Check file size
            size_bytes = file_path.stat().st_size
            result["size_mb"] = size_bytes / (1024 * 1024)
            
            if size_bytes == 0:
                result["issues"].append("File is empty")
                return result
            
            if size_bytes > 50 * 1024 * 1024:  # 50MB
                result["issues"].append("File is very large (>50MB)")
            
            # Try to parse JSON
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Count entries
            if isinstance(data, list):
                result["entries"] = len(data)
                # Check first entry for framework
                if data and isinstance(data[0], dict):
                    result["framework"] = InputHelper._detect_framework_simple(data[0])
            elif isinstance(data, dict):
                result["entries"] = 1
                result["framework"] = InputHelper._detect_framework_simple(data)
            
            result["valid"] = True
            
        except json.JSONDecodeError as e:
            result["issues"].append(f"Invalid JSON: {str(e)[:100]}")
        except Exception as e:
            result["issues"].append(f"File error: {str(e)[:100]}")
        
        return result
    
    @staticmethod
    def _detect_framework_simple(data: Dict[str, Any]) -> str:
        """Simple framework detection for display."""
        if "choices" in data:
            return "OpenAI"
        elif "content" in data and isinstance(data["content"], list):
            return "Anthropic"
        elif "crew_output" in data:
            return "CrewAI"
        elif "intermediate_steps" in data:
            return "LangChain"
        elif "messages" in data and "graph_state" in data:
            return "LangGraph"
        elif "output" in data:
            return "Generic"
        else:
            return "Unknown"
    
    @staticmethod
    def save_clipboard_to_temp() -> Optional[Path]:
        """Save clipboard content to temporary JSON file."""
        try:
            import pyperclip
            clipboard_content = pyperclip.paste()
            
            # Validate it's JSON
            try:
                json.loads(clipboard_content)
            except json.JSONDecodeError:
                console.print("[red]❌ Clipboard content is not valid JSON[/red]")
                return None
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(clipboard_content)
                temp_path = Path(f.name)
            
            console.print(f"[green]📋 Clipboard saved to: {temp_path}[/green]")
            return temp_path
            
        except ImportError:
            console.print("[yellow]📋 Install pyperclip for clipboard support: pip install pyperclip[/yellow]")
            return None
        except Exception as e:
            console.print(f"[red]❌ Clipboard error: {e}[/red]")
            return None
    
    @staticmethod
    def display_file_candidates(candidates: List[Path]) -> None:
        """Display found files with quick validation."""
        if not candidates:
            console.print("[yellow]❌ No JSON files found in current directory[/yellow]")
            console.print("\n[blue]💡 Tips:[/blue]")
            console.print("• Copy agent output to clipboard, then run: [green]arc-eval compliance --domain <your-domain> --input clipboard[/green]")
            console.print("• Save agent output to a .json file")
            console.print("• Try quick-start mode: [green]arc-eval compliance --domain <your-domain> --quick-start[/green]")
            return
        
        console.print(f"[green]🔍 Found {len(candidates)} potential trace files:[/green]\n")
        
        from rich.table import Table
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("#", width=3)
        table.add_column("File", style="cyan")
        table.add_column("Size", width=8)
        table.add_column("Entries", width=8)
        table.add_column("Framework", width=12)
        table.add_column("Status", width=12)
        
        for i, candidate in enumerate(candidates[:10], 1):  # Show top 10
            validation = InputHelper.quick_validate_json(candidate)
            
            size_str = f"{validation['size_mb']:.1f}MB" if validation['size_mb'] >= 1 else f"{int(validation['size_mb']*1024)}KB"
            entries_str = str(validation['entries']) if validation['valid'] else "?"
            framework = validation['framework'] if validation['valid'] else "Invalid"
            status = "[green]✅ Valid[/green]" if validation['valid'] else "[red]❌ Invalid[/red]"
            
            if validation['issues']:
                status = f"[yellow]⚠️ {validation['issues'][0][:20]}[/yellow]"
            
            table.add_row(
                str(i),
                candidate.name,
                size_str,
                entries_str,
                framework,
                status
            )
        
        console.print(table)
        
        if candidates:
            console.print(f"\n[blue]💡 To use file #1:[/blue]")
            console.print(f"  [green]arc-eval compliance --domain <your-domain> --input {candidates[0]}[/green]")


def handle_smart_input(input_value: str, scan_folder: bool = False) -> Optional[Path]:
    """Handle smart input resolution with auto-discovery and clipboard support."""
    helper = InputHelper()
    
    # Special handling for clipboard
    if input_value == "clipboard":
        return helper.save_clipboard_to_temp()
    
    # Special handling for folder scan
    if scan_folder or input_value == "scan":
        candidates = helper.scan_directory()
        helper.display_file_candidates(candidates)
        
        if candidates:
            # Return the most recent file
            return candidates[0]
        return None
    
    # Regular file path
    file_path = Path(input_value)
    if file_path.exists():
        return file_path
    
    # If file doesn't exist, maybe it's a pattern or folder
    if file_path.parent.exists() and file_path.parent.is_dir():
        # Try to find similar files
        pattern = file_path.name
        matches = list(file_path.parent.glob(pattern))
        if matches:
            console.print(f"[green]🔍 Found matching file: {matches[0]}[/green]")
            return matches[0]
    
    console.print(f"[red]❌ File not found: {input_value}[/red]")
    return None