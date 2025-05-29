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

### Phase 2: Consolidate to Single File (Next Sprint)
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

## Implementation Steps
1. Copy unified CLI functions to cli.py
2. Update main() to handle both modes
3. Test thoroughly
4. Remove cli_unified.py
5. Update imports and entry points