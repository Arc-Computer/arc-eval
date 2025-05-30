# Comprehensive QA Test Plan for ARC-Eval CLI

## Context
You are QA testing ARC-Eval, an enterprise-grade CLI tool for AI agent evaluation and improvement. Recent changes have implemented:
1. Adaptive post-evaluation menus across all workflows
2. Unified `analyze` command for workflow chaining
3. Scenario contribution and pattern tracking features
4. Consistent UX with clear next steps after every workflow

## Critical Success Criteria
- **100% Accuracy**: All evaluations must produce correct, consistent results
- **Perfect Functionality**: No crashes, hangs, or undefined behavior
- **Perfect User Experience**: Clear guidance, natural flow, no dead ends

## Test Execution Plan

### 1. Installation and Setup Tests
```bash
# Test 1.1: Fresh installation
pip install -e .
echo $?  # Must return 0

# Test 1.2: Verify all commands are available
arc-eval --help
arc-eval debug --help
arc-eval compliance --help
arc-eval improve --help
arc-eval analyze --help  # NEW unified command

# Test 1.3: Test with missing API keys
unset ANTHROPIC_API_KEY
arc-eval compliance --domain finance --quick-start
# Should work in quick-start mode without API key

# Test 1.4: Test with API key
export ANTHROPIC_API_KEY="test-key"
arc-eval compliance --domain finance --quick-start --agent-judge
# Should fail gracefully with invalid API key message
```

### 2. Workflow Tests

#### 2.1 Debug Workflow Tests
```bash
# Test 2.1.1: Basic debug with various input formats
echo '{"output": "test", "error": "timeout"}' > test_debug.json
arc-eval debug --input test_debug.json

# Test 2.1.2: Debug with framework detection
echo '{"intermediate_steps": [], "output": "test"}' > langchain_test.json
arc-eval debug --input langchain_test.json
# Should auto-detect LangChain

# Test 2.1.3: Test post-evaluation menu appears
arc-eval debug --input test_debug.json
# After analysis, should show menu with 4 options:
# [1] Run compliance check on these outputs (Recommended)
# [2] Ask questions about the failures
# [3] Export debug report
# [4] Submit failure pattern for scenario generation
```

#### 2.2 Compliance Workflow Tests
```bash
# Test 2.2.1: Quick-start compliance for each domain
for domain in finance security ml; do
    arc-eval compliance --domain $domain --quick-start --no-export
    # Should complete successfully and show post-evaluation menu
done

# Test 2.2.2: Compliance with real input file
echo '[{"output": "Transaction approved", "metadata": {"scenario_id": "fin_001"}}]' > test_compliance.json
arc-eval compliance --domain finance --input test_compliance.json --no-export

# Test 2.2.3: Test menu recommendations based on pass rate
# Create failing input
echo '[{"output": "FAILED", "metadata": {"scenario_id": "fin_001"}}]' > test_fail.json
arc-eval compliance --domain finance --input test_fail.json --quick-start
# Menu option [2] should show "(Recommended for <90% pass)"
```

#### 2.3 Improve Workflow Tests
```bash
# Test 2.3.1: Generate improvement plan from evaluation
arc-eval compliance --domain finance --quick-start --no-export
# Note the evaluation file created
arc-eval improve --from-evaluation finance_evaluation_*.json

# Test 2.3.2: Test post-improvement menu
# Should show:
# [1] Re-run evaluation to measure improvement (Recommended)
# [2] Schedule automated re-evaluation (Coming Soon)
# [3] Export plan as actionable tasks
# [4] Track this pattern for future scenarios
```

#### 2.4 Unified Analyze Workflow Tests
```bash
# Test 2.4.1: Full analyze workflow
echo '[{"output": "Test agent output", "tool_calls": []}]' > test_analyze.json
arc-eval analyze --input test_analyze.json --domain finance --quick

# Should run through:
# Step 1: Debug Analysis
# Step 2: Compliance Evaluation  
# Step 3: Analysis Complete with unified menu

# Test 2.4.2: Analyze with verbose mode
arc-eval analyze --input test_analyze.json --domain security --verbose
# Should show detailed output at each step
```

### 3. Menu Navigation Tests

#### 3.1 Interactive Mode Tests
```bash
# Test 3.1.1: Test each menu option (manual interaction required)
# For each workflow, test selecting options 1-4
# Verify each option provides appropriate response/action

# Test 3.1.2: Test menu continuation flow
# Select option, complete action, press Enter to return to menu
# Verify menu re-displays correctly

# Test 3.1.3: Test quit functionality
# Type 'q' when prompted to quit
# Verify clean exit
```

#### 3.2 Export Functionality Tests
```bash
# Test 3.2.1: Test all export formats
arc-eval compliance --domain finance --quick-start
# When menu appears, select option 3
# Test: pdf, csv, json, all

# Test 3.2.2: Verify export files are created
ls evaluation_results/
# Should see exported files

# Test 3.2.3: Test improvement task export
arc-eval improve --from-evaluation finance_evaluation_*.json
# Select option 3 to export tasks
ls improvement_tasks/
# Should see markdown task file
```

### 4. Error Handling Tests

#### 4.1 Invalid Input Tests
```bash
# Test 4.1.1: Missing required parameters
arc-eval compliance
# Should show helpful error message

# Test 4.1.2: Invalid domain
arc-eval compliance --domain invalid --quick-start
# Should show valid domain choices

# Test 4.1.3: Non-existent input file
arc-eval debug --input nonexistent.json
# Should show helpful file not found message

# Test 4.1.4: Malformed JSON
echo '{invalid json}' > bad.json
arc-eval debug --input bad.json
# Should show JSON parsing error
```

