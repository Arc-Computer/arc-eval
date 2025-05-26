#!/usr/bin/env python3
"""
Generate enhanced agent traces with tool calls, reasoning, and performance metrics.
Creates enterprise-grade tracing examples for LangSmith/Langfuse-style evaluation.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
OUTPUTS_DIR = BASE_DIR / "examples" / "agent-outputs"

# Common tools by domain
FINANCE_TOOLS = [
    "kyc_verification_api", "sanctions_check_api", "aml_screening_tool", 
    "fraud_detection_api", "compliance_validator", "transaction_monitor",
    "credit_check_api", "identity_verification", "document_analyzer"
]

SECURITY_TOOLS = [
    "vulnerability_scanner", "threat_intelligence_api", "malware_detector",
    "network_analyzer", "credential_validator", "access_control_checker",
    "incident_response_api", "security_policy_engine", "audit_logger"
]

ML_TOOLS = [
    "model_registry_api", "data_validation_tool", "drift_detector",
    "bias_analyzer", "performance_monitor", "feature_store_api",
    "experiment_tracker", "model_governance_api", "pipeline_validator"
]

def generate_reasoning_step(step_num, context, domain):
    """Generate realistic reasoning step based on domain context."""
    reasoning_templates = {
        'finance': [
            f"Step {step_num}: Need to verify customer identity against sanctions lists",
            f"Step {step_num}: Checking transaction patterns for AML compliance",
            f"Step {step_num}: Analyzing risk factors for KYC approval decision",
            f"Step {step_num}: Evaluating fraud indicators in transaction history",
            f"Step {step_num}: Determining compliance requirements for this jurisdiction"
        ],
        'security': [
            f"Step {step_num}: Analyzing input for potential security threats",
            f"Step {step_num}: Checking for known attack patterns in request",
            f"Step {step_num}: Validating user permissions and access controls",
            f"Step {step_num}: Scanning for malicious content or injection attempts",
            f"Step {step_num}: Evaluating security policy compliance"
        ],
        'ml': [
            f"Step {step_num}: Validating model inputs for data drift",
            f"Step {step_num}: Checking model performance against baseline metrics",
            f"Step {step_num}: Analyzing feature importance and bias indicators",
            f"Step {step_num}: Evaluating model governance compliance",
            f"Step {step_num}: Determining deployment readiness criteria"
        ]
    }
    
    return {
        "step": step_num,
        "action": "reasoning",
        "content": random.choice(reasoning_templates[domain]),
        "duration_ms": random.randint(150, 400),
        "timestamp": datetime.now().isoformat() + 'Z'
    }

def generate_tool_call(step_num, tool_name, domain, should_fail=False):
    """Generate realistic tool call with inputs/outputs based on domain."""
    
    # Domain-specific tool inputs/outputs
    tool_examples = {
        'finance': {
            'kyc_verification_api': {
                'input': {"customer_id": "CUST_12345", "document_type": "passport", "ssn_last4": "6789"},
                'success_output': {"verified": True, "confidence": 0.95, "document_valid": True},
                'fail_output': {"verified": False, "confidence": 0.23, "reason": "Document mismatch"}
            },
            'sanctions_check_api': {
                'input': {"name": "John Smith", "dob": "1985-03-15", "jurisdiction": "US"},
                'success_output': {"match_found": False, "confidence": 0.98, "lists_checked": ["OFAC", "UN", "EU"]},
                'fail_output': {"match_found": True, "confidence": 0.89, "matched_list": "OFAC", "risk_level": "HIGH"}
            },
            'fraud_detection_api': {
                'input': {"transaction_amount": 50000, "merchant": "crypto_exchange", "location": "unknown"},
                'success_output': {"fraud_score": 0.15, "risk_level": "LOW", "indicators": []},
                'fail_output': {"fraud_score": 0.87, "risk_level": "HIGH", "indicators": ["unusual_location", "high_amount"]}
            }
        },
        'security': {
            'vulnerability_scanner': {
                'input': {"target": "api.company.com", "scan_type": "web_app", "auth_required": True},
                'success_output': {"vulnerabilities": [], "risk_score": 0.1, "scan_complete": True},
                'fail_output': {"vulnerabilities": ["SQL_INJECTION", "XSS"], "risk_score": 0.85, "critical_count": 2}
            },
            'threat_intelligence_api': {
                'input': {"ip_address": "192.168.1.100", "domain": "suspicious-site.com"},
                'success_output': {"threat_level": "LOW", "reputation": "clean", "last_seen": None},
                'fail_output': {"threat_level": "HIGH", "reputation": "malicious", "categories": ["malware", "phishing"]}
            },
            'credential_validator': {
                'input': {"username": "admin", "password_hash": "***", "context": "privileged_access"},
                'success_output': {"valid": True, "strength": "strong", "compromise_check": "clean"},
                'fail_output': {"valid": False, "reason": "breached_credentials", "last_breach": "2024-01-15"}
            }
        },
        'ml': {
            'drift_detector': {
                'input': {"model_id": "fraud_v2.1", "data_window": "7d", "baseline": "training_set"},
                'success_output': {"drift_score": 0.12, "drift_detected": False, "stability": "STABLE"},
                'fail_output': {"drift_score": 0.78, "drift_detected": True, "affected_features": ["income", "age"]}
            },
            'bias_analyzer': {
                'input': {"model_predictions": "batch_001", "protected_attributes": ["gender", "race"]},
                'success_output': {"bias_score": 0.05, "fairness_met": True, "demographic_parity": 0.03},
                'fail_output': {"bias_score": 0.34, "fairness_met": False, "disparate_impact": 0.67}
            },
            'model_governance_api': {
                'input': {"model_id": "credit_scoring_v3", "deployment_stage": "production"},
                'success_output': {"approved": True, "compliance_score": 0.94, "documentation_complete": True},
                'fail_output': {"approved": False, "missing_docs": ["bias_assessment", "performance_report"]}
            }
        }
    }
    
    if tool_name not in tool_examples[domain]:
        # Generic tool call
        tool_input = {"query": "generic_input", "context": domain}
        tool_output = {"success": not should_fail, "result": "generic_output"}
    else:
        tool_data = tool_examples[domain][tool_name]
        tool_input = tool_data['input']
        tool_output = tool_data['fail_output'] if should_fail else tool_data['success_output']
    
    return {
        "step": step_num,
        "action": "tool_call",
        "tool": tool_name,
        "input": tool_input,
        "output": tool_output,
        "duration_ms": random.randint(800, 3000),
        "success": not should_fail,
        "timestamp": datetime.now().isoformat() + 'Z'
    }

def generate_enhanced_trace(scenario, domain, should_fail=False):
    """Generate comprehensive trace with reasoning and tool calls."""
    
    # Determine tools for domain
    if domain == 'finance':
        available_tools = FINANCE_TOOLS
    elif domain == 'security':
        available_tools = SECURITY_TOOLS
    elif domain == 'ml':
        available_tools = ML_TOOLS
    else:
        available_tools = ["generic_tool"]
    
    # Generate trace steps
    steps = []
    step_count = 1
    
    # Start with reasoning
    steps.append(generate_reasoning_step(step_count, scenario, domain))
    step_count += 1
    
    # Add 2-4 tool calls with reasoning between
    num_tools = random.randint(2, 4)
    for i in range(num_tools):
        # Tool call
        tool = random.choice(available_tools)
        tool_should_fail = should_fail and (i == num_tools - 1)  # Last tool fails if scenario should fail
        steps.append(generate_tool_call(step_count, tool, domain, tool_should_fail))
        step_count += 1
        
        # Reasoning after tool (except last)
        if i < num_tools - 1:
            steps.append(generate_reasoning_step(step_count, f"Processing {tool} results", domain))
            step_count += 1
    
    # Final reasoning
    steps.append(generate_reasoning_step(step_count, "Formulating final response", domain))
    
    # Calculate totals
    total_duration = sum(step.get('duration_ms', 0) for step in steps)
    tool_calls = [step for step in steps if step['action'] == 'tool_call']
    reasoning_steps = [step for step in steps if step['action'] == 'reasoning']
    
    # Determine failure point
    failure_point = None
    if should_fail:
        failed_tools = [step for step in tool_calls if not step.get('success', True)]
        if failed_tools:
            failure_point = failed_tools[-1]['tool']
    
    return {
        "steps": steps,
        "total_duration_ms": total_duration,
        "tool_calls_count": len(tool_calls),
        "reasoning_steps_count": len(reasoning_steps),
        "success": not should_fail,
        "failure_point": failure_point,
        "trace_id": str(uuid.uuid4()),
        "session_id": str(uuid.uuid4())[:8]
    }

def enhance_agent_output(output_entry, domain):
    """Add enhanced tracing to existing agent output."""
    should_fail = output_entry.get('expected_to_fail', False)
    scenario = output_entry.get('scenario', 'unknown')
    
    # Generate enhanced trace
    trace = generate_enhanced_trace(scenario, domain, should_fail)
    
    # Add enhanced fields
    enhanced_output = output_entry.copy()
    enhanced_output.update({
        "trace": trace,
        "performance_metrics": {
            "total_latency_ms": trace['total_duration_ms'],
            "tool_call_latency_ms": sum(step['duration_ms'] for step in trace['steps'] if step['action'] == 'tool_call'),
            "reasoning_latency_ms": sum(step['duration_ms'] for step in trace['steps'] if step['action'] == 'reasoning'),
            "token_usage": {
                "prompt_tokens": random.randint(500, 2000),
                "completion_tokens": random.randint(100, 800),
                "total_tokens": random.randint(600, 2800)
            },
            "cost_usd": round(random.uniform(0.01, 0.15), 4)
        },
        "evaluation_context": {
            "complexity_score": random.uniform(0.3, 0.9),
            "risk_assessment": "HIGH" if should_fail else random.choice(["LOW", "MEDIUM"]),
            "compliance_frameworks": get_compliance_frameworks(domain),
            "evaluation_timestamp": datetime.now().isoformat() + 'Z'
        }
    })
    
    return enhanced_output

def get_compliance_frameworks(domain):
    """Get relevant compliance frameworks for domain."""
    frameworks = {
        'finance': ["SOX", "KYC", "AML", "PCI-DSS", "GDPR"],
        'security': ["NIST", "ISO27001", "OWASP", "GDPR", "SOC2"],
        'ml': ["EU AI Act", "ISO23053", "NIST AI RMF", "GDPR", "IEEE Standards"]
    }
    return frameworks.get(domain, ["Generic Compliance"])

def create_enhanced_traces(domain):
    """Create enhanced traces for a domain."""
    input_file = OUTPUTS_DIR / f"complete_{domain}_outputs.json"
    output_file = OUTPUTS_DIR / f"enhanced_{domain}_traces.json"
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return 0
    
    # Load existing outputs
    with open(input_file, 'r') as f:
        outputs = json.load(f)
    
    print(f"🔍 Enhancing {len(outputs)} outputs for {domain} domain...")
    
    # Enhance each output with tracing
    enhanced_outputs = []
    for output in outputs:
        enhanced = enhance_agent_output(output, domain)
        enhanced_outputs.append(enhanced)
    
    # Save enhanced outputs
    with open(output_file, 'w') as f:
        json.dump(enhanced_outputs, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced {len(enhanced_outputs)} traces for {domain} → {output_file}")
    return len(enhanced_outputs)

def main():
    """Generate enhanced traces for all domains."""
    print("🚀 Generating Enhanced Agent Traces with Tool Calls & Performance Metrics...")
    print("=" * 70)
    
    total_enhanced = 0
    domains = ['finance', 'security', 'ml']
    
    for domain in domains:
        count = create_enhanced_traces(domain)
        total_enhanced += count
        print()
    
    print("🎉 Enhanced Tracing Complete!")
    print(f"📈 Total traces enhanced: {total_enhanced}")
    print(f"📁 Enhanced files saved to: {OUTPUTS_DIR}")
    print()
    print("🔍 Enhanced Features Added:")
    print("   • Step-by-step reasoning traces")
    print("   • Tool call chains with inputs/outputs")  
    print("   • Performance metrics (latency, tokens, cost)")
    print("   • Compliance framework mapping")
    print("   • Failure point identification")
    print("   • Session and trace IDs for correlation")
    print()
    print("🚀 Usage Examples:")
    print("   # Run Agent-as-a-Judge with enhanced traces:")
    print("   arc-eval --domain finance --input examples/agent-outputs/enhanced_finance_traces.json --agent-judge")
    print("   arc-eval --domain security --input examples/agent-outputs/enhanced_security_traces.json --agent-judge")
    print("   arc-eval --domain ml --input examples/agent-outputs/enhanced_ml_traces.json --agent-judge")

if __name__ == "__main__":
    main()