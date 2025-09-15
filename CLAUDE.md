# Claude Code User Memory

## Workspace-Wide Development Principles

### Language Evolution
- **Evolutionary Mindset**: Never use promotional language ("enhanced", "improved", "optimized") - everything is evolutionary by nature
- **Application Scope**: ALL Claude Code workspace content, documentation, commit messages, communications, and development work
- **Rationale**: Eliminates maintenance burden of constantly updating promotional qualifiers in evolving development environments

### Planning Philosophy
- **Logical Dependencies**: Never use time-based planning (hours, days, weeks) or roadmapping; organize by logical dependencies, priorities, and capabilities instead
- **Dynamic Evolution**: Objectives and implementations are dynamically evolutionary by nature

## Claude Code User Memory Documentation Principles

### Document Definition
- **Scope**: These principles apply _ONLY_ to this Claude Code user memory file Located in `.claude/CLAUDE.md`
- **Purpose**: This document serves as a high-level pointer/reference only
- **Rationale**: Detailed specifications belong in the actual script files to avoid redundancy

### Content Standards
- **Include**: Environment preferences, tool choices, file locations
- **Exclude**: Implementation details, parameters, version numbers, limitations, processing flows

## System Architecture & Environment

### Platform & Path Conventions
- **Target Platform**: Unix-like systems (macOS, Linux) - **Not designed for Windows compatibility**
- **Path Standards**: `$HOME` (resolves to `/Users/$USER` on macOS, `/home/$USER` on Linux)
- **Workspace Location**: `$HOME/.claude/` (follows dotfile convention)
- **Shell Environment**: POSIX-compliant shells (zsh, bash)
- **Portability**: All documentation MUST use Unix conventions (`$HOME`, `$USER`) for cross-user compatibility

### Universal Tool Access & Working Directory Preservation
- **Hybrid Architecture Strategy**: `$HOME/.local/bin/` for executables, `$HOME/.claude/tools/` for supporting files/configs
- **PATH Configuration**: Shell configuration includes ONLY `$HOME/.local/bin` in PATH (industry standard)
- **Clean Separation**: Executables globally accessible, source code and configs organized in .claude structure
- **Cross-Platform Consistency**: Same tool access pattern on macOS and Linux environments
- **Absolute Path Resolution**: Scripts use absolute paths to find supporting files in .claude structure
- **Architecture Pattern**: Tools use `uv run --active python -m --directory` for self-contained environments while preserving working directory context
- **Working Directory Principle**: All workspace scripts MUST preserve user's current working directory - avoid `cd` operations that permanently change user context (subshell path resolution and save/restore patterns are acceptable)

### Current User Context
- Engineering lead responsible for features engineering for downstream seq-2-seq model consumption

## Defensive Programming Standards

### Data Authenticity Requirements - CCXT MANDATE
- **CCXT USDⓈ-M Perpetuals ONLY**: Use CCXT direct Binance API connectivity as the exclusive authentic data source for all financial data collection
- **USDⓈ-M Perpetuals ONLY**: `'defaultType': 'future'` (USDⓈ-Margined Perpetuals), BTC/USDT:USDT perpetual - NEVER spot or other derivatives
- **Performance Validated**: 35x more data than constraints (26,280 vs 744 bars), perfect backtesting.py compatibility
- **Zero Synthetic Data Tolerance**: Never use fake, mock, synthetic, or placeholder financial data in ANY scenario
- **Production Quality Sources**: All data must originate from direct Binance USDⓈ-M Perpetuals API sources
- **Data Integrity**: Validate all inputs at system boundaries with explicit type checking

### CCXT USDⓈ-M Perpetuals Integration Standards
- **Mandatory Library**: `import ccxt`
- **Installation Command**: `uv add ccxt`
- **Standard Configuration**: 
  ```python
  exchange = ccxt.binance({
      'options': {'defaultType': 'future'}  # USDⓈ-M Perpetuals ONLY
  })
  # Collect authentic USDⓈ-M Perpetuals data: 26,280 bars vs 744 constraint
  ohlcv = exchange.fetch_ohlcv('BTC/USDT:USDT', '1h', since, 1000)
  ```
- **Perfect OHLCV Format**: Direct backtesting.py compatibility with authentic USDⓈ-M perpetual pricing
- **Authenticity Verification**: Real USDT settlement matching backtesting environment

