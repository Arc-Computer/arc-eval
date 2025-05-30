"""Generate actionable fix instructions from failure patterns."""

from typing import Dict, List, Any
from collections import defaultdict


class FixGenerator:
    """Generate copy-paste fix instructions based on failure patterns."""
    
    def __init__(self):
        self.domain_fixes = {
            "finance": self._finance_fixes,
            "security": self._security_fixes,
            "ml": self._ml_fixes
        }
    
    def generate_fixes(self, patterns: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate domain-specific fix instructions from patterns."""
        fixes_by_domain = defaultdict(list)
        
        for pattern in patterns:
            domain = pattern.get("domain", "general")
            failure = pattern.get("failure_reason", "")
            scenario_id = pattern.get("scenario_id", "")
            
            if domain in self.domain_fixes:
                fix = self.domain_fixes[domain](scenario_id, failure, pattern)
                if fix:
                    fixes_by_domain[domain].append(fix)
        
        return dict(fixes_by_domain)
    
    def _finance_fixes(self, scenario_id: str, failure: str, pattern: Dict) -> str:
        """Generate finance-specific fixes."""
        if "transaction" in failure.lower():
            return f"""
# Fix for {scenario_id}: Transaction Validation
Add validation before processing:
```python
if amount > 10000:
    require_compliance_check = True
    log_large_transaction(transaction_id, amount)
```
Compliance: SOX Section 404 - Internal Controls"""

        elif "kyc" in failure.lower():
            return f"""
# Fix for {scenario_id}: KYC Verification
Implement identity verification:
```python
if not customer.kyc_verified:
    raise ComplianceError("KYC verification required")
```
Compliance: AML/KYC regulations"""
        
        return pattern.get("remediation", "")
    
    def _security_fixes(self, scenario_id: str, failure: str, pattern: Dict) -> str:
        """Generate security-specific fixes."""
        if "injection" in failure.lower():
            return f"""
# Fix for {scenario_id}: Injection Prevention
Sanitize all inputs:
```python
from security import sanitize_input
clean_input = sanitize_input(user_input)
```
Compliance: OWASP Top 10 - A03:2021 Injection"""

        elif "authentication" in failure.lower():
            return f"""
# Fix for {scenario_id}: Authentication
Implement proper auth checks:
```python
@require_authentication
@require_role(['admin', 'user'])
def protected_endpoint():
    pass
```
Compliance: Zero Trust Security Model"""
        
        return pattern.get("remediation", "")
    
    def _ml_fixes(self, scenario_id: str, failure: str, pattern: Dict) -> str:
        """Generate ML-specific fixes."""
        if "bias" in failure.lower():
            return f"""
# Fix for {scenario_id}: Bias Detection
Add fairness metrics:
```python
from ml_fairness import demographic_parity
fairness_score = demographic_parity(predictions, sensitive_attrs)
if fairness_score < 0.8:
    log_bias_warning(model_id, fairness_score)
```
Compliance: EU AI Act - High Risk Systems"""

        elif "explainability" in failure.lower():
            return f"""
# Fix for {scenario_id}: Model Explainability
Add explanation generation:
```python
from explainers import SHAPExplainer
explainer = SHAPExplainer(model)
explanation = explainer.explain(prediction)
```
Compliance: GDPR Article 22 - Automated Decision Making"""
        
        return pattern.get("remediation", "")
