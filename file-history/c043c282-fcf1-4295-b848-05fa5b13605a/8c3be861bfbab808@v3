# MT5 File Locations and Indicator Translation Workflow

**Status**: Production reference (2025-10-13)
**Purpose**: Complete path documentation for MT5 files in CrossOver bottle and workflow for translating MQL5 indicators to Python

## Critical Path Definitions

### CrossOver Bottle Root
```bash
BOTTLE_ROOT="/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5"
```

### MT5 Installation Root
```bash
MT5_ROOT="$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5"
```

### MQL5 Source Tree
```bash
MQL5_ROOT="$MT5_ROOT/MQL5"
```

## Complete MT5 Directory Structure

### Executables
```bash
# MetaEditor (compile MQL5 code)
$MT5_ROOT/MetaEditor64.exe

# Terminal (MT5 platform)
$MT5_ROOT/terminal64.exe

# Tester (strategy testing)
$MT5_ROOT/metatester64.exe
```

### MQL5 Source Directories

#### Indicators
```bash
# Custom indicators (user-created/downloaded)
$MQL5_ROOT/Indicators/Custom/
# Examples: ATR adaptive smoothed Laguerre RSI 2 (extended).mq5

# Standard MT5 examples
$MQL5_ROOT/Indicators/Examples/

# Community/downloaded indicators
$MQL5_ROOT/Indicators/Market/

# Additional custom directory
$MQL5_ROOT/Indicators/Customs/

# Free indicators collection
$MQL5_ROOT/Indicators/Free Indicators/
```

**Full path examples**:
```bash
# Target indicator for translation
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5

# Other custom indicators
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/cci-woodie.mq5
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/BB_Width.mq5
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/Range Expansion Index (REI).mq5
```

#### Scripts
```bash
# User scripts
$MQL5_ROOT/Scripts/

# Example scripts
$MQL5_ROOT/Scripts/Examples/

# Unit tests
$MQL5_ROOT/Scripts/UnitTests/
```

#### Include Files (Libraries)
```bash
# Standard library headers
$MQL5_ROOT/Include/

# Key libraries:
$MQL5_ROOT/Include/MovingAverages.mqh
$MQL5_ROOT/Include/Indicators/Indicators.mqh
$MQL5_ROOT/Include/Indicators/Trend.mqh
$MQL5_ROOT/Include/Indicators/Oscilators.mqh
$MQL5_ROOT/Include/Trade/Trade.mqh
```

#### Expert Advisors (EAs)
```bash
# Expert advisors
$MQL5_ROOT/Experts/
```

#### Files (Data/Output)
```bash
# Script output, user files
$MQL5_ROOT/Files/
```

#### Logs
```bash
# MQL5 script execution logs
$MQL5_ROOT/Logs/
```

### MT5 Configuration and Logs

```bash
# MT5 terminal logs (startup errors, config issues)
$MT5_ROOT/logs/

# MT5 configuration files
$MT5_ROOT/Config/

# User profiles
$MT5_ROOT/Profiles/
```

### Wine Python Environment

```bash
# Wine Python installation
$BOTTLE_ROOT/drive_c/Program Files/Python312/python.exe

# User scripts location (for v3.0.0)
$BOTTLE_ROOT/drive_c/users/crossover/export_aligned.py

# Export output directory
$BOTTLE_ROOT/drive_c/users/crossover/exports/
```

## Indicator Translation Workflow

### Phase 1: Locate Source Indicator

**Objective**: Find the MQL5 indicator file to translate.

**Search Commands**:
```bash
# Search by name
find "$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators" -name "*ATR*Laguerre*" -o -name "*Laguerre*RSI*"

# List all custom indicators
find "$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom" -name "*.mq5"

# Search Include files for dependencies
find "$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Include" -name "*.mqh"
```

**Expected Output**:
```
/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5
```

### Phase 2: Extract Indicator Logic

**Objective**: Analyze MQL5 code structure and dependencies.

**Read Indicator File**:
```bash
# Check encoding
file "/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/Program Files/MetaTrader 5/MQL5/Indicators/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5"

# Convert UTF-16 to UTF-8 if needed
iconv -f UTF-16LE -t UTF-8 "...mq5" > indicator_utf8.mq5

# Or use Python to read
python -c "
with open('...mq5', 'r', encoding='utf-16-le') as f:
    print(f.read())
"
```

**Key Elements to Extract**:
1. **Input parameters**: `input int inpAtrPeriod = 32;`
2. **Buffer definitions**: `double val[], valc[], prices[];`
3. **Calculation functions**: `CalculateTrueRange()`, `CalculateATR()`, `CalculateLaguerreRSI()`
4. **Dependencies**: `#include <MovingAverages.mqh>`
5. **Main calculation loop**: `OnCalculate()` function

### Phase 3: Design Python Equivalent

**Objective**: Map MQL5 concepts to Python/pandas equivalents.

**Mapping Guide**:

| MQL5 Concept | Python Equivalent |
|--------------|-------------------|
| `double array[]` | `pd.Series` or `np.array` |
| `iMA()` / `iMAOnArray()` | `series.rolling().mean()` or `series.ewm()` |
| `iATR()` | Custom TR calculation + EMA |
| `OnInit()` | Function initialization in `__init__()` |
| `OnCalculate()` | Main processing in `calculate()` method |
| `CopyBuffer()` | Data frame column access |
| `ArrayResize()` | `np.resize()` or list operations |

**Example Translation**:
```python
# MQL5: True Range calculation
double tr = MathMax(high, prevClose) - MathMin(low, prevClose);

# Python equivalent:
tr = np.maximum(high, prev_close) - np.minimum(low, prev_close)
```

### Phase 4: Implement Python Module

**Objective**: Create modular Python implementation following `export_aligned.py` pattern.

**Structure**:
```python
# File: indicator_laguerre_rsi.py
import numpy as np
import pandas as pd

def calculate_true_range(high: pd.Series, low: pd.Series, prev_close: pd.Series) -> pd.Series:
    """Calculate True Range"""
    pass

def calculate_atr(tr: pd.Series, period: int = 14) -> pd.Series:
    """Calculate ATR using exponential moving average"""
    pass

def calculate_laguerre_filter(prices: pd.Series, gamma: float) -> pd.Series:
    """Calculate Laguerre filter stages"""
    pass

def calculate_laguerre_rsi(prices: pd.Series, period: int = 32) -> pd.Series:
    """
    Calculate ATR adaptive smoothed Laguerre RSI.

    Args:
        prices: Close prices
        period: ATR period (default 32)

    Returns:
        Laguerre RSI values (0-1 range)
    """
    # 1. Calculate ATR
    tr = calculate_true_range(...)
    atr = calculate_atr(tr, period)

    # 2. Adaptive coefficient
    ...

    # 3. Laguerre filter
    ...

    # 4. RSI calculation
    ...

    return laguerre_rsi
```

### Phase 5: Integrate with Export Script

**Objective**: Add indicator to Wine Python export script.

**File**: `$BOTTLE_ROOT/drive_c/users/crossover/export_aligned.py`

**Integration Steps**:

1. **Import module**:
```python
# Add at top of export_aligned.py
from indicator_laguerre_rsi import calculate_laguerre_rsi
```

2. **Add CLI argument**:
```python
parser.add_argument(
    '--laguerre-period',
    type=int,
    default=32,
    help='Laguerre RSI ATR period (default: 32)'
)
```

3. **Calculate indicator**:
```python
# In export_data() function after OHLC fetch
df['laguerre_rsi'] = calculate_laguerre_rsi(
    df['close'],
    period=laguerre_period
)
```

4. **Update CSV export**:
```python
# Update column selection
export_df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume', 'rsi', 'laguerre_rsi']].copy()
export_df.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'Laguerre_RSI']
```

### Phase 6: Validation

**Objective**: Verify Python implementation matches MT5 output.

**Approach**:

1. **Export MT5 indicator data** (manual or via script with indicator values)
2. **Export Python calculated data** using Wine Python script
3. **Compare with validator**:
```bash
python python/validate_export.py exports/Export_SYMBOL_with_laguerre.csv
```

**Validation Criteria**:
- **Correlation**: ≥ 0.999
- **Mean Absolute Error**: < 0.1
- **Data Integrity**: 100% (no NaN/inf values)

## Workflow Robustness Audit

### Strengths ✅

1. **Clear separation of environments**:
   - MT5 source code in bottle (immutable)
   - Python translation in bottle (Wine Python execution)
   - Validation in native macOS (native Python)
   - Repo tracking (Git)

2. **Path clarity**:
   - Absolute paths documented
   - Wine vs macOS paths clearly distinguished
   - Environment variables documented (CX_BOTTLE, WINEPREFIX)

3. **Modular approach**:
   - Indicators as separate Python modules
   - Reusable components (ATR, EMA, etc.)
   - Easy to add new indicators

4. **Validation pipeline**:
   - Automated correlation checks
   - Data integrity verification
   - RSI formula precision validated

### Weaknesses & Mitigations ⚠️

#### Weakness 1: UTF-16 Encoding in MQL5 Files
**Problem**: MQL5 files may be UTF-16 encoded, causing read issues.

**Mitigation**:
```bash
# Check encoding
file "indicator.mq5"

# Convert if needed
iconv -f UTF-16LE -t UTF-8 "indicator.mq5" > "indicator_utf8.mq5"

# Or read with Python
with open('indicator.mq5', 'r', encoding='utf-16-le') as f:
    content = f.read()
```

#### Weakness 2: Manual Indicator Extraction
**Problem**: No automated MQL5 → Python translation (requires manual code review).

**Mitigation**:
- Document common patterns (see Mapping Guide above)
- Build library of translated components (ATR, EMA, RSI, etc.)
- Create template for new indicators