### Input Validation Requirements  
- **Boundary Conditions**: Check for null, empty, and edge case values before processing
- **Format Validation**: Ensure data conforms to expected formats before consumption
- **Range Validation**: Verify numeric values fall within acceptable bounds

### Exception-Only Failure Principles
- **No Fallover Mechanisms**: Never implement failover, failsafe, or fallback mechanisms for data or model operations
- **Immediate Exception**: Systems must fail immediately with rich debug context, never continue with corrupted state
- **No Silent Failures**: Every anomaly, inconsistency, or boundary violation must raise explicit exceptions
- **Explicit Exceptions**: Raise structured exceptions with rich context for debugging
- **Early Detection**: Identify problems as close to source as possible

### Temporal Integrity Mandate - ZERO TOLERANCE
**ABSOLUTE RULE**: Never fit() on future data in financial backtesting

#### **Critical Violations (Auto-Reject)**
```python
# ❌ FORBIDDEN: Global scaling uses tomorrow's statistics today
scaler.fit_transform(entire_dataset)  # Knows future means/stds
cross_val_score(model, scaled_data, target, cv=TimeSeriesSplit())

# ❌ FORBIDDEN: Target leakage
features['next_return'] = returns.shift(-1)  # Uses future returns

# ❌ FORBIDDEN: Future parameter optimization  
best_params = grid_search_on_full_period()  # Optimizes on test outcomes
```

#### **Correct Implementation**
```python
# ✅ MANDATORY: Per-fold scaling via Pipeline
pipeline = Pipeline([('scaler', StandardScaler()), ('model', Model())])
cross_val_score(pipeline, raw_features, target, cv=TimeSeriesSplit(5))

# ✅ MANDATORY: Per-window WFA scaling
for window in wfa_windows:
    train_scaler = StandardScaler().fit(train_data[window])  # Only historical
    test_scaled = train_scaler.transform(test_data[window])  # Apply historical stats
```

#### **Enforcement**
- **Exception-Only**: Any `.fit()` on future data → immediate system failure
- **Code Audit**: Search all `.fit_transform()` calls for temporal violations  
- **Validation**: Every ML pipeline must demonstrate temporal integrity compliance

### Auditing Temporal Violations (ATV) Framework
**PURPOSE**: Systematic detection of temporal violations in OHLCV + technical indicators + cross-validation backtesting systems

#### **ATV Pipeline Audit (13 Violations)**
**DATA COLLECTION PHASE**:
- Data leakage (future data contaminating historical)
- Frequency mismatch violations (mixed timeframes)

**FEATURE ENGINEERING PHASE**:
- Look-ahead bias (features using future data)
- Scaling violations (using future statistics) 
- Feature engineering violations (TA indicators with future data)
- Target generation violations (incorrect temporal relationships)
- Index alignment violations (timestamp mismatches)

**MODEL TRAINING PHASE**:
- Memory/state violations (model state bleeding between windows)
- Sampling/selection violations (cherry-picking periods)

**EVALUATION PHASE**:
- Temporal misalignment (wrong chronological order)
- Time-based splitting errors (improper train/test boundaries)
- Cross-validation temporal violations (CV fold contamination)
- Benchmark/comparison violations (benchmark using future data)

#### **ATV Audit Checklist**
```python
# ✅ Quick ATV audit commands:
# 1. grep -n "shift(-" *.py  # Check for look-ahead bias
# 2. grep -n "fit_transform.*entire" *.py  # Check scaling violations  
# 3. grep -n "for.*model.*fit" *.py  # Check memory/state violations
# 4. grep -n "TimeSeriesSplit\|cross_val" *.py  # Check CV implementation
```

#### **ATV Success Criteria**
- **All 13 violations clean** → Temporal integrity confirmed
- **Any violation found** → Fix before proceeding
- **Regular ATV audits** → Maintain temporal integrity over time

## Quantitative Development Standards

### backtesting.py Strategy Architecture - EXCLUSIVE FRAMEWORK
**MANDATE**: backtesting.py ONLY for all quantitative backtesting

