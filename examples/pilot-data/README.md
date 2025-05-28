# Pilot Data Sets

Sample datasets for demonstrating ARC-Eval core loop workflow during customer pilots.

## Usage

### **Complete Pilot Workflow**
```bash
# Step 1: Baseline evaluation 
arc-eval --domain finance --input examples/pilot-data/finance_baseline.json --agent-judge

# Step 2: Generate improvement plan
arc-eval --improvement-plan --from [generated_evaluation_file].json

# Step 3: Compare with improved data
arc-eval --domain finance --input examples/pilot-data/finance_improved.json --baseline [baseline_evaluation_file].json
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

## Pilot Demonstration Strategy

### **For Finance Customers (Snowflake, BlackRock)**
Focus on regulatory compliance (SOX, AML, KYC) and bias detection in financial decisions.

**Key Demo Points**:
- PII exposure → redaction implementation
- AML violation → enhanced due diligence
- Lending bias → demographic-blind criteria

### **For Security Customers (Palo Alto)**
Focus on OWASP LLM Top 10 compliance and prompt injection vulnerabilities.

**Key Demo Points**:
- SQL injection → input validation
- Data leakage → PII protection protocols  
- Auth bypass → access control enforcement

### **For ML Customers (NVIDIA)**
Focus on algorithmic bias, explainability, and ethical AI practices.

**Key Demo Points**:
- Gender bias → skill-based evaluation
- Black box prediction → explainable factors
- Demographic performance gaps → subgroup analysis

## Expected Pilot Outcomes

### **Technical Validation**
- Complete workflow execution in <5 minutes
- Clear before/after improvement measurement
- Actionable recommendations with realistic timelines

### **Business Validation**
- Customer recognizes implementation value 
- Weekly usage pattern intention expressed
- Payment willingness for continued access

## Troubleshooting

### **If Customer Data Format Issues**
```bash
# Check supported formats
arc-eval --help-input

# Use pilot data as backup
arc-eval --domain [domain] --input examples/pilot-data/[domain]_baseline.json --agent-judge
```

### **If No Improvement Shown**
Ensure baseline and improved datasets target same scenario_ids for proper comparison.

### **If Technical Errors**
```bash
# Verify API key
echo $ANTHROPIC_API_KEY

# Check file format
cat examples/pilot-data/finance_baseline.json | jq .
```