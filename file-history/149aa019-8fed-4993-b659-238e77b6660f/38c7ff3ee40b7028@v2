# CC Indicator Refactoring Plan (Option C: Simplified Modular)

**Version**: 1.0.0
**Status**: IN PROGRESS
**Created**: 2025-10-14
**Last Updated**: 2025-10-14 00:21 UTC

## Objectives

1. Extract pattern detection logic into reusable modules
2. Enable addition of new patterns (inside bar, outside bar, etc.) with minimal code changes
3. Maintain 100% backward compatibility with existing behavior
4. Support CLI compilation workflow (local includes only)

## Architecture: Simplified Modular (Functional Approach)

### Rationale for Functional vs OOP

- MQL5 classes have runtime overhead (virtual functions, vtables)
- Functional approach compiles faster and executes faster
- Simpler debugging and testing
- Matches MQL5 community idioms
- Easier CLI compilation (no complex inheritance chains)

### File Structure

```
MQL5/Indicators/Custom/
├── cc.mq5                      # Orchestrator (main indicator)
├── PatternHelpers.mqh          # Common utilities (DONE - Step 1)
├── BodySizePatterns.mqh        # Expansion/contraction detectors
└── CandlePatterns.mqh          # Inside bar, outside bar, etc.
```

### Module Responsibilities

**cc.mq5** (Orchestrator):
- Buffer management (13 buffers)
- OnInit() - setup and validation
- OnCalculate() - orchestrate pattern detections
- Input parameter definitions
- Visualization configuration

**PatternHelpers.mqh** (DONE):
- `CheckSameDirection()` - validate bar direction consistency
- `CheckConsecutiveContractions()` - body size decreasing
- `CheckConsecutiveExpansions()` - body size increasing

**BodySizePatterns.mqh** (NEW):
- `SetContractionSignal()` - mark contraction pattern bars
- `SetExpansionSignal()` - mark expansion pattern bars with dots
- Requires access to: buffers, input params (via cc.mq5 scope)

**CandlePatterns.mqh** (NEW):
- `CheckInsideBar()` - detect inside bar pattern
- `SetInsideBarSignal()` - mark inside bar pattern
- Future: `CheckOutsideBar()`, `CheckEngulfing()`, etc.

## Service Level Objectives

### Availability: 100%
- All files accessible at expected paths
- CLI compilation succeeds with 0 errors
- Compiled .ex5 loads on MT5 chart without crashes

### Correctness: 100%
- Refactored indicator produces identical signals to v1.10 baseline
- Inside bar pattern detects correctly per definition
- No buffer overflows or array index errors

### Observability: 100%
- Compilation logs show clear error messages if failures occur
- Git diffs show clean separation of concerns
- Version numbers track in cc.mq5 header

### Maintainability: High
- New pattern addition requires ≤50 lines of code
- Module boundaries clear (function signatures documented)
- No duplicate logic across files

## Implementation Phases

### Phase 1: Extract Body Size Pattern Functions ✅ COMPLETE

**Status**: COMPLETE (2025-10-14 00:27)

**Completed**:
- ✅ PatternHelpers.mqh extracted (48 lines)
- ✅ BodySizePatterns.mqh extracted (88 lines)
- ✅ cc.mq5 reduced to 299 lines (from 417 original)
- ✅ Includes placed after global declarations (critical discovery)
- ✅ Compilation: 0 errors, 0 warnings, 895ms

**File Structure**:
- cc.mq5: 299 lines
- PatternHelpers.mqh: 48 lines
- BodySizePatterns.mqh: 88 lines
- Total: 435 lines (modular)

### Phase 2: Add Inside Bar Pattern

**Steps**:
1. Create CandlePatterns.mqh with `CheckInsideBar()`
2. Create `SetInsideBarSignal()` function
3. Allocate 2 new buffers in cc.mq5 (inside bar bullish/bearish dots)
4. Add inside bar detection loop in OnCalculate()
5. Add input parameter `InpShowInsideBars = true`

**Definition - Inside Bar**:
- Current bar high ≤ previous bar high
- Current bar low ≥ previous bar low
- Direction: bullish if close > open, bearish otherwise

**Compilation Checkpoint**: cc.mq5 compiles with 0 errors

### Phase 3: Validation

**Tests**:
1. Load refactored indicator on EURUSD M1 chart
2. Compare signals with cc.mq5.backup side-by-side
3. Verify expansion dots appear at identical bars
4. Verify contraction colors match
5. Verify inside bar dots appear at correct bars

**Acceptance Criteria**:
- Visual inspection: 100% signal match for expansion/contraction
- Inside bar signals appear (new functionality)
- No errors in Experts log

## Critical Constraints

### CLI Compilation Limitation (Discovered 2025-10-14 00:15)

**Issue**: `#include <Path/File.mqh>` fails in CLI compilation
**Workaround**: Use local includes `#include "File.mqh"` in same directory
**Impact**: All .mqh files must be in `MQL5/Indicators/Custom/` directory

### MQL5 Include Processing Order (Discovered 2025-10-14 00:26)

**Issue**: `#include` statements process inline - functions cannot access variables declared later
**Requirement**: All `#include` directives must appear AFTER global variable/constant declarations
**Correct Order**:
1. `#property` directives
2. `#define` constants
3. `input` parameters
4. Global buffer/variable declarations
5. `#include` statements ← MUST BE HERE
6. `OnInit()` / `OnCalculate()` functions

**Failure Mode**: 4 compilation errors if includes appear before buffer declarations

### No Fallback Error Handling

**Requirement**: Raise and propagate all errors
**Implementation**:
- No default values on parameter validation failures
- No silent error suppression
- OnInit() returns INIT_FAILED if validation fails
- OnCalculate() returns 0 if critical errors occur

### Buffer Management

**Current**: 13 buffers allocated
**After Inside Bar**: 15 buffers (2 new for inside bar signals)
**Constraint**: MQL5 limit is 512 buffers per indicator

## Rollback Strategy

**Files**:
- cc.mq5.backup - original working version
- Restore command: `cp cc.mq5.backup cc.mq5`

**Validation**:
- Backup compiles: ✅ Verified (0 errors, 18KB .ex5)
- Compilation time: ~900ms

## Version History

- **1.10** - Original monolithic implementation (417 lines)
- **1.11** - PatternHelpers.mqh extracted (378 lines cc.mq5 + 50 lines helpers)
- **1.20** (Target) - BodySizePatterns.mqh + CandlePatterns.mqh modular architecture

## References

- Original indicator: `/MQL5/Indicators/Custom/cc.mq5.backup `
- MQL5 CLI compilation guide: `/Users/terryli/eon/mql5-crossover/docs/guides/MQL5_CLI_COMPILATION_SUCCESS.md `
- Project CLAUDE.md: `/Users/terryli/eon/mql5-crossover/CLAUDE.md `

## Notes

- Inside bar pattern is first of many planned candle patterns
- Future patterns: outside bar, engulfing, harami, piercing line
- Consider adding pattern strength scoring in v1.30
