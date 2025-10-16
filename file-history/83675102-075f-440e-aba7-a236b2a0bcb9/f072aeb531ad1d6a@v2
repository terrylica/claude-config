# Migration Plan: mql5-crossover → drive_c/

**Date**: 2025-10-14
**From**: `/Users/terryli/eon/mql5-crossover/`
**To**: `~/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/`

---

## Migration Strategy

### ✅ What to Move

#### 1. **Documentation (23 files)** → `drive_c/docs/`
All `.md` files from old repo:
- `CLAUDE.md` → `drive_c/CLAUDE.md` (root level, project memory)
- `README.md` → `drive_c/README.md` (root level, project overview)
- `docs/` → `drive_c/docs/` (entire directory structure)

**Why**: Documentation is the single source of truth - all guides, plans, reports

#### 2. **Python Validation Tool (1 file)** → `drive_c/python/`
- `python/validate_export.py` → `drive_c/python/validate_export.py`

**Why**: Essential tool for validating CSV exports

#### 3. **Shell Scripts (2 files)** → `drive_c/scripts/`
- `scripts/mq5run` → `drive_c/scripts/mq5run` (v2.0.0 legacy wrapper)
- `scripts/setup-bottle-mapping` → `drive_c/scripts/setup-bottle-mapping`

**Why**: Automation tools, historical reference

#### 4. **MQL5 Export Scripts (2 files)** → Already exists in different form
- `mql5/Scripts/ExportAligned.mq5` - Compare with mt5work/ExportEURUSD.mq5
- `mql5/Scripts/ExportEURUSD.mq5` - Already exists in mt5work/

**Action**: Review and merge if needed, likely keep drive_c versions

#### 5. **MQL5 Include Files (3 files)** → Review for merging
- `mql5/Include/DataExportCore.mqh`
- `mql5/Include/ExportAlignedCommon.mqh`
- `mql5/Include/modules/RSIModule.mqh`

**Action**: Check if these are used by current export scripts

---

### ❌ What NOT to Move

#### 1. **Config Files**
- `.gitignore` - Already created new one for drive_c/
- `.gitattributes` - Not needed
- `reorg-plan.yml` - Historical artifact, can archive

#### 2. **Directories**
- `.venv/` - Python virtual environment, not portable
- `exports/` - CSV files, too large, generated data
- `logs/` - Runtime logs, not needed
- `config/` - MT5 configs, already in drive_c/Program Files/MetaTrader 5/Config/

#### 3. **Sample/Test Files**
- `mql5/Samples/*.mq5` - Test code, not needed

---

## Directory Structure (New)

```
drive_c/
├── .git/
├── .gitignore
├── README.md                          # ← from old repo
├── CLAUDE.md                          # ← from old repo
├── MIGRATION_PLAN.md                  # ← this file
│
├── docs/                              # ← from old repo
│   ├── guides/
│   ├── plans/
│   ├── reports/
│   └── archive/
│
├── python/
│   └── validate_export.py             # ← from old repo
│
├── scripts/
│   ├── mq5run                         # ← from old repo
│   └── setup-bottle-mapping           # ← from old repo
│
├── users/crossover/
│   ├── export_aligned.py              # ← Already here (Wine Python)
│   ├── test_mt5_connection.py         # ← Already here
│   └── exports/                       # ← CSV outputs (gitignored)
│
├── mt5work/
│   ├── ExportEURUSD.mq5               # ← Already here
│   └── auto_export.ini                # ← Already here
│
└── Program Files/MetaTrader 5/
    ├── Config/                        # ← Already here
    └── MQL5/
        ├── Indicators/
        │   ├── Custom/                # ← Already here (Laguerre RSI, etc.)
        │   └── Customs/               # ← Already here (atr_refactor_for_python)
        └── Scripts/                   # ← Check for duplicates
```

---

## Execution Steps

1. **Create directories**:
   ```bash
   mkdir -p drive_c/docs
   mkdir -p drive_c/python
   mkdir -p drive_c/scripts
   ```

2. **Copy documentation**:
   ```bash
   cp -r /Users/terryli/eon/mql5-crossover/docs/* drive_c/docs/
   cp /Users/terryli/eon/mql5-crossover/README.md drive_c/
   cp /Users/terryli/eon/mql5-crossover/CLAUDE.md drive_c/
   ```

3. **Copy Python tools**:
   ```bash
   cp /Users/terryli/eon/mql5-crossover/python/validate_export.py drive_c/python/
   ```

4. **Copy shell scripts**:
   ```bash
   cp /Users/terryli/eon/mql5-crossover/scripts/* drive_c/scripts/
   ```

5. **Review and merge MQL5 files** (manual step):
   - Compare old repo MQL5 files with drive_c/mt5work/
   - Merge if improvements found

6. **Git commit**:
   ```bash
   cd drive_c
   git add .
   git commit -m "feat: Migrate documentation and tools from mql5-crossover repo"
   ```

7. **Update CLAUDE.md** with new paths

8. **Archive old repo** (optional):
   ```bash
   mv /Users/terryli/eon/mql5-crossover /Users/terryli/eon/mql5-crossover.old
   ```

---

## Post-Migration Checklist

- [ ] All documentation accessible in drive_c/docs/
- [ ] validate_export.py works from drive_c/python/
- [ ] Scripts executable and functional
- [ ] CLAUDE.md updated with new structure
- [ ] Git history clean and committed
- [ ] Old repo archived or removed

---

## Benefits of New Structure

1. **Single source of truth** - Everything in one place (drive_c/)
2. **No syncing** - Edit where you work, git sees it immediately
3. **Complete context** - All indicators, scripts, docs, tools together
4. **Clean tracking** - Only OUR code (136 files), no MT5 bloat
5. **Natural workflow** - Compile → Test → Commit → Push

---

## Notes

- Old repo path will still exist until you manually archive/delete it
- This migration is ONE-WAY - old repo becomes read-only historical reference
- Update any external scripts that reference old repo paths
