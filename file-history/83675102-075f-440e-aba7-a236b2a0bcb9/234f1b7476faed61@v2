# MT5 CrossOver Development Workspace

**Git Repository**: `~/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/`

This is the primary development workspace for MQL5 indicators, Python validation tools, and MT5 automation scripts.

## Quick Links

- **Project Memory**: [`CLAUDE.md`](CLAUDE.md) - Complete project context and instructions
- **Documentation Index**: [`docs/README.md`](docs/README.md) - Hub for all guides, plans, and reports
- **Migration Plan**: [`docs/plans/MIGRATION_PLAN.md`](docs/plans/MIGRATION_PLAN.md) - Migration from old repo

## Directory Structure

```
drive_c/
├── docs/                     # Documentation (guides, plans, reports)
├── python/                   # Python validation tools
├── scripts/                  # Shell automation scripts
├── users/crossover/          # Wine Python scripts and exports
├── mt5work/                  # Temporary compilation area
└── Program Files/
    └── MetaTrader 5/
        ├── Config/           # MT5 configuration
        └── MQL5/             # MQL5 source code
            ├── Indicators/
            │   ├── Custom/   # Custom indicators (Laguerre RSI, etc.)
            │   └── Customs/  # Work-in-progress indicators
            └── Scripts/      # Export and utility scripts
```

## Key Components

### Indicators
- **ATR Adaptive Smoothed Laguerre RSI** - Custom indicator with temporal violation fixes
- **atr_refactor_for_python.mq5** - Python-translation-ready version

### Python Tools
- **export_aligned.py** - Wine Python script for headless MT5 data export
- **validate_export.py** - CSV validation tool with correlation checks

### Automation
- **mq5run** - Legacy v2.0.0 script wrapper (startup.ini approach)
- **setup-bottle-mapping** - CrossOver bottle path mapping

## Getting Started

See [`CLAUDE.md`](CLAUDE.md) for:
- Complete file paths and MT5 locations
- Compilation workflow (CLI via CrossOver)
- Headless execution (v3.0.0 Python API)
- Validation requirements (≥0.999 correlation)

## Documentation

All documentation is in [`docs/`](docs/):
- **Guides**: Step-by-step workflows and technical references
- **Plans**: Implementation plans and architectural decisions
- **Reports**: Validation results and status reports
- **Archive**: Historical documents and deprecated approaches

---

**Working Directory**: This directory (`drive_c/`) is both the git repository root AND the actual MT5 working environment. Changes are immediately visible to both git and MT5.
