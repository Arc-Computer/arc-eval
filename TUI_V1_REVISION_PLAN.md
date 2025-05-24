# ARC-Eval TUI V1 Revision Plan
*Strategic UX simplification based on user feedback and analysis*

## Context & Vision

**Current State**: Functional V1 TUI with professional appearance but overwhelming first-time experience
**Target State**: Minimal, developer-focused interface that gets users to value in <30 seconds
**Core Philosophy**: Less is more. Let developers experience value immediately without cognitive overhead.

---

## Current V1 Analysis

### What's Working Well ✅
- Professional brand identity with orange accents and dark theme
- Clear value proposition and logical information hierarchy
- Persona-driven approach aligns with customer validation strategy
- Enterprise-ready aesthetic that builds trust with compliance teams
- Strong foundation that validates design direction

### Key Problems to Solve ❌
- **Too much upfront information** - "What is ARC-Eval?" panel unnecessary for intentional users
- **Excessive panels and visual noise** - overwhelming for first-time users
- **Hidden call-to-action** - unclear next steps after reading Quick Start
- **Marketing-focused copy** - developers want to experience value, not read about it
- **Vertical scroll required** - core workflow should fit in single screen

---

## Strategic Revision Approach

### Core Principles
1. **Immediate Value Over Education** - 30-second path to first evaluation
2. **Efficiency Over Features** - keyboard-first, minimal clicks
3. **Trust Through Competence** - tool quality is the proof, not marketing copy
4. **Progressive Disclosure** - reveal advanced features only after initial success

### Developer-Centric Design
- No onboarding tours or explanatory text
- Smart defaults + intuitive interface
- Results speak louder than promises
- Robust error handling with clear next steps

---

## Specific Revision Scope

### Phase 1: Immediate Simplification (High Impact)

#### A. Landing Screen Redesign
**Remove Entirely:**
- "What is ARC-Eval?" panel
- "Quick Start" instructional text
- Use case dropdown (start with smart default)
- All marketing copy and feature explanations

**Keep & Simplify:**
- Simple header with app name only
- Center focus: File selection (drag/drop or browse)
- Domain selector (Finance/Security/ML) 
- Single "Run Evaluation" button (disabled until file selected)

#### B. Interaction Flow Redesign
1. **File selected** → Domain selector becomes active
2. **Domain selected** → Run button becomes active  
3. **Evaluation starts** → Switch to progress view
4. **Results ready** → Switch to results view with export options

#### C. Visual Simplification
- Eliminate excessive panels and borders
- Condense vertical space (no scrolling for core workflow)
- Reduce visual noise by ~70%
- Clean, minimal aesthetic

### Phase 2: Progressive Feature Discovery (Post-First-Run)

#### Smart Reveals Based on Usage
- **After 1st evaluation**: Show keyboard shortcuts tip
- **After 2nd evaluation**: Reveal export format options  
- **After 3rd evaluation**: Show advanced settings/templates

#### Contextual Help Only
- No upfront documentation
- Tooltips on hover/focus only
- F1 for help (but don't advertise initially)
- Error states provide just-in-time guidance

---

## Implementation Priorities

### High Impact, Low Effort (Week 1)
1. Remove 60% of current text content
2. Collapse 3 panels into 1 main interface
3. Hide export buttons until results exist
4. Auto-focus file input on launch
5. Eliminate scrolling for primary workflow

### Medium Impact, Medium Effort (Week 2-3)
1. Implement progressive disclosure states
2. Add contextual tooltips for domain selection
3. Smart defaults based on file type detection
4. Keyboard navigation improvements

### Future Enhancements (Post-Validation)
1. Recent files quick access
2. Saved evaluation templates  
3. Batch evaluation workflows

---

## Success Metrics

### Immediate Validation (Week 1)
- **Time to first evaluation**: <30 seconds (vs current ~2 minutes)
- **User confusion eliminated**: No "what do I do next?" moments
- **Visual complexity reduced**: ~70% less interface elements
- **Zero scrolling**: Core workflow fits in single screen

### Ongoing Validation (Weeks 2-4)
- **Repeat usage increases**: Easier re-runs drive daily adoption
- **Feature discovery**: Happens naturally through usage patterns
- **Export adoption**: Improves when contextually revealed
- **Design partner feedback**: Confirms reduced friction

---

## Technical Context

### Current TUI Status
- **Phase 1 MVP**: Fully implemented and functional
- **All PR feedback**: Addressed and merged
- **Button variants**: Fixed for Textual compatibility
- **CSS issues**: Resolved
- **Resource handling**: Production-ready

### Key Files for Revision
- `agent_eval/tui/screens/onboarding.py` - Primary target for simplification
- `agent_eval/tui/screens/main.py` - Progressive disclosure implementation
- `agent_eval/tui/styles/main.tcss` - Visual density and spacing
- `agent_eval/tui/widgets/` - Smart reveals and contextual help

---

## Validation Strategy

### Core Assumptions Being Tested
1. **Repeatable Pain**: Organizations want repeated evaluation workflows vs one-off audits
2. **Friction Reduction**: Visual interface drives non-developer adoption  
3. **Scenario Value**: Out-of-box scenarios solve 80% of core needs
4. **Reporting Action**: Reports get used in real compliance workflows

### Success Criteria (Phase 1)
- **Daily Usage**: >50% of pilot partners use TUI daily
- **Repeat Runs**: >3 evaluation runs per partner per week  
- **Session Duration**: >5 minutes average (vs 2min CLI)
- **Critical Findings**: >20% partners find critical failures immediately

---

## Final Notes

**Philosophy**: Transform from "feature showcase" to "workflow accelerator"
**Marketing**: Let evaluation result quality be the marketing, not interface copy
**User Journey**: File → Domain → Run → Results → Export (5 steps max)
**Developer Experience**: Keyboard-first, fast iteration, minimal cognitive load

This revision plan transforms the TUI from a comprehensive introduction to ARC-Eval into a focused tool that gets experienced developers to value immediately, with progressive disclosure of advanced features as they build confidence and workflow patterns.