**Recommended**: Create `python/indicators/` directory with:
```
python/indicators/
├── __init__.py
├── base.py           # Base indicator class
├── atr.py            # ATR calculation
├── ema.py            # EMA calculation
├── rsi.py            # RSI calculation (already have)
├── laguerre.py       # Laguerre filter
└── laguerre_rsi.py   # Combined indicator
```

#### Weakness 3: No Automated Dependency Resolution
**Problem**: Include files (`#include <...>`) not automatically tracked.

**Mitigation**:
```bash
# Extract includes from MQL5 file
grep "#include" "indicator.mq5"

# Locate include files
find "$MQL5_ROOT/Include" -name "MovingAverages.mqh"

# Review include file for functions used
```

#### Weakness 4: Complex Indicator State Management
**Problem**: Some indicators maintain state across bars (e.g., Laguerre filter stages).

**Mitigation**:
- Use class-based approach for stateful indicators
- Initialize buffers properly
- Test incremental updates vs full recalculation

**Example**:
```python
class LaguerreRSI:
    def __init__(self, period=32):
        self.period = period
        self.laguerre_stages = np.zeros((4,))  # 4 stages

    def update(self, price):
        """Incremental update (O(1))"""
        # Update filter stages
        ...

    def calculate(self, prices):
        """Full calculation (O(n))"""
        # Calculate all values
        ...
```

#### Weakness 5: Performance Differences
**Problem**: MQL5 optimized for tick-by-tick calculation, Python for vectorized batch processing.

**Mitigation**:
- Focus on batch processing (5000+ bars)
- Use NumPy vectorization
- Profile slow operations with `timeit`
- Consider Numba JIT compilation for hot paths

**Benchmark**:
```python
import timeit

# Test ATR calculation performance
timeit.timeit(
    'calculate_atr(tr, period=14)',
    setup='from indicators.atr import calculate_atr; import numpy as np; tr = np.random.rand(5000)',
    number=1000
)
```

### Expansion Readiness Assessment

**Question**: Are we ready to translate more indicators like "ATR adaptive smoothed Laguerre RSI 2 (extended).mq5"?

**Answer**: **Partially Ready** ✅⚠️

**Ready**:
- ✅ File location discovery (documented)
- ✅ Wine Python execution (v3.0.0 validated)
- ✅ Validation pipeline (0.999+ correlation)
- ✅ CSV export workflow (automated)
- ✅ Git tracking (repo structure)

**Needs Improvement**:
- ⚠️ UTF-16 encoding handling (add to workflow)
- ⚠️ Dependency resolution (manual for now)
- ⚠️ Indicator library structure (create `python/indicators/`)
- ⚠️ State management patterns (document class-based approach)
- ⚠️ Performance benchmarking (add to validation)

### Recommended Next Steps

1. **Create indicator library structure**:
```bash
mkdir -p python/indicators
touch python/indicators/__init__.py
touch python/indicators/base.py
```

2. **Document common MQL5 patterns**:
   - Create `docs/guides/MQL5_PYTHON_PATTERNS.md`
   - Document buffer management, state handling, etc.

3. **Build reusable components**:
   - Extract ATR calculation to `python/indicators/atr.py`
   - Extract EMA to `python/indicators/ema.py`
   - Extract RSI to `python/indicators/rsi.py`

4. **Add encoding detection to workflow**:
   - Update `export_aligned.py` to handle UTF-16 if needed
   - Add file encoding check to validation

5. **Create indicator translation template**:
   - Template MQL5 analysis checklist
   - Template Python module structure
   - Template test cases

## References

- **Wine Python Execution**: `WINE_PYTHON_EXECUTION.md ` - v3.0.0 production workflow
- **Validation Pipeline**: `python/validate_export.py ` - RSI correlation validation
- **Export Script**: `~/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/users/crossover/export_aligned.py `
- **Implementation Plan**: `../plans/HEADLESS_EXECUTION_PLAN.md ` - v3.0.0 development history

## Path Quick Reference

```bash
# Bottle root
BOTTLE_ROOT="/Users/terryli/Library/Application Support/CrossOver/Bottles/MetaTrader 5"

# MT5 indicators source
INDICATORS_ROOT="$BOTTLE_ROOT/drive_c/Program Files/MetaTrader 5/MQL5/Indicators"

# Wine Python executable
WINE_PYTHON="$BOTTLE_ROOT/drive_c/Program Files/Python312/python.exe"

# Export script
EXPORT_SCRIPT="$BOTTLE_ROOT/drive_c/users/crossover/export_aligned.py"

# Native Python validator
VALIDATOR="$REPO_ROOT/python/validate_export.py"

# Target indicator
TARGET_INDICATOR="$INDICATORS_ROOT/Custom/ATR adaptive smoothed Laguerre RSI 2 (extended).mq5"
```

---

**Last Updated**: 2025-10-13 20:00
**Status**: Active reference document for indicator translation workflow
