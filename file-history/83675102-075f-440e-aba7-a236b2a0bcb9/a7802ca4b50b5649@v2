# CrossOver Bottle File Tracking

**Strategy**: Host repo as single source of truth (Solution 1)
**Status**: Implementation guide
**Created**: 2025-10-13

## Architecture

```
macOS Git Repo                     CrossOver Bottle
/Users/terryli/eon/mql5-crossover/ → X:\ (mapped drive)
├── mql5/                          → X:\mql5\
├── python/                        → X:\python\
├── scripts/                       → X:\scripts\
├── config/                        → X:\config\
├── exports/                       → X:\exports\
└── logs/                          → X:\logs\

Wine Python reads from:  X:\python\
MT5 writes exports to:   X:\exports\
Config templates in:     X:\config\
```

**Key Insight**: Single Git repo on macOS, visible to bottle apps via `X:` drive mapping. No Git inside bottle, no file duplication, no sync scripts.

## Implementation Steps

### Step 1: Map Project as X: Drive

**GUI Method** (Recommended):
1. Open CrossOver
2. Select "MetaTrader 5" bottle
3. Click "Manage Bottle" → "Configuration"
4. Go to "Drives" tab
5. Add new drive mapping:
   - Drive letter: `X:`
   - Path: `/Users/terryli/eon/mql5-crossover`
6. Click "Apply"

**CLI Method** (Alternative):
```bash
# Edit bottle registry (requires Wine registry editor)
BOTTLE_REG="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5/drive_c/windows/system32/config/system"
# Manual edit needed - GUI method preferred
```

### Step 2: Update Wine Python Scripts

Wine Python scripts already in bottle can reference `X:\python\` for imports:

```python
# C:\users\crossover\export_aligned.py
import sys
sys.path.insert(0, r'X:\python')  # Add mapped repo path

# Now can import from repo
# import validate_export  # if needed
```

### Step 3: Redirect MT5 Exports to X:

Update export script to write directly to mapped drive:

```python
# In export_aligned.py
OUTPUT_DIR = r'X:\exports'  # Write directly to repo
os.makedirs(OUTPUT_DIR, exist_ok=True)
```

**Benefit**: CSV files land directly in Git repo, no copy step needed.

### Step 4: Update mq5run for X: Paths

See `scripts/mq5run-x-drive` for updated version that:
- Copies config from `X:\config\startup_template.ini` to MT5 directory
- Points MT5 to scripts in `X:\mql5\Scripts\` (via mapped path)
- Exports land in `X:\exports\` automatically

### Step 5: Git Hygiene

**Add .gitattributes** to normalize line endings:

```bash
cat > .gitattributes << 'EOF'
# Normalize line endings between macOS and Wine
* text=auto

# MQL5 files (Windows line endings)
*.mq5 text eol=crlf
*.mqh text eol=crlf

# Python files (Unix line endings)
*.py text eol=lf
*.sh text eol=lf

# Binary files
*.ex5 binary
*.dll binary
*.exe binary

# CSV exports (Unix line endings, easier for diff)
*.csv text eol=lf
EOF

git add .gitattributes
git commit -m "Add .gitattributes for Wine/macOS line ending normalization"
```

### Step 6: Backup Strategy

**Periodic bottle snapshots**:
```bash
# Export bottle via CrossOver GUI
# File → "MetaTrader 5" → "Manage Bottle" → "Archive"
# Saves to: ~/Documents/CrossOver/Bottle Archives/MetaTrader5_YYYYMMDD.cxarchive

