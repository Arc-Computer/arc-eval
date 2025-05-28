# Phase 1: Template-Based Domain Generation

## Overview
Rapid domain expansion capability to support pilot requests and validate scalability assumptions without months of manual scenario writing.

## Strategic Context
- **Current pilots need coverage beyond Finance/Security/ML**
- **Key assumption to validate**: "Enterprises pay for deep domain scenarios vs generic evals"
- **Business need**: Never say "we don't cover that domain" to pilot requests
- **Technical goal**: Prove generated scenarios perform as well as hand-crafted ones

## Implementation Plan (4 Weeks)

### Week 1-2: Template Engine Foundation
```python
# New module: agent_eval/generators/template_generator.py

class TemplateGenerator:
    def generate_scenarios_from_template(
        base_scenario: EvaluationScenario,
        domain_context: str,
        compliance_frameworks: List[str],
        variation_count: int = 10
    ) -> List[EvaluationScenario]:
        """
        Generate domain-specific scenarios from existing templates
        
        Args:
            base_scenario: Template scenario from existing domain
            domain_context: Target domain (e.g., "healthcare", "legal")
            compliance_frameworks: Relevant frameworks (e.g., ["HIPAA", "FDA"])
            variation_count: Number of variations to generate
            
        Returns:
            List of generated scenarios with domain-specific context
        """
```

### Week 3-4: Target Domain Expansion
**Priority domains for pilot support:**

1. **Healthcare**: 
   - Base templates from Finance KYC/privacy scenarios
   - Compliance: HIPAA, FDA, HITECH, 21 CFR Part 11
   - Use cases: Patient data handling, clinical trial compliance

2. **Legal**:
   - Base templates from Security confidentiality scenarios  
   - Compliance: Attorney-client privilege, FRCP, state bar rules
   - Use cases: Discovery review, privilege screening

3. **Government**:
   - Base templates from Security + Finance scenarios
   - Compliance: FISMA, FedRAMP, NIST 800-53, ATO processes
   - Use cases: Clearance verification, classified data handling

4. **Data Governance** (for Snowflake):
   - Base templates from ML governance scenarios
   - Compliance: GDPR, CCPA, SOC 2, data lineage requirements
   - Use cases: Data pipeline compliance, PII detection

## Technical Architecture

### Template Variation Engine
```python
# Leverage existing infrastructure:
- EvaluationScenario dataclass (proven structure)
- Domain judge prompt templates (compliance expertise)
- YAML loading system (EvaluationPack.from_dict)

# Generation process:
1. Select base scenario template from existing domains
2. Apply domain-specific context transformation
3. Map compliance frameworks using judge knowledge
4. Generate failure indicators based on domain risks
5. Create remediation steps using regulatory guidance
6. Human review (20% of generated scenarios)
```

### Quality Validation Pipeline
```python
# Validation criteria:
- Compliance framework accuracy (regulatory mapping)
- Scenario realism (domain expert review)
- Failure indicator relevance (actual risk patterns)
- Judge evaluation consistency (confidence scores)

# Success metrics:
- Generated scenarios achieve >85% confidence scores vs hand-crafted
- Domain experts approve >90% of generated scenarios after review
- Pilot customers can't distinguish generated from manual scenarios
```

## CLI Integration
```bash
# New command for rapid domain generation:
arc-eval --generate-domain healthcare --base-domain finance --frameworks "HIPAA,FDA" --scenarios 50

# Generated domain usage (seamless):
arc-eval --domain healthcare --input outputs.json --agent-judge
```

## Pilot Support Strategy

### Immediate Capabilities
- **48-hour domain turnaround** for any pilot request
- **50+ scenarios** generated from proven templates
- **Compliance framework coverage** for any regulated industry
- **Quality assurance** with 20% human expert review

### Validation Approach
1. **A/B test** generated vs manual scenarios with pilot customers
2. **Performance comparison** (confidence scores, failure detection rates)
3. **Customer satisfaction** (blind evaluation of scenario quality)
4. **Conversion impact** (do generated domains drive same adoption?)

## Success Criteria

### Technical Validation
- [ ] Generate 50 healthcare scenarios from finance templates
- [ ] Achieve >85% confidence score parity with manual scenarios  
- [ ] Pass domain expert review (>90% approval rate)
- [ ] Seamless integration with existing evaluation pipeline

### Business Validation  
- [ ] Support 100% of pilot domain requests within 48 hours
- [ ] Pilot customers achieve same results with generated domains
- [ ] Zero customer complaints about generated scenario quality
- [ ] At least 2 pilots request additional generated domains

### Platform Validation
- [ ] Prove template-based generation scales to any domain
- [ ] Validate assumption: "Domain-specific scenarios drive enterprise adoption"
- [ ] Establish foundation for Phase 2 (LLM-powered generation)
- [ ] Create competitive barrier: rapid domain expansion capability

## Risk Mitigation

### Quality Risks
- **Mitigation**: 20% human review, A/B testing vs manual scenarios
- **Fallback**: Manual scenario creation for critical pilot domains

### Technical Risks  
- **Mitigation**: Build on proven infrastructure (existing judges, YAML system)
- **Fallback**: Start with simple parameter substitution, increase sophistication

### Business Risks
- **Mitigation**: Validate with pilot customers before expanding generation
- **Fallback**: Return to manual scenario creation if quality concerns arise

## Path to Phase 2 & 3

### Phase 2 Trigger: LLM-Powered Generation
- **Condition**: Phase 1 achieves >90% quality parity with manual scenarios
- **Timeline**: Post-pilot validation (8-12 weeks)
- **Capability**: 95% automation, generate entirely new scenarios

### Phase 3 Trigger: Customer-Driven Generation  
- **Condition**: Production deployments provide failure pattern data
- **Timeline**: 6+ months (requires pilot → production conversions)
- **Capability**: 100% automation based on real agent failures

## Expected Outcomes

### Immediate (4 weeks)
- Support any pilot domain request within 48 hours
- Validate scalability assumption with generated scenarios
- Create competitive differentiation: rapid domain expansion

### Medium-term (3 months)
- Prove template generation drives same enterprise adoption
- Establish foundation for fully automated scenario generation
- Build pilot pipeline: never limited by domain coverage

### Long-term (6+ months)
- Platform advantage: dynamic, customer-driven evaluation
- Defensible moat: dataset generation scales with usage
- Category leadership: only platform that evolves with customer needs