#### **Separated LONG/SHORT Strategy Pattern**
- **Implementation**: Separate Strategy classes, never unified LONG/SHORT
- **Pattern**:
  ```python
  class LongOnlyStrategy(Strategy):  # Pure LONG momentum
  class ShortOnlyStrategy(Strategy): # Pure SHORT momentum  
  class PortfolioManager:            # Combines results manually
  ```
- **Source**: Empirically derived (Dec 2024) - unified approaches failed execution despite generating signals

### backtesting.py Universal Configuration Standards

#### **Canonical Configuration Template**
```python
# Universal backtesting.py configuration for crypto assets
bt = Backtest(
    data,                    # OHLCV DataFrame from CCXT USDⓈ-M Perpetuals API  
    StrategyClass,          # Strategy class (not instance)
    cash=10_000_000,        # Universal cash - works for any crypto asset
    commission=0.0008,      # Realistic USDⓈ-M perpetuals rate (8bp)
    exclusive_orders=True,  # Clean position management
    trade_on_close=False    # Prevent look-ahead bias
)
```

#### **Parameter Documentation (Official backtesting.py Sources)**

**`data` (Required)**:
- **Official**: "A pandas DataFrame with columns Open, High, Low, Close, and optionally Volume"
- **Standard**: OHLCV from CCXT USDⓈ-M Perpetuals API with authentic pricing and datetime index

**`strategy` (Required)**:
- **Official**: "A Strategy subclass (not an instance) defining trading logic"
- **Critical**: Pass the **class itself**, never `StrategyClass()` instance

**`cash` (Optional, Default: $10,000)**:
- **Official**: "Initial cash to start the backtest, defaulting to $10,000"
- **Empirical**: `10_000_000` ($10M) validated for ALL crypto assets (BTCUSDT ~$111K, ETHUSDT ~$4.3K)

**`commission` (Optional, Default: 0.0)**:
- **Official**: "Trading commission rate" supporting float, tuple, or callable formats
- **Standard**: `0.0008` = 8bp (realistic Binance USDⓈ-M perpetuals rate)

**`exclusive_orders` (Optional, Default: False)**:
- **Official**: "If True, each new order automatically closes the previous trade/position"
- **Standard**: `True` - prevents position stacking, complements separated LONG/SHORT

**`trade_on_close` (Optional, Default: False)**:
- **Official**: "If True, market orders filled at current bar's closing price instead of next bar's open"
- **Standard**: `False` - orders execute at **next bar's open** (prevents look-ahead bias)

#### **Order Execution Timing**
**Sequence** (with `trade_on_close=False`):
1. `next()` called at bar N → 2. Order placed at bar N → 3. Executes at bar N+1 open

#### **Mandatory Standards**
- **Cash**: `10_000_000` 
- **Commission**: `0.0008`
- **Exclusive Orders**: `True`
- **Trade on Close**: `False`
- **Data Source**: CCXT USDⓈ-M Perpetuals API with direct Binance connectivity ONLY
- **Strategy Pattern**: Separated LONG/SHORT classes
- **Benchmark Comparison**: Required for all strategies (see Benchmark Standards below)

### Benchmark Comparison Standards - EMPIRICALLY VALIDATED

**UNIVERSAL REQUIREMENT**: ALL quantitative strategies MUST include benchmark comparison for accurate performance assessment

#### **Canonical Benchmark Implementation**
```python
# Buy-and-Hold Benchmark for LONG strategies
class BuyAndHoldBenchmark(Strategy):
    def init(self): pass
    def next(self):
        if not self.position: self.buy()

# Short-and-Hold Benchmark for SHORT strategies  
class ShortAndHoldBenchmark(Strategy):
    def init(self): pass
    def next(self):
        if not self.position: self.sell()
```

#### **Direction-Specific Benchmark Selection**
- **LONG Strategies**: MUST compare against `BuyAndHoldBenchmark`
- **SHORT Strategies**: MUST compare against `ShortAndHoldBenchmark`  
- **NEUTRAL Strategies**: Default to `BuyAndHoldBenchmark`

#### **Benchmark Configuration Standards**
```python
# LONG strategy benchmark
benchmark_bt = Backtest(data, BuyAndHoldBenchmark, cash=10_000_000, commission=0.0008)

# SHORT strategy benchmark  
benchmark_bt = Backtest(data, ShortAndHoldBenchmark, cash=10_000_000, 
                       commission=0.0008, margin=0.5)
```

