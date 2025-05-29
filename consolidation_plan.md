# CLI Consolidation Plan

## Current State
- `cli.py`: Legacy CLI with 20+ flags (434 lines)
- `cli_unified.py`: New unified CLI with 3 workflows (423 lines)
- Both files import the same command handlers
- Routing logic in cli.py main() function

## Recommended Approach: Gradual Migration

### Phase 1: Keep Both Files (Current - DONE)
- Maintain backward compatibility
- Route through cli.py main() function
- Show deprecation warnings

### Phase 2: Consolidate to Single File (COMPLETED)
1. Move unified CLI logic into cli.py
2. Keep legacy_main() function for old commands
3. Single entry point with intelligent routing
4. Remove cli_unified.py

### Phase 3: Full Migration (Future)
1. Remove legacy command support
2. Clean, maintainable single CLI file
3. Archive old flags in documentation

## Benefits of Consolidation
- Single source of truth
- Easier maintenance
- No import complexity
- Clear migration path

## Implementation Steps (COMPLETED)
1. ✅ Copied unified CLI functions to cli.py
2. ✅ Updated main() to handle both modes intelligently
3. ✅ Tested all workflows (debug, compliance, improve)
4. ✅ Removed cli_unified.py
5. ✅ Updated imports in test files

## Results
- Single cli.py file (787 lines) contains all functionality
- Unified commands work perfectly
- Legacy commands show deprecation warnings
- Interactive mode guides users
- Full backward compatibility maintained