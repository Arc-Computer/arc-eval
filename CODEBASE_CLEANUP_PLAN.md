# ARC-Eval Codebase Cleanup Plan

## 🎯 Context & Objective

**Company**: ARC-Eval - Agentic Workflow Reliability Platform

**Current State**: The codebase has accumulated legacy features, experimental code, and complexity that doesn't align with our focused V1 MVP vision.

**Target State**: A clean, enterprise-ready codebase that implements exactly three workflows:
1. **Debug** - Why did it fail? + What will fail? (with test harness)
2. **Compliance** - Does it meet requirements? (378 domain scenarios)
3. **Improve** - How to fix it? (with data flywheel)

**Core Principle**: Simplicity and focus. Remove anything that doesn't directly support these three workflows.

  ✅ Removing Legacy Commands Will NOT Break the Product

  Here's Why:

  1. Smart Routing in main() (lines 820-844)
  The entry point intelligently routes between new and legacy commands:
  if len(sys.argv) > 1 and sys.argv[1] in ['debug', 'compliance', 'improve', '--version', 'legacy']:
      return cli()  # New unified commands
  elif len(sys.argv) == 1:
      return cli()  # Interactive mode
  else:
      # Shows deprecation warning but STILL WORKS
      return legacy_main()
  2. New Commands Map to Same Handlers
    - debug command → ReliabilityCommandHandler (same as --debug-agent, --unified-debug)
    - compliance command → ComplianceCommandHandler (same as --domain)
    - improve command → WorkflowCommandHandler (same as --improvement-plan)
  3. Smart Defaults Fill the Gaps
  The new commands have intelligent defaults that replicate legacy behavior:
    - compliance automatically enables --agent-judge
    - compliance auto-exports PDF unless --no-export
    - debug enables unified debugging features by default

  Critical Analysis of Dependencies:

  1. Command Handlers are Shared
  from agent_eval.commands import (
      ReliabilityCommandHandler,
      ComplianceCommandHandler,
      WorkflowCommandHandler,
      BenchmarkCommandHandler
  )
  1. These handlers support BOTH new and legacy commands.
  2. Parameters are Passed Through
  New commands pass parameters to the same handlers:
  handler.execute(
      input_file=input_file,
      domain=domain,
      unified_debug=True,  # Smart defaults
      workflow_reliability=True,
      ...
  )
  3. No Hard Dependencies on Legacy Flags
  The handlers accept parameters, not specific flag names. The flags are just CLI sugar.

  ⚠️ One Important Consideration

  The --quick-start functionality is currently only in legacy. You should:
  1. Add --quick-start to the compliance command OR
  2. Keep just this one flag in the simplified version

  Recommended Approach:

  1. Remove legacy_main() function entirely (lines 555-815)
  2. Remove legacy routing in main() (lines 835-844)
  3. Keep the three unified commands with their current implementation
  4. Add --quick-start to compliance command for demo purposes

  Proof the New Commands Cover Everything:

  Testing Strategy:

  Before removing legacy commands:
  1. Run all tests in the testing strategy with new commands
  2. Verify identical output between legacy and new commands
  3. Check that all command handlers still work correctly

  Bottom Line: The product is already architected to support this transition. The new commands are just a cleaner interface to the same underlying functionality. Removing legacy commands will simplify the 
  codebase without breaking any features.

---

## 🧹 Cleanup Tasks

### 1. Remove Legacy CLI Complexity 🚨 [PRIORITY 1]

**Current Problem**: The CLI has 40+ legacy flags that complicate the codebase and confuse users.

**Files to Modify**:
- `agent_eval/cli.py`

**Actions**:
1. Remove the entire `legacy_main()` function (lines ~555-815)
2. Remove the `legacy` command (lines ~500-510)
3. Remove all legacy option flags (40+ @click.option decorators)
4. Keep ONLY the new unified commands: debug, compliance, improve
5. Update help text to reflect simplified interface
6. Remove backward compatibility warnings

**Keep**: 
- The `@click.group()` structure
- The three workflow commands
- Smart defaults and workflow tracking

---

### 2. Remove Test/Demo Data from Production 🚨 [PRIORITY 2]

**Current Problem**: Test data and demo scripts shouldn't ship with production code.

**Directories to Remove**:
- `/retraining_data/` - Contains test improvement curriculum
- `/scripts/` - Contains demo scripts

**Actions**:
1. Delete `/retraining_data/` directory entirely
2. Delete `/scripts/` directory entirely
3. Update `.gitignore` to exclude these if regenerated
4. Ensure no code references these directories

---

### 3. Clean Up Experimental Features [PRIORITY 4]

**Current Problem**: Experimental features add complexity without supporting core workflows.

**Files to Remove**:
- `agent_eval/evaluation/objective_analyzer.py` - Experimental framework comparison
- `agent_eval/analysis/judge_comparison.py` - A/B testing functionality

**Actions**:
1. Delete both files
2. Remove any imports of these modules
3. Remove `--compare-judges` flag from CLI if it exists
4. Remove `/config/judge_comparison_templates.yaml`