#### 4.2 Edge Case Tests
```bash
# Test 4.2.1: Empty input file
echo '[]' > empty.json
arc-eval debug --input empty.json
# Should handle gracefully

# Test 4.2.2: Very large input file
# Create file with 1000+ outputs
python -c "import json; json.dump([{'output': f'test{i}'} for i in range(1000)], open('large.json', 'w'))"
arc-eval compliance --domain ml --input large.json --quick-start
# Should handle without memory issues

# Test 4.2.3: Interrupt handling
arc-eval compliance --domain finance --quick-start
# Press Ctrl+C during menu
# Should exit cleanly
```

### 5. Integration Tests

#### 5.1 Workflow Chaining Tests
```bash
# Test 5.1.1: Complete improvement cycle
# Step 1: Initial evaluation
arc-eval compliance --domain finance --input test_compliance.json --agent-judge

# Step 2: Generate improvement plan
arc-eval improve --from-evaluation finance_evaluation_*.json

# Step 3: Re-evaluate (simulate improved outputs)
echo '[{"output": "Transaction approved with compliance checks", "metadata": {"scenario_id": "fin_001"}}]' > improved.json
arc-eval compliance --domain finance --input improved.json --baseline finance_evaluation_*.json

# Verify improvement metrics are shown
```

#### 5.2 Cross-Workflow Menu Tests
```bash
# Test 5.2.1: Debug → Compliance flow
arc-eval debug --input test_debug.json
# Select option 1 (Run compliance check)
# Verify instructions are clear and correct

# Test 5.2.2: Compliance → Improve flow  
arc-eval compliance --domain security --quick-start
# Select option 2 (Generate improvement plan)
# Verify appropriate guidance is shown
```

### 6. Performance Tests

#### 6.1 Response Time Tests
```bash
# Test 6.1.1: Measure quick-start performance
time arc-eval compliance --domain finance --quick-start --no-export --no-interaction

# Test 6.1.2: Measure analyze command performance
time arc-eval analyze --input test_analyze.json --domain ml --quick
# Should complete in reasonable time (<5 seconds for quick mode)
```

#### 6.2 Resource Usage Tests
```bash
# Test 6.2.1: Memory usage monitoring
# Run with memory profiler if available
# python -m memory_profiler arc-eval compliance --domain finance --quick-start
```

### 7. User Experience Tests

#### 7.1 Help and Documentation Tests
```bash
# Test 7.1.1: Verify all help messages are clear
arc-eval --help
arc-eval debug --help
arc-eval compliance --help
arc-eval improve --help
arc-eval analyze --help

# Test 7.1.2: Test error message helpfulness
# Intentionally trigger various errors and verify messages guide user to solution
```

#### 7.2 Output Clarity Tests
```bash
# Test 7.2.1: Verify output formatting
# Run each workflow and verify:
# - Colors are used consistently
# - Tables are properly formatted
# - Progress indicators work correctly
# - Emojis display properly
```

### 8. Regression Tests

#### 8.1 Legacy Command Tests
```bash
# Test 8.1.1: Ensure legacy commands still work
arc-eval --domain finance --input test_compliance.json --agent-judge --export pdf

# Test 8.1.2: Test backward compatibility
arc-eval --debug-agent --unified-debug --input test_debug.json
```

### 9. Platform-Specific Tests

#### 9.1 Cross-Platform Tests
```bash
# Test on:
# - macOS (current platform)
# - Linux (Ubuntu 20.04+)
# - Windows (WSL2)
# - Different Python versions (3.9, 3.10, 3.11, 3.12)
```

### 10. Scenario Contribution Tests

#### 10.1 Pattern Submission Tests
```bash
# Test 10.1.1: Test scenario contribution placeholders
arc-eval debug --input test_debug.json
# Select option 4
# Verify placeholder message is informative

# Test 10.1.2: Test results sharing
arc-eval compliance --domain finance --quick-start
# Select option 4
# Verify sharing explanation is clear
```

## Expected Results Summary

1. **No Crashes**: All commands complete without errors
2. **Consistent Menus**: Post-evaluation menu appears after every workflow
3. **Natural Flow**: Users can navigate between workflows seamlessly
4. **Clear Guidance**: Every error has helpful resolution steps
5. **Fast Performance**: Quick-start completes in <2 seconds
6. **Memory Efficient**: Handles large inputs without issues
7. **Platform Agnostic**: Works on all major platforms
8. **Backward Compatible**: Legacy commands still function

## Critical Path Test Sequence

For rapid validation, run this sequence:
```bash
# 1. Install
pip install -e .

# 2. Quick functionality check
arc-eval --help

# 3. Test unified workflow
echo '[{"output": "test"}]' > test.json
arc-eval analyze --input test.json --domain finance --quick

# 4. Test each workflow menu
arc-eval debug --input test.json
arc-eval compliance --domain finance --quick-start
arc-eval improve --from-evaluation finance_evaluation_*.json

# 5. Verify no crashes or hangs
echo "All critical paths tested successfully"
```

## QA Sign-off Checklist

- [ ] All test cases pass without errors
- [ ] Menus appear consistently across workflows
- [ ] Navigation between workflows is intuitive
- [ ] Error messages are helpful and actionable
- [ ] Performance meets requirements (<5s for most operations)
- [ ] No memory leaks or resource issues
- [ ] Platform compatibility verified
- [ ] Documentation matches implementation
- [ ] No regression in existing functionality
- [ ] Enterprise-ready for production deployment

---

**Note**: This test plan should be executed in full before any production release. Any failures must be documented and resolved before deployment.