#### **Performance Metrics (Mandatory)**
- **Alpha**: `strategy_return - benchmark_return` (primary metric)
- **Excess Sharpe**: `strategy_sharpe - benchmark_sharpe`
- **Information Ratio**: `mean(excess_returns) / std(excess_returns)`
- **Tracking Error**: `std(excess_returns) * sqrt(252)` (annualized)
- **Risk Improvement**: `benchmark_max_dd - strategy_max_dd`

#### **Integration Pattern**
```python
from benchmarks.benchmark_comparison_framework import BenchmarkComparisonFramework

# Initialize framework
framework = BenchmarkComparisonFramework(cash=10_000_000, commission=0.0008)

# Run strategy with automatic benchmark comparison
comparison_results = framework.run_benchmark_comparison(data, StrategyClass)

# Access results
alpha = comparison_results['metrics']['alpha']
excess_sharpe = comparison_results['metrics']['excess_sharpe']
benchmark_used = comparison_results['benchmark_class']

print(f"Alpha: {alpha:+.2f}%")
print(f"Benchmark: {benchmark_used}")
```

#### **Validation Requirements**
- **Performance Assessment**: Strategy MUST generate alpha > 0% for production use
- **Risk Analysis**: Strategy MUST show risk improvement vs benchmark
- **Statistical Significance**: Information Ratio > 1.0 indicates meaningful outperformance
- **Trade Validation**: Strategy MUST execute trades (benchmark comparison fails with 0 trades)

## Development Environment & Tools

### Primary Toolchain
- **Python Management**: `uv` for all Python operations (`uv run --active python -m`, `uv add`) - **Avoid**: pip, conda, pipenv
- **Rust Development**: `cargo` with ARM64-native compilation, cross-platform targets ready
- **GPU-Accelerated Computing**: `uv add cupy` - GPU-accelerated NumPy replacement for CUDA/ROCm acceleration across all numerical computing
- **Backtesting Framework**: backtesting.py EXCLUSIVELY - **Prohibited**: bt, vectorbt, btester, backtrader, zipline, pyfolio, quantlib, NautilusTrader, any alternative backtesting frameworks
- **Python-Rust Integration**: `maturin develop --release --uv` for building PyO3 extensions with consistent uv package management
- **Information Theory & Pattern Analysis**: 
  - **Primary**: `uv add infomeasure jax jaxlib` - SOTA 2024-2025 entropy stack
  - **Specialized**: `uv add entropyhub pydtmc numpyro jaxent` - Pattern analysis & Markov chains
  - **Performance Hierarchy**: JAX (35x GPU speedup) > infomeasure (<1min/100k elements) > EntropyHub (comprehensive)
  - **Deprecated**: pyinform, scipy.stats entropy functions - use infomeasure instead
- **Module-Only Execution**: Mandatory `-m` flag with on-demand compatibility resolution and consolidation over proliferation
- **Python Version**: 3.12+, type checking disabled (development environment)
- **Libraries**: Prefer `httpx` over `requests`, `platformdirs` for cache directories
- **Remote Access**: Prefer `curl` over fetch
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

### Rust Environment Configuration (Cross-Platform)
- **Shell Integration**: Standard `.zshrc` configuration with Rust-first PATH precedence (`$HOME/.cargo/bin` before language-specific paths)
- **Performance Optimization**: Native compilation with target-specific flags (ARM64 macOS, x86_64 Linux)
- **Cross-Platform Targets**: Pre-configured for `aarch64-apple-darwin`, `x86_64-apple-darwin`, `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`
- **Parallel Builds**: Auto-detects CPU cores (`sysctl -n hw.ncpu` macOS, `nproc` Linux)
- **Environment Harmony**: Rust and Python toolchains coexist without PATH conflicts
- **Essential Tools**: Use `cargo nextest run` (enhanced testing), `cargo deny check` (comprehensive validation)
- **Utility Functions**: `rust-python-project()` (hybrid project creation), `fresh-build()` (clean rebuild)

