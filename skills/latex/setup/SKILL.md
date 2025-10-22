---
name: LaTeX Environment Setup
description: Install and configure complete LaTeX development environment on macOS with MacTeX, Skim viewer, and SyncTeX support. Use when setting up new machine, installing LaTeX distribution, configuring PDF viewer, or troubleshooting package installations.
---

# LaTeX Environment Setup Skill

## Quick Reference

**When to use this skill:**
- Installing LaTeX on a new machine
- Setting up MacTeX distribution
- Configuring Skim PDF viewer with SyncTeX
- Verifying LaTeX installation
- Troubleshooting missing packages

## Recommended Stack

| Component | Purpose | Status |
|-----------|---------|--------|
| **MacTeX 2025** | Full LaTeX distribution (TeX Live 2025) | ✅ Recommended |
| **Skim 1.7.11** | PDF viewer with SyncTeX support | ✅ macOS only |
| **TeXShop 5.57** | Integrated LaTeX IDE (optional) | ✅ Native macOS |

---

## Installation

### Option 1: Full MacTeX (Recommended)

```bash
# Download from mactex.org
# Or install via Homebrew:
brew install --cask mactex

# Size: ~4.5 GB (includes everything)
# Includes: TeX Live 2025, TeXShop, BibDesk, LaTeXiT, Skim
```

### Option 2: Lightweight (No GUI Tools)

```bash
# Smaller install without GUI tools
brew install mactex-no-gui

# Size: ~2 GB
# Includes: TeX Live 2025, latexmk, but no TeXShop/BibDesk
```

### Install Skim Separately (if using no-gui)

```bash
brew install --cask skim

# Why Skim?
# - ONLY macOS PDF viewer with full SyncTeX support
# - Forward search: LaTeX source → PDF location
# - Inverse search: PDF → LaTeX source
# - Auto-reload on PDF changes
```

---

## Verification

### Check Installation

```bash
# Check TeX version
tex --version
# Expected: TeX 3.141592653 (TeX Live 2025)

# Check pdflatex
pdflatex --version

# Check latexmk
latexmk --version
# Expected: Latexmk, John Collins, version 4.86a
```

### Verify PATH

```bash
# TeX binaries should be in PATH
which pdflatex
# Expected: /Library/TeX/texbin/pdflatex

# Check environment
echo $PATH | grep -o '/Library/TeX/texbin'
```

### Test Basic Compilation

```bash
# Create test document
cat > test.tex <<'EOF'
\documentclass{article}
\begin{document}
Hello World!
\end{document}
EOF

# Compile
pdflatex test.tex

# Verify PDF created
ls test.pdf
```

---

## Package Management

### Check if Package Installed

```bash
# Use kpsewhich to find package
kpsewhich tabularray.sty
# If found: /usr/local/texlive/2025/texmf-dist/tex/latex/tabularray/tabularray.sty
# If not found: (empty output)
```

### Install Missing Package

```bash
# Update TeX Live package manager
sudo tlmgr update --self

# Install specific package
sudo tlmgr install tabularray

# Verify installation
kpsewhich tabularray.sty
```

### Search for Packages

```bash
# Search for package by name
tlmgr search --global tabularray

# List all installed packages
tlmgr list --only-installed
```

---

## Skim Configuration

### Enable SyncTeX

**In your LaTeX compilation:**
```bash
# Add -synctex=1 flag
pdflatex -synctex=1 document.tex

# Or use latexmk (automatically enables SyncTeX)
latexmk -pdf document.tex
```

### Skim Preferences

1. **Skim → Preferences → Sync**
2. **Preset:** Custom
3. **Command:** Path to your editor
4. **Arguments:** Depends on editor (e.g., for VS Code: `--goto %file:%line`)

**For Helix:**
```
Command: /usr/local/bin/hx
Arguments: %file:%line
```

---

## Troubleshooting

### Issue: TeX binaries not in PATH

```bash
# Add to ~/.zshrc or ~/.bash_profile
export PATH="/Library/TeX/texbin:$PATH"

# Reload shell
source ~/.zshrc
```

### Issue: sudo required for tlmgr

```bash
# This is normal for system-wide MacTeX installation
# Use sudo for package management:
sudo tlmgr install <package>
```

### Issue: Package not found

```bash
# Update tlmgr database
sudo tlmgr update --self --all

# Search for package
tlmgr search --global <package-name>

# Install
sudo tlmgr install <package-name>
```

### Issue: Permission errors

```bash
# Fix permissions on TeX Live directory
sudo chown -R $(whoami):staff /usr/local/texlive/2025/texmf-var
```

---

## Post-Installation Checklist

- [ ] Verify `tex --version` shows TeX Live 2025
- [ ] Verify `latexmk --version` shows 4.86a+
- [ ] Verify `pdflatex test.tex` creates PDF
- [ ] Install Skim if using mactex-no-gui
- [ ] Test SyncTeX: compile with `-synctex=1` flag
- [ ] Configure Skim preferences for editor integration
- [ ] Add `/Library/TeX/texbin` to PATH if needed
- [ ] Test package installation: `sudo tlmgr install <package>`

---

## See Also

- **Build Workflows**: Use `latex/build` skill for latexmk automation
- **Table Creation**: Use `latex/tables` skill for tabularray usage
- **Reference**: Check `REFERENCE.md` for complete installation guide
