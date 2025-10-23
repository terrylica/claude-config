---
name: LaTeX Build Automation
description: Build and compile LaTeX documents using latexmk with live preview, dependency tracking, and automatic rebuilds. Use when setting up build workflows, enabling live preview, troubleshooting compilation, or automating multi-file projects.
---

# LaTeX Build Automation Skill

## Quick Reference

**When to use this skill:**

- Compiling LaTeX documents
- Setting up live preview with auto-rebuild
- Managing multi-file projects
- Troubleshooting build failures
- Cleaning build artifacts
- Automating compilation workflows

## Why latexmk?

**Industry Standard Build Tool:**

- ✅ Auto-detects dependencies (bibliography, index, etc.)
- ✅ Runs correct number of times (handles cross-references)
- ✅ Live preview mode watches for file changes
- ✅ Works with Skim for SyncTeX auto-reload
- ✅ Bundled with MacTeX (no separate install needed)

---

## Basic Usage

### One-Time Build

```bash
# Compile to PDF
latexmk -pdf document.tex

# Result: document.pdf created
```

### Live Preview (Watch Mode)

```bash
# Continuous preview with auto-rebuild
latexmk -pvc -pdf document.tex

# What happens:
# - Compiles document initially
# - Watches for file changes
# - Auto-recompiles when files change
# - Auto-reloads PDF in Skim viewer
```

**Stop watching:** Press `Ctrl+C`

---

## Common Commands

### Build Once

```bash
# PDF output
latexmk -pdf document.tex

# DVI output
latexmk -dvi document.tex

# PostScript output
latexmk -ps document.tex
```

### Clean Build Artifacts

```bash
# Remove auxiliary files (.aux, .log, .synctex.gz, etc.)
latexmk -c

# Also remove PDF output
latexmk -C

# Then rebuild from scratch
latexmk -pdf document.tex
```

### Force Rebuild

```bash
# Force rerun of all tools (bibliography, index, etc.)
latexmk -gg -pdf document.tex
```

### Build with Options

```bash
# Enable SyncTeX (for Skim integration)
latexmk -pdf -synctex=1 document.tex

# Use LuaLaTeX instead of pdfLaTeX
latexmk -pdflua document.tex

# Use XeLaTeX
latexmk -pdfxe document.tex

# Verbose output for debugging
latexmk -pdf -verbose document.tex
```

---

## Live Preview Workflow

### Standard Setup

```bash
# Start live preview
latexmk -pvc -pdf document.tex

# In another terminal or editor:
# Edit your .tex files
# latexmk automatically detects changes and recompiles
# Skim automatically reloads the PDF
```

### With Custom Viewer

```bash
# Use specific PDF viewer
latexmk -pvc -pdf -view=pdf document.tex

# Disable viewer opening
latexmk -pvc -pdf -view=none document.tex
```

---

## Multi-File Projects

latexmk automatically tracks dependencies!

### Project Structure

```
my-project/
├── main.tex              # Root document
├── chapters/
│   ├── intro.tex
│   ├── methodology.tex
│   └── results.tex
├── figures/
│   └── diagram.pdf
└── bibliography.bib
```

### Root Document (main.tex)

```latex
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\input{chapters/intro}
\input{chapters/methodology}
\input{chapters/results}

\bibliographystyle{plain}
\bibliography{bibliography}

\end{document}
```

### Compile Root

```bash
# latexmk watches ALL included files
latexmk -pvc -pdf main.tex

# Edit any chapter → automatic rebuild
# Update bibliography.bib → automatic rebuild
# Change figure → automatic rebuild
```

---

## Makefile Integration

### Basic Makefile

```makefile
.PHONY: pdf watch clean

pdf:
	latexmk -pdf main.tex

watch:
	latexmk -pvc -pdf main.tex

clean:
	latexmk -c
	rm -f main.pdf

distclean:
	latexmk -C
```

### Usage

```bash
make pdf      # Build once
make watch    # Live preview
make clean    # Remove artifacts
```

---

## Configuration (.latexmkrc)

Create `.latexmkrc` in project directory for custom settings:

### Example Configuration