# Or via CLI (if supported):
# cxarchive --bottle "MetaTrader 5" --output ~/backups/mt5-$(date +%Y%m%d).cxarchive
```

**Git repo backups**:
```bash
# Standard git operations - bottle files are already tracked
git add exports/*.csv config/startup.ini
git commit -m "Update exports and config"
git push origin main
```

## Usage Patterns

### Pattern 1: Develop MQL5 Code

```bash
# 1. Edit source on macOS
vim mql5/Scripts/ExportAligned.mq5

# 2. Compile via mq5c (auto-stages to bottle)
mq5c mql5/Scripts/ExportAligned.mq5

# 3. Run via mq5run (reads from X: if updated)
./scripts/mq5run --symbol EURUSD --period PERIOD_M1

# 4. Commit changes
git add mql5/Scripts/ExportAligned.mq5 exports/*.csv
git commit -m "Update export script and validate"
```

### Pattern 2: Python Script Development

```bash
# 1. Edit Wine Python script (accessible from bottle)
vim python/export_aligned_wine.py  # If we move script to repo

# 2. Or edit in bottle location and it's visible via X:
# Wine path: C:\users\crossover\export_aligned.py
# macOS path: ~/...Bottles/.../drive_c/users/crossover/export_aligned.py
# Better: Move to repo and reference X:\python\export_aligned.py
```

### Pattern 3: CSV Export Collection

```bash
# Exports automatically land in repo via X:\exports\
ls -lh exports/*.csv

# Validate immediately
python python/validate_export.py exports/Export_EURUSD_PERIOD_M1.csv

# Commit results
git add exports/Export_*.csv
git commit -m "Add EURUSD M1 export validation"
```

## Troubleshooting

### Issue: X: Drive Not Visible in Wine Apps

**Check mapping**:
```bash
# List bottle drives
BOTTLE_ROOT="$HOME/Library/Application Support/CrossOver/Bottles/MetaTrader 5"
cat "$BOTTLE_ROOT/cxbottle.conf" | grep -A5 "Drives"

# Or check in Wine
mt5-start cmd /c "dir X:\"
```

**Solution**: Verify drive letter in CrossOver Configuration → Drives tab.

### Issue: Permission Denied Writing to X:

**Cause**: macOS file permissions on repo directory.

**Solution**:
```bash
# Ensure bottle user can write
chmod -R u+w /Users/terryli/eon/mql5-crossover/exports/
chmod -R u+w /Users/terryli/eon/mql5-crossover/logs/
```

### Issue: Wine Python Can't Import from X:

**Cause**: Python path not including `X:\python\`.

**Solution**:
```python
# Add at top of Wine Python script
import sys
sys.path.insert(0, r'X:\python')
```

### Issue: MT5 Ignores X: Path in Config

**Cause**: Some MT5 paths are hardcoded to `C:\Program Files\...`.

**Solution**:
- Keep compiled `.ex5` in standard MT5 location
- Only redirect exports and user-editable configs to `X:`
- Use mq5c staging (it handles this automatically)

## Security Considerations

**Do NOT commit**:
- MT5 account credentials
- API keys or tokens
- Broker-specific configurations with account numbers

**Use .gitignore**:
```bash
# Add to .gitignore
config/startup.ini        # Contains symbol-specific configs
config/account_*.ini      # Account credentials
*.secret
.env
```

**Template pattern**:
```bash
# Commit template
config/startup_template.ini

# Generate actual config at runtime
cp config/startup_template.ini config/startup.ini
sed -i '' 's/SYMBOL_PLACEHOLDER/EURUSD/g' config/startup.ini
```

## Benefits Summary

✅ **Single source of truth**: One Git repo, one CI pipeline
✅ **No duplication**: Files edited once, visible everywhere
✅ **Immediate validation**: Exports land in repo, validate instantly
✅ **Standard Git workflow**: No special bottle commands needed
✅ **Disaster recovery**: Git history + periodic bottle archives
✅ **Multi-machine sync**: Standard git push/pull

## Limitations

⚠️ **MT5 compiled files**: `.ex5` files stay in `C:\Program Files\...` (not tracked)
⚠️ **Registry changes**: Not tracked by Git (use bottle archives for full environment)
⚠️ **Wine configuration**: Bottle-specific settings need bottle archives
⚠️ **Large CSV files**: Consider Git LFS if exports exceed 100MB

## Alternative: Git Inside Bottle (Not Recommended)

If you must use Git inside the bottle:
```bat
REM Inside bottle, install Git for Windows
REM Then initialize repo
cd C:\users\crossover
git init
git config core.autocrlf true
echo * text=auto > .gitattributes
```

**Why not recommended**: Dual repos to manage, CRLF complexity, bottle updates can break Git installation.

## References

- **CrossOver Drive Mapping**: [support.codeweavers.com/mapping-a-drive](https://support.codeweavers.com/mapping-a-drive-or-external-volume)
- **Bottle Archiving**: [support.codeweavers.com/archiving-and-restoring](https://support.codeweavers.com/common-actions/archiving-and-restoring-a-bottle)
- **Git Line Ending Handling**: [git-scm.com/book/en/v2/Customizing-Git-Git-Attributes](https://git-scm.com/book/en/v2/Customizing-Git-Git-Attributes)
- **Research Findings**: See community research summary in project root

## Implementation Checklist

- [ ] Map `/Users/terryli/eon/mql5-crossover/` as `X:` in CrossOver
- [ ] Add `.gitattributes` for line ending normalization
- [ ] Update Wine Python scripts to reference `X:\python\`
- [ ] Update `export_aligned.py` to write to `X:\exports\`
- [ ] Test: Run export, verify CSV appears in repo `exports/`
- [ ] Test: Edit MQL5 file, compile with mq5c, verify in bottle
- [ ] Create initial bottle archive backup
- [ ] Update `.gitignore` for sensitive configs
- [ ] Document in CLAUDE.md for future reference
