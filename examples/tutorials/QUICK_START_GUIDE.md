# ARC-Eval Core Loop Quick Start Guide

**Target Duration**: 15 minutes  
**Objective**: Validate complete evaluation → improvement → validation workflow  
**Prerequisites**: `ANTHROPIC_API_KEY` set, agent outputs ready for evaluation

## Session Structure

### **Minute 0-2: Setup & Context**
```bash
# Verify installation and API key
arc-eval --help | grep "improvement-plan"
echo $ANTHROPIC_API_KEY  # Should return your API key

# Quick domain overview
arc-eval --list-domains
```

**Context Setting**: "We'll validate ARC-Eval's complete improvement workflow using your agent data. This demonstrates how to measure and improve agent compliance through actionable improvement cycles."

### **Minute 2-7: Baseline Evaluation**
```bash
# Run baseline evaluation with customer's agent outputs
arc-eval --domain [finance|security|ml] --input customer_outputs.json --agent-judge --dev

# Note the auto-generated evaluation file (example):
# → finance_evaluation_20250527_143022.json
```

**Key Observations to Capture**:
- Total scenarios evaluated
- Pass rate percentage  
- Failed scenarios by priority (Critical/High/Medium/Low)
- Evaluation file name for next steps

### **Minute 7-10: Improvement Plan Generation**
```bash
# Generate improvement plan from baseline
arc-eval --improvement-plan --from finance_evaluation_20250527_143022.json --dev

# Review generated plan
cat improvement_plan_20250527_143022.md
```

**Validation Questions**:
1. Are recommended actions technically actionable?
2. Do timeline estimates seem realistic?
3. Are priority levels aligned with business impact?
4. Would you implement ≥50% of suggested changes?

### **Minute 10-13: Simulation of Improvements**
```bash
# Use provided improved outputs (simulated post-implementation)
arc-eval --domain [finance|security|ml] --input improved_outputs.json --baseline finance_evaluation_20250527_143022.json --dev
```

**Expected Output Validation**:
- Before/after pass rate comparison
- Scenario-level improvement tracking
- Net improvement calculation
- Degraded scenarios identification

### **Minute 13-15: Workflow Discussion**
**Key Questions**:
1. **Frequency**: "How often would you run this evaluation on your agents?"
2. **Implementation**: "What percentage of recommendations would you implement?"
3. **Value**: "Does the improvement measurement provide clear value?"
4. **Integration**: "How would this fit into your existing workflow?"

## Success Criteria Validation

### **Technical Validation**
- [ ] Complete workflow executes in <5 minutes
- [ ] Improvement plan generates actionable recommendations
- [ ] Comparison shows measurable improvement metrics
- [ ] No technical errors or confusing output

### **Usage Validation**  
- [ ] User indicates regular evaluation usage intent
- [ ] User would implement ≥50% of recommendations
- [ ] User sees clear value in before/after measurement
- [ ] User understands integration possibilities

### **Feedback Collection**
- [ ] Specific scenarios where recommendations were unclear
- [ ] Timeline estimates that seem unrealistic
- [ ] Missing functionality that would increase usage
- [ ] Integration points needed for their workflow

## Post-Session Follow-up

### **Week 1 Actions**
1. **Day 1**: Send improvement plan for implementation
2. **Day 3**: Check implementation progress
3. **Day 7**: Schedule re-evaluation session

### **Week 2 Validation**
1. **Day 7**: Run comparison evaluation together
2. **Day 8**: Capture final feedback and workflow integration discussion
3. **Day 9**: Document lessons learned and success metrics

## Domain-Specific Focus Areas

### **Finance Domain**
- Compliance violations (SOX, KYC, AML, PCI-DSS)
- Bias detection in financial decisions
- PII exposure and data protection
- **Use Case Context**: Regulatory audit preparation, compliance validation

### **Security Domain**  
- Prompt injection vulnerabilities
- Data leakage detection
- OWASP LLM Top 10 compliance
- **Use Case Context**: Enterprise deployment readiness, security certification

### **ML Domain**
- Algorithmic bias and fairness
- Model governance and ethics
- Performance reliability
- **Use Case Context**: Production deployment, bias compliance, model validation

## Troubleshooting

### **Common Issues**
```bash
# API key not set
export ANTHROPIC_API_KEY="your-key-here"

# Input format errors
arc-eval --help-input  # Show supported formats

# Domain mismatch
# Ensure input scenarios match domain (finance/security/ml)

# Missing evaluation file
ls *evaluation*.json  # Check auto-generated files
```

### **Backup Demo Data**
If your data has issues, use provided samples:
```bash
# Finance demo
arc-eval --domain finance --input examples/demo-data/finance.json --agent-judge

# Security demo  
arc-eval --domain security --input examples/demo-data/security.json --agent-judge

# ML demo
arc-eval --domain ml --input examples/demo-data/ml.json --agent-judge
```

## Success Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Technical completion | 100% | Workflow executes without errors |
| Recommendation quality | ≥80% actionable | User feedback on implementability |
| Usage intent | Regular use | User indication of ongoing usage |
| Implementation intent | ≥50% of recommendations | User commitment level |
| Value recognition | Clear value seen | User understanding of benefits |
| Session duration | ≤15 minutes | Actual session time |

## Next Steps Template

**For users showing strong engagement**:
```
Next Steps:
1. Implement 2-3 high-priority recommendations from plan
2. Schedule follow-up evaluation for [Day 7]
3. Begin regular evaluation cycle discussion
4. Explore integration into existing workflows
```

**For users showing limited engagement**:
```
Follow-up Actions:
1. Understand specific blockers to implementation
2. Identify missing features or integration needs
3. Assess fit with current evaluation workflow
4. Determine if timing or workflow fit issues exist
```