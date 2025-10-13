# Modern LaTeX Workflow for macOS (2025)

**Purpose**: Production-ready LaTeX stack for professional PDF generation with perfect table alignment

**Status**: ✅ Installed and configured (October 2025)

---

## Stack Overview

| Component | Version | Purpose |
|-----------|---------|---------|
| **MacTeX** | 2025 (TeX Live 2025) | Full LaTeX distribution |
| **latexmk** | 4.86a (Dec 2024) | Build automation, live preview |
| **Skim** | 1.7.11 | PDF viewer with SyncTeX |
| **TeXShop** | 5.57 (2025) | Integrated LaTeX IDE |
| **tabularray** | Latest (TeX Live 2025) | Modern table system |

---

## Why This Stack?

### latexmk
- Auto-detects dependencies, runs correct number of times
- Continuous preview mode (`-pvc`) watches files
- Actively maintained (latest Dec 2024)
- Industry standard, bundled with MacTeX

### Skim
- **Only** macOS viewer with full SyncTeX support
- Auto-reloads when PDF changes
- Forward/inverse search (click PDF ↔ LaTeX source)
- Open source, actively maintained

### TeXShop
- Native macOS integrated IDE
- Editor + viewer in one window
- One-click typesetting
- Bundled with MacTeX

### tabularray
- Modern LaTeX3 package
- Replaces old packages (tabular, tabularx, longtable, booktabs)
- **Critical**: Proper fixed-width column support

---

## Installation

### 1. Install MacTeX
```bash
brew install --cask mactex-no-gui
```

After installation, update PATH:
```bash
eval "$(/usr/libexec/path_helper)"
```

Verify:
```bash
which pdflatex
# Should output: /Library/TeX/texbin/pdflatex
```

### 2. Install Skim
```bash
brew install --cask skim
```

Configure auto-reload:
```bash
defaults write -app Skim SKAutoReloadFileUpdate -boolean true
```

### 3. Install TeXShop (Optional but Recommended)
```bash
brew install --cask texshop
```

---

## Configuration

### Create `.latexmkrc` in Project Directory

```perl
# latexmk configuration for macOS with Skim

# Use pdflatex by default
$pdf_mode = 1;

# Use Skim as PDF previewer
$pdf_previewer = 'open -a Skim';

# Enable synctex for forward/inverse search
$pdflatex = '/Library/TeX/texbin/pdflatex -synctex=1 -interaction=nonstopmode %O %S';

# Continuous preview update method
$preview_continuous_mode = 1;

# Clean up auxiliary files
$clean_ext = 'synctex.gz synctex.gz(busy) run.xml tex.bbl bcf fdb_latexmk run tdo %R-blx.bib';

# Extra options
$bibtex_use = 2;  # Run bibtex/biber when needed
$force_mode = 1;  # Force completion even with errors
```

**Global config**: Copy to `~/.latexmkrc` for all projects

---

## Usage

### Workflow 1: latexmk + Skim (Terminal-based)

#### Start continuous preview:
```bash
cd /path/to/project
latexmk -pdf -pvc document.tex
```

This will:
1. Compile your document
2. Open it in Skim
3. Watch for changes and auto-recompile
4. Skim auto-updates when PDF changes

#### Edit in Helix/VS Code/any editor
- Save file → automatic recompilation (typically <1 second)
- Skim updates instantly

#### Stop watching:
```bash
# Press Ctrl+C in terminal
```

#### One-time compilation:
```bash
latexmk -pdf document.tex
```

#### Clean auxiliary files:
```bash
latexmk -c document.tex  # Keep PDF
latexmk -C document.tex  # Remove PDF too
```

---

### Workflow 2: TeXShop (Integrated IDE)

1. Open `.tex` file in TeXShop
2. Two windows appear: Editor (left) + PDF preview (right)
3. Click "Typeset" button (or `Cmd+T`)
4. Preview updates automatically

**Advantages**:
- All-in-one solution
- No terminal needed
- Native macOS experience

**Disadvantages**:
- Manual typesetting (not continuous)
- Less flexible than Helix/VS Code

---

## Table Alignment: Critical Best Practices

### ❌ WRONG: Using X-columns with fixed width

```latex
\begin{tblr}{
  colspec={X[4.8cm,l]X[1,l]},  % BROKEN - X-columns are flexible!
}
```

**Problem**: X-columns ignore fixed widths in narrow containers (minipage), causing misalignment.

### ✅ CORRECT: Using p-columns for fixed width

```latex
% Define width once
\newlength{\shortcutcolwidth}
\setlength{\shortcutcolwidth}{3.8cm}

\begin{tblr}{
  colspec={p{\shortcutcolwidth}X[l]},  % CORRECT - p{} guarantees width
  row{1}={font=\bfseries},
  hline{2}={0.5pt},
  rowsep=2pt,
}
  Shortcut & Action \\
  \texttt{Cmd+N} & New Window \\
  \texttt{Cmd+Q} & Quit \\
\end{tblr}
```

**Why this works**:
- `p{3.8cm}` = **absolute fixed width**, honored regardless of content
- `X[l]` = flexible width, takes remaining space
- All tables using same `\shortcutcolwidth` = **perfect alignment**