### Mandatory Rust Code Quality Enforcement (2025 Best Practices)
- **Pre-commit Hook**: MANDATORY `.git/hooks/pre-commit` script blocks unformatted code, clippy warnings, failing tests
- **Formatting**: `cargo fmt --check` required before every commit (auto-enforced)
- **Linting**: `cargo clippy --all-targets --all-features -- -D warnings` blocks commits with warnings
- **Testing**: `cargo test` must pass before commit acceptance
- **VS Code Integration**: Auto-format on save/type/paste with rust-analyzer (`editor.formatOnSave: true`)
- **CI/CD Enforcement**: GitHub Actions validates formatting, clippy, tests on every push/PR
- **Setup Commands**:
  ```bash
  # Create mandatory pre-commit hook
  chmod +x .git/hooks/pre-commit
  # Configure VS Code rust-analyzer formatting
  # Enable pre-commit framework: pip install pre-commit && pre-commit install
  ```
- **Zero Tolerance**: No commits allowed with unformatted code, clippy warnings, or failing tests
- **New Project Requirement**: Set up mandatory enforcement for every new Rust project immediately

### Git Repository Detection
- `uv run --active python -m pathlib -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

## Documentation Standards

### Claude Code Markdown Restrictions & README Policies
- **Global `~/.claude/`**: Markdown files allowed (configuration template)
- **Project `.claude/`**: NO markdown files - Claude Code interprets them as slash commands causing invocation conflicts
- **Root README Delegation**: NEVER create root `README.md` - use `docs/README.md` as main documentation (GitHub auto-renders)
- **Related Docs**: Use alternative naming (OVERVIEW.md, INDEX.md, GUIDE.md) for non-global `.claude/` directory documentation

### Link Validation Standards
- **Pre-edit Verification**: Verify all directory links have README.md or point to existing files
- **GitHub Behavior**: Directory links without README.md show empty pages/404 on GitHub
- **Validation Scope**: Check directory references, file paths, anchor links, relative paths
- **Security Audit**: Validate shell commands, file paths, user input handling in documentation examples

## Native Pattern Conformity

### Pattern Adherence Requirements
- **User Global Patterns** (`~/.claude/CLAUDE.md`): Language evolution, Unix conventions, tool preferences, documentation standards
- **Project Patterns** (`CLAUDE.md`): PPO, COE, FPPA, NTPA, APCF compliance
- **Cross-Pattern Validation**: Ensure harmony between user global and project requirements
- **Systematic Validation**: Apply audit methodology to verify pattern conformity

## Success Gates & Success Sluices Terminology

- **Success Gates**: Major implementation milestones that must be validated before proceeding
- **Success Sluices**: Granular validation checkpoints between Success Gates that must be cleared before advancing

## Claude Code User Custom Extensions

### CNS (Conversation Notification System)
**Specification**: [`.claude/specifications/cns-conversation-notification-system.yaml`](.claude/specifications/cns-conversation-notification-system.yaml)

### GitHub Flavored Markdown Link Checker
**Specification**: [`.claude/specifications/gfm-link-checker.yaml`](.claude/specifications/gfm-link-checker.yaml)

### Pushover Integration
**API**: https://pushover.net/api
**Keychain**: `pushover-user-key`, `pushover-app-token`, `pushover-email` (account: `terryli`)
**Sounds**: `toy_story`, `dune`, `bike`, `siren`, `cosmic`, `alien`, `vibrate`, `none`

### PyPI Publishing Methods

#### Legacy Token-Based (Backup Only)
**Location**: `$HOME/.pypirc` (terryli's macOS MacBook only - not stored elsewhere)
**Authentication**: Token-based authentication (`username = __token__`)
**Manual Command**: `uv publish --token "pypi-[TOKEN]"`
**Token Format**: `pypi-AgEI...` (scoped to specific package publishing permissions)
**Unique Identifier**: `cc934ce2-87dc-4995-812b-1149d7e977cf` (publishing token ID)

#### Trusted Publishing (Primary Method - 2025 Best Practice)
**Security**: OIDC-based authentication (no stored tokens)
**Automation**: GitHub Actions with `.github/workflows/publish.yml`
**Environments**: `pypi` (production) and `testpypi` (testing)
**Approval**: Manual approval required for production releases
**Features**: Digital attestations, Sigstore signatures, zero-credential workflow
**Documentation**: `docs/PUBLISHING.md` for complete setup guide

