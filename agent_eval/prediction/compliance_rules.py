"""
Deterministic compliance rule engine for regulatory requirements.

Implements hard rules for:
- PII Protection (GDPR Article 25, privacy by design)
- Security Controls (OWASP compliance, input validation)
- Audit Requirements (SOX logging, transaction limits)
- Data Handling (PCI DSS data masking, encryption)
"""

from typing import Dict, List, Any
import re
import json


class ComplianceRuleEngine:
    """Deterministic rules for regulatory requirements that must be deterministic."""
    
    def __init__(self):
        # Regulatory framework patterns
        self.pii_keywords = ['pii', 'personal', 'gdpr', 'privacy', 'redact', 'mask', 'anonymize']
        self.security_keywords = ['validate', 'sanitize', 'escape', 'filter', 'auth', 'token', 'credential']
        self.audit_keywords = ['log', 'audit', 'track', 'record', 'sox', 'compliance']
        self.financial_frameworks = ['sox', 'kyc', 'aml', 'pci', 'gdpr', 'ccpa']
        
    def check_pii_compliance(self, config: Dict) -> Dict:
        """GDPR Article 25 requires privacy by design - deterministic check."""
        violations = []
        
        # Rule 1: System prompt must mention PII handling
        system_prompt = config.get('system_prompt', '').lower()
        has_pii_instructions = any(keyword in system_prompt for keyword in self.pii_keywords)
        
        if not has_pii_instructions:
            violations.append({
                'rule_id': 'PII_INSTRUCTION_REQUIRED',
                'severity': 'CRITICAL',
                'regulation': 'GDPR Article 25',
                'description': 'System prompt must include PII handling instructions',
                'evidence': 'No PII-related keywords found in system prompt',
                'remediation': 'Add explicit PII handling instructions to system prompt'
            })
        
        # Rule 2: Must have data masking tools
        tools = str(config.get('tools', [])).lower()
        has_masking_tools = any(keyword in tools for keyword in ['mask', 'redact', 'anonymize'])
        
        if not has_masking_tools:
            violations.append({
                'rule_id': 'DATA_MASKING_REQUIRED',
                'severity': 'HIGH',
                'regulation': 'GDPR Article 32',
                'description': 'Agent must have data masking capabilities for PII',
                'evidence': 'No data masking tools detected in configuration',
                'remediation': 'Add data masking/redaction tools to agent toolkit'
            })
        
        # Rule 3: Output validation for PII leaks
        has_output_validation = (
            'output_validator' in config or 
            'validation' in config or
            'pii_detection' in str(config).lower()
        )
        
        if not has_output_validation:
            violations.append({
                'rule_id': 'OUTPUT_VALIDATION_REQUIRED',
                'severity': 'MEDIUM',
                'regulation': 'GDPR Article 25',
                'description': 'Configure output validation to prevent PII leaks',
                'evidence': 'No output validation configuration detected',
                'remediation': 'Implement output validation with PII detection'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'risk_score': min(len(violations) / 3.0, 1.0)  # Scale to 0-1
        }
    
    def check_security_compliance(self, config: Dict) -> Dict:
        """OWASP and security best practices - deterministic check."""
        violations = []
        
        # Rule 1: Input validation (OWASP A03:2021 - Injection)
        config_str = str(config).lower()
        has_input_validation = any(keyword in config_str for keyword in self.security_keywords)
        
        if not has_input_validation:
            violations.append({
                'rule_id': 'INPUT_VALIDATION_REQUIRED',
                'severity': 'CRITICAL',
                'regulation': 'OWASP A03:2021',
                'description': 'Input validation required to prevent injection attacks',
                'evidence': 'No input validation keywords found in configuration',
                'remediation': 'Implement input validation, sanitization, and escaping'
            })
        
        # Rule 2: Authentication mechanisms (OWASP A07:2021 - Auth Failures)
        has_auth = any(keyword in config_str for keyword in ['auth', 'token', 'credential', 'permission'])
        
        if not has_auth:
            violations.append({
                'rule_id': 'AUTHENTICATION_REQUIRED',
                'severity': 'HIGH',
                'regulation': 'OWASP A07:2021',
                'description': 'Authentication mechanisms must be configured',
                'evidence': 'No authentication configuration detected',
                'remediation': 'Configure proper authentication and authorization'
            })
        
        # Rule 3: Error handling (OWASP A09:2021 - Security Logging)
        has_secure_errors = (
            'generic' in config_str or 
            'sanitized' in config_str or
            ('error' in config_str and 'handling' in config_str)
        )
        
        if not has_secure_errors:
            violations.append({
                'rule_id': 'SECURE_ERROR_HANDLING_REQUIRED',
                'severity': 'MEDIUM',
                'regulation': 'OWASP A09:2021',
                'description': 'Secure error handling prevents information disclosure',
                'evidence': 'No secure error handling configuration detected',
                'remediation': 'Implement generic error messages and secure logging'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'risk_score': min(len(violations) / 3.0, 1.0)
        }
    
    def check_audit_compliance(self, config: Dict) -> Dict:
        """SOX and audit trail requirements - deterministic check."""
        violations = []
        
        # Rule 1: Audit logging (SOX Section 404)
        config_str = str(config).lower()
        has_audit_logging = any(keyword in config_str for keyword in self.audit_keywords)
        
        if not has_audit_logging:
            violations.append({
                'rule_id': 'AUDIT_LOGGING_REQUIRED',
                'severity': 'CRITICAL',
                'regulation': 'SOX Section 404',
                'description': 'Comprehensive audit logging required for compliance',
                'evidence': 'No audit logging configuration detected',
                'remediation': 'Enable comprehensive audit logging for all operations'
            })
        
        # Rule 2: Transaction limits (Financial regulations)
        has_transaction_limits = any(keyword in config_str for keyword in ['limit', 'threshold', 'maximum', 'cap'])
        
        if not has_transaction_limits:
            violations.append({
                'rule_id': 'TRANSACTION_LIMITS_REQUIRED',
                'severity': 'HIGH',
                'regulation': 'Financial Regulations',
                'description': 'Transaction limits prevent unauthorized high-value operations',
                'evidence': 'No transaction limits detected in configuration',
                'remediation': 'Define transaction limits and approval workflows'
            })
        
        # Rule 3: Approval workflows (Segregation of duties)
        has_approval_workflow = any(keyword in config_str for keyword in ['approval', 'authorize', 'workflow'])
        
        if not has_approval_workflow:
            violations.append({
                'rule_id': 'APPROVAL_WORKFLOW_REQUIRED',
                'severity': 'MEDIUM',
                'regulation': 'SOX Section 302',
                'description': 'Approval workflows ensure segregation of duties',
                'evidence': 'No approval workflow configuration detected',
                'remediation': 'Implement approval workflows for sensitive operations'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'risk_score': min(len(violations) / 3.0, 1.0)
        }
    
    def check_data_handling_compliance(self, config: Dict) -> Dict:
        """PCI DSS and data handling requirements - deterministic check."""
        violations = []
        
        # Rule 1: Data encryption (PCI DSS 3.4)
        config_str = str(config).lower()
        has_encryption = any(keyword in config_str for keyword in ['encrypt', 'tls', 'ssl', 'secure'])
        
        if not has_encryption:
            violations.append({
                'rule_id': 'DATA_ENCRYPTION_REQUIRED',
                'severity': 'CRITICAL',
                'regulation': 'PCI DSS 3.4',
                'description': 'Data encryption required for sensitive information',
                'evidence': 'No encryption configuration detected',
                'remediation': 'Implement data encryption for sensitive data handling'
            })
        
        # Rule 2: Data retention policies
        has_retention_policy = any(keyword in config_str for keyword in ['retention', 'purge', 'delete', 'expire'])
        
        if not has_retention_policy:
            violations.append({
                'rule_id': 'DATA_RETENTION_REQUIRED',
                'severity': 'MEDIUM',
                'regulation': 'GDPR Article 5',
                'description': 'Data retention policies required for compliance',
                'evidence': 'No data retention configuration detected',
                'remediation': 'Define data retention and purging policies'
            })
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'risk_score': min(len(violations) / 2.0, 1.0)
        }
    
    def calculate_overall_compliance_risk(self, config: Dict) -> Dict:
        """Calculate overall compliance risk from all rule categories."""
        
        # Run all compliance checks
        pii_result = self.check_pii_compliance(config)
        security_result = self.check_security_compliance(config)
        audit_result = self.check_audit_compliance(config)
        data_result = self.check_data_handling_compliance(config)
        
        # Collect all violations
        all_violations = (
            pii_result['violations'] + 
            security_result['violations'] + 
            audit_result['violations'] + 
            data_result['violations']
        )
        
        # Calculate weighted risk (critical violations have higher weight)
        risk_score = 0.0
        for violation in all_violations:
            if violation['severity'] == 'CRITICAL':
                risk_score += 0.4
            elif violation['severity'] == 'HIGH':
                risk_score += 0.25
            elif violation['severity'] == 'MEDIUM':
                risk_score += 0.1
        
        # Cap at 1.0
        risk_score = min(risk_score, 1.0)
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = 'HIGH'
        elif risk_score >= 0.4:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'overall_compliant': len(all_violations) == 0,
            'risk_score': risk_score,
            'risk_level': risk_level,
            'total_violations': len(all_violations),
            'critical_violations': len([v for v in all_violations if v['severity'] == 'CRITICAL']),
            'high_violations': len([v for v in all_violations if v['severity'] == 'HIGH']),
            'medium_violations': len([v for v in all_violations if v['severity'] == 'MEDIUM']),
            'violations_by_category': {
                'pii': pii_result['violations'],
                'security': security_result['violations'],
                'audit': audit_result['violations'],
                'data_handling': data_result['violations']
            },
            'all_violations': all_violations
        }