### Key Principles

1. **Use `p{width}` for columns that must align vertically**
2. **Use `X[align]` for flexible columns**
3. **Define widths with `\newlength` for consistency**
4. **Never use `X[width,align]` syntax** - it's unreliable

---

## SyncTeX: Forward and Inverse Search

### Forward Search: LaTeX → PDF

**Command line**:
```bash
displayline <line-number> <pdf-file> <tex-file>
```

Example:
```bash
displayline 42 document.pdf document.tex
```

This highlights the PDF location for line 42 in your `.tex` file.

### Inverse Search: PDF → LaTeX

**In Skim**:
1. `Cmd+Shift+Click` on any text in PDF
2. Your editor jumps to corresponding line in `.tex` file

**Configuration** (Skim → Preferences → Sync):
- Preset: Custom
- Command: `/opt/homebrew/bin/hx` (for Helix)
- Arguments: `%file:%line`

---

## Editor Integration

### Helix

Add to `~/.config/helix/languages.toml`:

```toml
[[language]]
name = "latex"
auto-format = false
formatter = { command = "latexindent", args = ["-"] }

[language-server.texlab.config.build]
executable = "latexmk"
args = ["-pdf", "-interaction=nonstopmode", "-synctex=1", "%f"]

[language-server.texlab.config.forwardSearch]
executable = "displayline"
args = ["%l", "%p", "%f"]
```

### VS Code

Install: **LaTeX Workshop** extension
- Auto-compiles with latexmk
- Built-in SyncTeX
- 10M+ downloads

### Vim/Neovim

Use: **VimTeX** plugin
- Full latexmk integration
- SyncTeX with Skim works out-of-box

---

## Common LaTeX Packages for Cheat Sheets

```latex
\documentclass[8pt,landscape]{extarticle}
\usepackage[margin=0.4in]{geometry}
\usepackage{tabularray}          % Modern tables
\usepackage{charter}             % Professional serif font for print
\usepackage[scaled=0.95]{helvet} % Helvetica for headers
\usepackage[T1]{fontenc}         % Better font encoding
\usepackage{microtype}           % Micro-typography improvements
\usepackage{xcolor}              % Colors

% Tabularray booktabs integration
\UseTblrLibrary{booktabs}

% No page numbers
\pagestyle{empty}
```

---

## Troubleshooting

### Skim not auto-reloading

**Fix**:
```bash
defaults write -app Skim SKAutoReloadFileUpdate -boolean true
```

Or: Skim → Preferences → Sync → "Check for file changes" enabled

### latexmk can't find pdflatex

**Fix**: Use absolute path in `.latexmkrc`:
```perl
$pdflatex = '/Library/TeX/texbin/pdflatex -synctex=1 -interaction=nonstopmode %O %S';
```

### Compilation errors

Check log file:
```bash
tail -50 document.log
```

### Tables misaligned

**Symptom**: "shortcut" text appearing in tables, columns not aligned

**Cause**: Using `X[width,l]` or problematic theme names

**Fix**: Use `p{width}X[l]` pattern (see Table Alignment section)

### Force clean rebuild

```bash
latexmk -C document.tex  # Remove all generated files
latexmk -pdf -pvc document.tex  # Rebuild from scratch
```

---

## Version Control: .gitignore for LaTeX

```gitignore
# LaTeX auxiliary files
*.aux
*.fdb_latexmk
*.fls
*.log
*.out
*.synctex.gz
*.synctex.gz(busy)
*.toc
*.lof
*.lot
*.bbl
*.blg
*.bcf
*.run.xml

# Keep configuration
!.latexmkrc
```

---

## Resources

- **latexmk manual**: `texdoc latexmk` or https://ctan.org/pkg/latexmk
- **Skim homepage**: https://skim-app.sourceforge.io/
- **tabularray manual**: `texdoc tabularray` or https://ctan.org/pkg/tabularray
- **SyncTeX docs**: `texdoc synctex`
- **TeXShop**: Bundled documentation in Help menu

---

## Real-World Example: Ghostty Cheat Sheet

**Files**:
- Source: `/tmp/ghostty-keybindings-fixed.tex`
- Config: `/tmp/.latexmkrc`
- Output: `~/Downloads/ghostty-keybindings-FIXED.pdf`

**Key features**:
- Landscape US Letter (11×8.5")
- 3-column layout with minipages
- 12 tables with perfect vertical alignment
- Charter font (8pt) for readability
- All shortcuts in fixed-width `p{3.8cm}` columns

**Workflow**:
```bash
cd /tmp
latexmk -pdf -pvc ghostty-keybindings-fixed.tex
```

Edit in Helix → Save → See changes in <1 second

---

## Summary

This LaTeX workflow provides:

✅ **Fast**: Compilation typically <1 second
✅ **Precise**: Pixel-perfect table alignment with tabularray
✅ **Interactive**: SyncTeX forward/inverse search
✅ **Future-proof**: All tools actively maintained (2024-2025)
✅ **Standard**: Industry-standard toolchain
✅ **Free**: 100% open-source

**Bottom line**: Professional PDF generation with reliable table alignment, unlike Typst's broken X-column implementation.
