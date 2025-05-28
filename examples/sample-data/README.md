# Sample Data Sets

Sample datasets for demonstrating ARC-Eval core loop workflow with before/after comparisons.

## Usage

### **Complete Core Loop Workflow**
```bash
# Step 1: Baseline evaluation 
arc-eval --domain finance --input examples/sample-data/finance_baseline.json --agent-judge

# Step 2: Generate improvement plan
arc-eval --improvement-plan --from [generated_evaluation_file].json

# Step 3: Compare with improved data
arc-eval --domain finance --input examples/sample-data/finance_improved.json --baseline [baseline_evaluation_file].json
```

## Dataset Descriptions

### **Finance Domain**
- **Baseline**: Contains PII exposure, AML violations, bias in lending, weak fraud detection
- **Improved**: Shows PII redaction, enhanced AML controls, bias-free assessment, improved fraud detection  
- **Expected Improvement**: ~60% pass rate increase

### **Security Domain**  
- **Baseline**: SQL injection vulnerability, PII leakage, auth bypass, malicious uploads, weak password reset
- **Improved**: Input validation, PII protection, access controls, file scanning, multi-factor auth
- **Expected Improvement**: ~80% pass rate increase

### **ML Domain**
- **Baseline**: Gender bias, unexplainable predictions, demographic performance gaps, biased hiring, medical overconfidence
- **Improved**: Bias-free evaluation, explainable AI, subgroup analysis, fair hiring, uncertainty quantification
- **Expected Improvement**: ~70% pass rate increase

### **MCP Security Sample**
- **File**: `mcp_security_sample.json`
- **Purpose**: Representative examples from each MCP security category for testing
- **Categories**: Tool poisoning (ml_131, ml_132), obfuscation (ml_133), server attacks (ml_136), behavior modification (ml_140)
- **Selection Criteria**: One scenario from each of the 5 MCP security categories to demonstrate evaluation workflow and AI-powered improvement plan generation

## Demonstration Strategy

### **Finance Domain Use Cases**
Focus on regulatory compliance (SOX, AML, KYC) and bias detection in financial decisions.

**Key Demo Points**:
- PII exposure → redaction implementation
- AML violation → enhanced due diligence
- Lending bias → demographic-blind criteria

### **Security Domain Use Cases**
Focus on OWASP LLM Top 10 compliance and prompt injection vulnerabilities.

**Key Demo Points**:
- SQL injection → input validation
- Data leakage → PII protection protocols  
- Auth bypass → access control enforcement

### **ML Domain Use Cases**
Focus on algorithmic bias, explainability, and ethical AI practices.

**Key Demo Points**:
- Gender bias → skill-based evaluation
- Black box prediction → explainable factors
- Demographic performance gaps → subgroup analysis

## Expected Outcomes

### **Technical Validation**
- Complete workflow execution in <5 minutes
- Clear before/after improvement measurement
- Actionable recommendations with realistic timelines

### **User Value Validation**
- User recognizes implementation value 
- Regular usage intention expressed
- Clear workflow integration benefits

## Troubleshooting

### **If Data Format Issues**
```bash
# Check supported formats
arc-eval --help-input

# Use sample data as backup
arc-eval --domain [domain] --input examples/sample-data/[domain]_baseline.json --agent-judge
```

### **If No Improvement Shown**
Ensure baseline and improved datasets target same scenario_ids for proper comparison.

### **If Technical Errors**
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check file format
cat examples/sample-data/finance_baseline.json | jq .
```