---

### 4. Consolidate UI Components [PRIORITY 5]

**Current Problem**: Multiple UI files with overlapping functionality.

**Files to Consolidate**:
- `agent_eval/ui/unified_output.py`
- `agent_eval/ui/result_renderer.py` (KEEP as base)
- `agent_eval/ui/streaming_evaluator.py`
- `agent_eval/ui/interactive_menu.py`

**Actions**:
1. Merge all UI functionality into `result_renderer.py`
2. Delete the other three files
3. Update all imports to use the consolidated module
4. Ensure consistent visual style matching screenshots

---

### 5. Remove Benchmark Integration [OPTIONAL - Get Approval First]

**Current Problem**: Generic benchmarks (MMLU, HumanEval, GSM8K) may not align with enterprise compliance focus.

**Directory to Remove**:
- `/agent_eval/benchmarks/` - Entire directory

**Actions** (IF APPROVED):
1. Delete `/agent_eval/benchmarks/` directory
2. Remove benchmark command from CLI
3. Remove `--benchmark` flag and related code
4. Update documentation to remove benchmark references

**Note**: Discuss with product owner before removing - may be useful for demos.

---

### 6. Clean Up Example Data [PRIORITY 3]

**Current Problem**: Multiple example directories with redundant content.

**Directories to Consolidate**:
- `/examples/demo-data/`
- `/examples/sample-data/`
- `/examples/complete-datasets/`
- `/examples/enhanced-traces/`

**Actions**:
1. Create `/examples/quickstart/` with one example per domain:
   - `finance_example.json`
   - `security_example.json`
   - `ml_example.json`
2. Move best examples from existing directories
3. Delete the four old directories
4. Update all documentation references

---

### 7. Remove Development Artifacts [PRIORITY 3]

**Files to Remove**:
- `TEST_HARNESS_SIMPLIFIED_PLAN.md` - Implementation plan
- `CODEBASE_CLEANUP_PLAN.md` - This file (after cleanup)
- Any files ending in `_old`, `_backup`, `_test`

**Actions**:
1. Delete implementation planning documents
2. Search for and remove all TODO/FIXME comments
3. Remove any commented-out code blocks
4. Clean up any print() debug statements

---

### 8. Simplify Command Structure [LOWER PRIORITY - After Test Harness]

**Current Problem**: Separate command files for each feature.

**Files to Consolidate**:
- `agent_eval/commands/benchmark.py` (delete if removing benchmarks)
- `agent_eval/commands/compliance.py` (merge into single handler)
- `agent_eval/commands/reliability.py` (merge into single handler)
- `agent_eval/commands/workflow.py` (merge into single handler)

**Actions**:
1. Create unified command handlers for debug/compliance/improve
2. Remove feature-specific command files
3. Simplify command routing logic

---

### 9. Clean Up Constants [PRIORITY 5]

**File to Review**:
- `agent_eval/core/constants.py`

**Actions**:
1. Review all constants for hardcoded values
2. Move configurable values to environment variables
3. Remove unused constants
4. Document remaining constants clearly

---

### 10. Security Review [PRIORITY 1]

**Actions**:
1. Search entire codebase for:
   - API keys or tokens
   - Hardcoded URLs with credentials
   - Debug logging that might expose data
   - File paths with user information
2. Review all config files in `/config/`
3. Ensure `.env.example` exists with safe defaults
4. Add `.env` to `.gitignore` if not already

---

## 💡 Keep These (Core Features)

These align with the three workflows and should NOT be removed:

- ✅ `/agent_eval/domains/` - Three domain YAML files (finance/security/ml)
- ✅ `/agent_eval/analysis/self_improvement.py` - Self-improvement engine
- ✅ `/agent_eval/evaluation/judges/` - Agent-as-Judge evaluation
- ✅ `/agent_eval/exporters/` - PDF/CSV/JSON exporters
- ✅ `/agent_eval/core/engine.py` - Core evaluation engine
- ✅ `/agent_eval/core/parser_registry.py` - Framework detection
- ✅ `/agent_eval/evaluation/reliability_validator.py` - For test harness

---

## 📋 Execution Order

1. **First**: Security review (Priority 1)
2. **Second**: CLI simplification (Priority 1) 
3. **Third**: Remove test data (Priority 2)
4. **Fourth**: Consolidate examples (Priority 3)
5. **Fifth**: Remove dev artifacts (Priority 3)
6. **Sixth**: Remove experimental features (Priority 4)
7. **Last**: UI consolidation and constants (Priority 5)

---

## ✅ Success Criteria

After cleanup, the codebase should:
1. Have ONLY code supporting debug/compliance/improve workflows
2. Have zero legacy CLI flags
3. Have no test data or demo scripts in production
4. Have consolidated, clean example files
5. Pass security review with no exposed credentials
6. Be ready for enterprise deployment

---

## 🧪 Testing Strategy

### Core User Journey Testing

After EACH cleanup task, run these tests to ensure the three workflows still function correctly:

#### 1. Debug Workflow Testing
```bash
# Test reactive debugging (existing functionality)
arc-eval debug --input examples/sample-data/finance_baseline.json
# Expected: Shows why agent failed with actionable recommendations

# Test with verbose mode
arc-eval debug --input examples/sample-data/security_baseline.json --verbose
# Expected: Detailed failure analysis with framework detection
```

#### 2. Compliance Workflow Testing
```bash
# Test each domain evaluation
arc-eval compliance --domain finance --input examples/sample-data/finance_baseline.json
# Expected: Shows compliance score, generates evaluation file

arc-eval compliance --domain security --input examples/sample-data/security_baseline.json
# Expected: Security compliance evaluation with framework coverage

arc-eval compliance --domain ml --input examples/sample-data/ml_baseline.json
# Expected: ML bias/fairness evaluation

# Test PDF export (critical for enterprise)
arc-eval compliance --domain finance --input examples/sample-data/finance_baseline.json --export pdf
# Expected: Generates PDF compliance report in current directory

# Test quick-start mode
arc-eval compliance --domain finance --quick-start
# Expected: Runs with built-in sample data
```

#### 3. Improve Workflow Testing
```bash
# Test improvement plan generation
arc-eval improve --from-evaluation latest
# Expected: Generates actionable improvement plan

# Test comparison functionality
arc-eval improve --baseline examples/sample-data/finance_baseline.json --current examples/sample-data/finance_improved.json
# Expected: Shows before/after comparison with improvement metrics
```

### Integration Testing

#### Test Complete User Journey
```bash
# Step 1: Debug a failure
arc-eval debug --input examples/sample-data/finance_baseline.json

# Step 2: Run compliance check
arc-eval compliance --domain finance --input examples/sample-data/finance_baseline.json

# Step 3: Generate improvement plan
arc-eval improve --from-evaluation latest

# Step 4: Verify improvements
arc-eval compliance --domain finance --input examples/sample-data/finance_improved.json
# Expected: Higher compliance score than baseline
```

### Critical Feature Testing

#### 1. Framework Detection
```bash
# Test with different framework outputs
arc-eval debug --input examples/workflow-reliability/langchain_workflow_trace.json
# Expected: Detects LangChain framework

arc-eval debug --input examples/workflow-reliability/crewai_performance_trace.json
# Expected: Detects CrewAI framework
```

#### 2. Agent-as-Judge (API Key is set in .env)
```bash
arc-eval compliance --domain finance --input examples/sample-data/finance_baseline.json --agent-judge
# Expected: Uses Claude for evaluation (check for judge results in output)
```

#### 3. Export Functionality
```bash
# Test all export formats
arc-eval compliance --domain security --input examples/sample-data/security_baseline.json --export pdf
arc-eval compliance --domain security --input examples/sample-data/security_baseline.json --export csv
arc-eval compliance --domain security --input examples/sample-data/security_baseline.json --export json
# Expected: Generates files in each format
```

### Performance Testing

```bash
# Test with timing enabled
arc-eval compliance --domain finance --input examples/sample-data/finance_baseline.json --timing
# Expected: Shows execution time metrics

# Test with performance tracking
arc-eval compliance --domain ml --input examples/sample-data/ml_baseline.json --performance
# Expected: Shows detailed performance metrics
```

### Error Handling Testing

```bash
# Test with invalid input
arc-eval debug --input nonexistent.json
# Expected: Clear error message, not a stack trace

# Test with wrong domain
arc-eval compliance --domain invalid --input examples/sample-data/finance_baseline.json
# Expected: Shows available domains (finance, security, ml)

# Test with malformed JSON
echo '{invalid json}' > test_invalid.json
arc-eval debug --input test_invalid.json
# Expected: Clear JSON parsing error
rm test_invalid.json
```

### Regression Test Checklist

After ALL cleanup is complete, verify:

- [ ] All three workflows (debug/compliance/improve) work with sample data
- [ ] PDF export generates valid compliance reports
- [ ] Framework detection works for LangChain/CrewAI/OpenAI
- [ ] Error messages are user-friendly (no stack traces)
- [ ] Help text is accurate (`arc-eval --help`, `arc-eval debug --help`, etc.)
- [ ] Quick-start mode works for all domains
- [ ] File outputs are created in correct locations
- [ ] No hardcoded paths or credentials in code
- [ ] Performance is acceptable (<5 seconds for basic operations)

### Unit Test Suite

```bash
# Run existing unit tests
pytest tests/

# Run with coverage
pytest --cov=agent_eval tests/

# Run specific test files that cover core functionality
pytest tests/test_unified_workflows.py
pytest tests/evaluation/test_reliability_validator.py
pytest tests/evaluation/test_performance_tracker.py
```

---

## 🚨 Important Notes

1. **Create a backup branch** before starting cleanup
2. **Run the Core User Journey Testing** after each major change
3. **Update imports** when deleting files
4. **Check for broken references** after deletions
5. **Update documentation** to match changes
6. **Run full regression testing** before marking complete

The goal is a **lean, focused, enterprise-ready** codebase that clearly implements the three-workflow vision without distractions while maintaining 100% functionality.