```perl
# Use pdflatex by default
$pdf_mode = 1;

# Use lualatex instead
# $pdf_mode = 4;

# Enable SyncTeX
$pdflatex = 'pdflatex -synctex=1 -interaction=nonstopmode %O %S';

# Set PDF viewer (macOS Skim)
$pdf_previewer = 'open -a Skim';

# Continuous mode delay (seconds)
$sleep_time = 1;

# Clean these extensions
@generated_exts = (@generated_exts, 'synctex.gz');
```

Place in project root, then:

```bash
latexmk -pvc main.tex
# Uses settings from .latexmkrc
```

---

## Troubleshooting

### Issue: latexmk Not Found

```bash
# Check installation
which latexmk
# Should show: /Library/TeX/texbin/latexmk

# If not found, ensure MacTeX installed
brew install --cask mactex

# Or add to PATH
export PATH="/Library/TeX/texbin:$PATH"
```

### Issue: PDF Not Auto-Reloading in Skim

**Check Skim preferences:**

1. Skim → Preferences → Sync
2. Check "Check for file changes"
3. Check "Reload automatically"

**Verify SyncTeX enabled:**

```bash
latexmk -pdf -synctex=1 document.tex
# Should create document.synctex.gz
```

### Issue: Build Hangs on Error

```bash
# Use non-interactive mode
latexmk -pdf -interaction=nonstopmode document.tex

# Or in .latexmkrc:
$pdflatex = 'pdflatex -interaction=nonstopmode %O %S';
```

### Issue: Bibliography Not Updating

```bash
# Force rebuild of all dependencies
latexmk -gg -pdf document.tex

# Or clean and rebuild
latexmk -C && latexmk -pdf document.tex
```

### Issue: Compilation Errors Not Showing

```bash
# Use verbose mode
latexmk -pdf -verbose document.tex

# Check log file
less document.log
```

### Issue: Stale Auxiliary Files

```bash
# Clean all build artifacts
latexmk -C

# Rebuild from scratch
latexmk -pdf document.tex
```

---

## Advanced Patterns

### Parallel Builds (Multiple Documents)

```bash
# Build all .tex files in directory
latexmk -pdf *.tex

# Watch multiple documents
latexmk -pvc -pdf doc1.tex doc2.tex doc3.tex
```

### Custom Build Script

```bash
#!/bin/bash
# build.sh - Custom LaTeX build script

set -e  # Exit on error

echo "Cleaning old build..."
latexmk -C

echo "Building document..."
latexmk -pdf -synctex=1 main.tex

echo "Build complete: main.pdf"
ls -lh main.pdf
```

### CI/CD Integration

```bash
# Headless build for CI (no viewer)
latexmk -pdf -interaction=nonstopmode -view=none document.tex

# Check exit code
if [ $? -eq 0 ]; then
  echo "Build successful"
else
  echo "Build failed"
  exit 1
fi
```

---

## Build Checklist

- [ ] Verify latexmk installed: `which latexmk`
- [ ] Test basic build: `latexmk -pdf document.tex`
- [ ] Enable SyncTeX: Add `-synctex=1` flag
- [ ] Test live preview: `latexmk -pvc -pdf document.tex`
- [ ] Configure Skim for auto-reload
- [ ] Create Makefile for common tasks (optional)
- [ ] Create .latexmkrc for project-specific settings (optional)
- [ ] Test clean: `latexmk -c` removes artifacts

---

## Quick Reference Card

```bash
# Build once
latexmk -pdf document.tex

# Live preview (watch mode)
latexmk -pvc -pdf document.tex

# Build with SyncTeX
latexmk -pdf -synctex=1 document.tex

# Clean artifacts
latexmk -c              # Keep PDF
latexmk -C              # Remove PDF too

# Force rebuild
latexmk -gg -pdf document.tex

# Non-interactive (for CI)
latexmk -pdf -interaction=nonstopmode document.tex
```

---

## See Also

- **Setup**: Use `latex/setup` skill for installing LaTeX and configuring environment
- **Tables**: Use `latex/tables` skill for creating tables with tabularray
- **Official Docs**: Run `man latexmk` or `latexmk -help` for complete reference
