"""
Fix Template Manager for ARC-Eval.

This module manages framework-specific fix templates and provides
production-ready code examples for common agent failure patterns.

Key Features:
- Framework-specific fix templates
- Production-ready, copy-paste code examples
- Cross-framework solution mapping
- Template validation and testing
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import importlib.util

logger = logging.getLogger(__name__)


@dataclass
class FixTemplate:
    """Represents a fix template for a specific failure pattern."""
    framework: str
    pattern_type: str
    subtype: str
    title: str
    description: str
    code_example: str
    implementation_steps: List[str]
    prerequisites: List[str]
    testing_notes: str
    business_impact: str
    difficulty: str  # 'beginner', 'intermediate', 'advanced'


@dataclass
class TemplateCollection:
    """Collection of templates for a specific framework and pattern type."""
    framework: str
    pattern_type: str
    templates: List[FixTemplate]
    cross_framework_alternatives: Dict[str, str]  # framework -> template_id


class TemplateManager:
    """
    Manages fix templates across all supported frameworks.
    
    Provides production-ready code examples and cross-framework
    solution mapping for universal failure patterns.
    """
    
    def __init__(self):
        """Initialize template manager with framework templates."""
        self.templates = {}
        self.template_index = {}
        self._load_templates()
    
    def get_fix_templates(
        self, 
        framework: str, 
        pattern_type: str, 
        subtype: Optional[str] = None
    ) -> List[FixTemplate]:
        """
        Get fix templates for specific framework and pattern.
        
        Args:
            framework: Target framework (langchain, crewai, autogen, etc.)
            pattern_type: Universal pattern type (tool_failures, planning_failures, etc.)
            subtype: Specific subtype (optional)
            
        Returns:
            List of applicable fix templates
        """
        framework_key = framework.lower()
        pattern_key = f"{framework_key}_{pattern_type}"
        
        if pattern_key not in self.templates:
            # Try generic templates
            pattern_key = f"generic_{pattern_type}"
        
        if pattern_key not in self.templates:
            return []
        
        templates = self.templates[pattern_key]
        
        if subtype:
            templates = [t for t in templates if t.subtype == subtype]
        
        return templates
    
    def get_cross_framework_alternatives(
        self, 
        source_framework: str, 
        target_framework: str, 
        pattern_type: str
    ) -> List[FixTemplate]:
        """
        Get alternative solutions from other frameworks.
        
        Args:
            source_framework: Framework with the issue
            target_framework: Framework to learn from
            pattern_type: Universal pattern type
            
        Returns:
            List of alternative fix templates from target framework
        """
        target_templates = self.get_fix_templates(target_framework, pattern_type)
        
        # Add cross-framework context to templates
        for template in target_templates:
            template.description = f"[Cross-Framework Insight from {target_framework.title()}] {template.description}"
        
        return target_templates
    
    def search_templates(
        self, 
        query: str, 
        framework: Optional[str] = None
    ) -> List[FixTemplate]:
        """
        Search templates by keyword or description.
        
        Args:
            query: Search query
            framework: Optional framework filter
            
        Returns:
            List of matching templates
        """
        results = []
        query_lower = query.lower()
        
        for template_list in self.templates.values():
            for template in template_list:
                if framework and template.framework.lower() != framework.lower():
                    continue
                
                # Search in title, description, and code example
                searchable_text = f"{template.title} {template.description} {template.code_example}".lower()
                if query_lower in searchable_text:
                    results.append(template)
        
        return results
    
    def validate_template(self, template: FixTemplate) -> Dict[str, Any]:
        """
        Validate a fix template for completeness and quality.
        
        Args:
            template: Template to validate
            
        Returns:
            Validation result with issues and suggestions
        """
        issues = []
        suggestions = []
        
        # Check required fields
        if not template.code_example.strip():
            issues.append("Missing code example")
        
        if not template.implementation_steps:
            issues.append("Missing implementation steps")
        
        if len(template.description) < 50:
            suggestions.append("Description could be more detailed")
        
        # Check code example quality
        if template.code_example:
            if "# TODO" in template.code_example:
                issues.append("Code example contains TODO comments")
            
            if len(template.code_example.split('\n')) < 5:
                suggestions.append("Code example could be more comprehensive")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "quality_score": max(0, 100 - len(issues) * 20 - len(suggestions) * 5)
        }
    
    def _load_templates(self):
        """Load all templates from framework-specific modules."""
        template_dir = Path(__file__).parent
        
        # Load templates from each framework directory
        for framework_dir in template_dir.iterdir():
            if framework_dir.is_dir() and framework_dir.name != "__pycache__":
                self._load_framework_templates(framework_dir)
    
    def _load_framework_templates(self, framework_dir: Path):
        """Load templates from a specific framework directory."""
        framework_name = framework_dir.name
        
        for template_file in framework_dir.glob("*.py"):
            if template_file.name.startswith("__"):
                continue
            
            try:
                # Import the template module
                spec = importlib.util.spec_from_file_location(
                    f"templates.{framework_name}.{template_file.stem}",
                    template_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Extract templates from module
                if hasattr(module, 'TEMPLATES'):
                    pattern_type = template_file.stem
                    key = f"{framework_name}_{pattern_type}"
                    self.templates[key] = module.TEMPLATES
                    
                    # Build index for fast lookup
                    for template in module.TEMPLATES:
                        template_id = f"{framework_name}_{pattern_type}_{template.subtype}"
                        self.template_index[template_id] = template
                        
            except Exception as e:
                logger.warning(f"Failed to load template {template_file}: {e}")


# Template validation utilities
def validate_code_syntax(code: str, framework: str) -> bool:
    """Validate that code example has correct syntax."""
    try:
        compile(code, '<template>', 'exec')
        return True
    except SyntaxError:
        return False


def extract_imports(code: str) -> List[str]:
    """Extract import statements from code example."""
    imports = []
    for line in code.split('\n'):
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            imports.append(line)
    return imports


def estimate_implementation_time(template: FixTemplate) -> str:
    """Estimate implementation time based on template complexity."""
    complexity_scores = {
        'beginner': 1,
        'intermediate': 2,
        'advanced': 3
    }
    
    base_score = complexity_scores.get(template.difficulty, 2)
    step_count = len(template.implementation_steps)
    code_complexity = len(template.code_example.split('\n'))
    
    total_score = base_score + (step_count * 0.5) + (code_complexity * 0.1)
    
    if total_score < 2:
        return "15-30 minutes"
    elif total_score < 4:
        return "30-60 minutes"
    elif total_score < 6:
        return "1-2 hours"
    else:
        return "2+ hours"


# Template quality metrics
def calculate_template_quality_score(template: FixTemplate) -> float:
    """Calculate quality score for a template (0-100)."""
    score = 100.0
    
    # Deduct points for missing or poor content
    if not template.code_example.strip():
        score -= 30
    elif len(template.code_example.split('\n')) < 5:
        score -= 10
    
    if not template.implementation_steps:
        score -= 20
    elif len(template.implementation_steps) < 3:
        score -= 10
    
    if len(template.description) < 50:
        score -= 15
    
    if not template.testing_notes.strip():
        score -= 10
    
    if not template.business_impact.strip():
        score -= 10
    
    # Bonus points for comprehensive content
    if len(template.code_example.split('\n')) > 20:
        score += 5
    
    if len(template.implementation_steps) > 5:
        score += 5
    
    return max(0, min(100, score))
