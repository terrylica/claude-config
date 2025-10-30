______________________________________________________________________

## name: latex-tables description: Create modern LaTeX tables with tabularray package for fixed-width columns, proper alignment, and clean syntax. Use when creating tables, formatting table layouts, working with column widths, or migrating from old tabular/tabularx packages. allowed-tools: Read, Edit, Bash

# LaTeX Tables with tabularray Skill

## Quick Reference

**When to use this skill:**

- Creating tables with fixed-width columns
- Formatting complex table layouts
- Need precise column alignment
- Migrating from tabular/tabularx/longtable/booktabs
- Troubleshooting table overflow issues

## Why tabularray?

**Modern LaTeX3 Package (replaces old solutions):**

- ✅ Fixed-width columns with proper alignment
- ✅ Clean, consistent syntax
- ✅ Replaces: `tabular`, `tabularx`, `longtable`, `booktabs`
- ✅ Better performance than legacy packages
- ✅ Part of TeX Live 2025

______________________________________________________________________

## Installation

```bash
# Check if installed
kpsewhich tabularray.sty

# If not found, install:
sudo tlmgr install tabularray
```

## Basic Usage

### Document Setup

```latex
\documentclass{article}
\usepackage{tabularray}  % Modern table package

\begin{document}
% Your tables here
\end{document}
```

______________________________________________________________________

## Common Table Patterns

### 1. Simple Table with Lines

```latex
\begin{table}[h]
  \centering
  \begin{tblr}{
    colspec = {ccc},    % 3 centered columns
    hlines,              % Horizontal lines
    vlines               % Vertical lines
  }
    Header 1 & Header 2 & Header 3 \\
    Data 1   & Data 2   & Data 3   \\
    More 1   & More 2   & More 3   \\
  \end{tblr}
  \caption{My table}
\end{table}
```

### 2. Fixed-Width Columns

```latex
\begin{table}[h]
  \centering
  \begin{tblr}{
    colspec = {Q[2cm] Q[4cm] Q[2cm]},  % Fixed widths: 2cm, 4cm, 2cm
    hlines, vlines
  }
    Short & This is longer text that wraps & Data \\
    A     & More wrapping content here     & B    \\
  \end{tblr}
\end{table}
```

### 3. Mixed Column Types

```latex
\begin{tblr}{
  colspec = {l Q[3cm,c] r},  % Left, centered fixed-width, right
  hlines
}
  Left-aligned & Centered in 3cm & Right-aligned \\
  Text         & More text       & 123           \\
\end{tblr}
```

### 4. No Lines (Minimal Style)

```latex
\begin{tblr}{
  colspec = {lcc},
  row{1} = {font=\bfseries}  % Bold first row (header)
}
  Name     & Age & City    \\
  Alice    & 25  & Boston  \\
  Bob      & 30  & Seattle \\
\end{tblr}
```

### 5. Colored Rows/Columns

```latex
\usepackage{xcolor}

\begin{tblr}{
  colspec = {ccc},
  row{1} = {bg=blue!20},      % Light blue header
  row{even} = {bg=gray!10}    % Alternate row colors
}
  Header 1 & Header 2 & Header 3 \\
  Data 1   & Data 2   & Data 3   \\
  Data 4   & Data 5   & Data 6   \\
\end{tblr}
```

______________________________________________________________________

## Column Specification (colspec)

### Alignment Options

| Code       | Meaning                          |
| ---------- | -------------------------------- |
| `l`        | Left-aligned                     |
| `c`        | Centered                         |
| `r`        | Right-aligned                    |
| `X`        | Flexible width (expands to fill) |
| `Q[width]` | Fixed width with wrapping        |

### Examples

```latex
% 3 centered columns
colspec = {ccc}

% Left, center, right
colspec = {lcr}

% Fixed widths
colspec = {Q[2cm] Q[3cm] Q[1.5cm]}

% Mixed: fixed left, flexible middle, fixed right
colspec = {Q[2cm] X Q[2cm]}

% With alignment in fixed-width
colspec = {Q[2cm,l] Q[3cm,c] Q[2cm,r]}
```

______________________________________________________________________

## Lines and Borders

### All Lines

```latex
\begin{tblr}{
  colspec = {ccc},
  hlines,              % All horizontal lines
  vlines               % All vertical lines
}
```

### Selective Lines

```latex
\begin{tblr}{
  colspec = {ccc},
  hline{1,2,Z} = {solid},  % Top, after header, bottom
  vline{2} = {dashed}      % Dashed line after column 1
}
```

### Thick Lines

```latex
\begin{tblr}{
  colspec = {ccc},
  hline{1,Z} = {2pt},     % Thick top/bottom
  hline{2} = {1pt}         % Thinner after header
}
```

______________________________________________________________________

## Multi-Page Tables

For tables spanning multiple pages:

```latex
\begin{longtblr}[
  caption = {Long table example},
]{
  colspec = {lcr},
  hlines,
  row{1} = {font=\bfseries}  % Header row
}
  Header 1 & Header 2 & Header 3 \\
  % ... many rows ...
\end{longtblr}
```

______________________________________________________________________

## Common Issues

### Issue: Table Too Wide

**Solution 1: Fixed-width columns**

```latex
% Instead of:
colspec = {ccc}

% Use fixed widths that fit:
colspec = {Q[2cm] Q[3cm] Q[2cm]}
```

**Solution 2: Flexible columns**

```latex
colspec = {XXX}  % All columns expand equally
```

**Solution 3: Scale table**

```latex
\usepackage{graphicx}

\begin{table}[h]
  \resizebox{\textwidth}{!}{%
    \begin{tblr}{...}
      % table content
    \end{tblr}
  }
\end{table}
```

### Issue: Text Not Wrapping

**Problem:** Using `c` or `l` or `r` doesn't wrap

**Solution:** Use `Q[width]` for wrapping

```latex
% ❌ Won't wrap:
colspec = {ccc}

% ✅ Will wrap:
colspec = {Q[3cm] Q[4cm] Q[3cm]}
```

### Issue: Alignment in Fixed-Width Column

```latex
% Left-aligned in fixed width
Q[3cm, l]

% Centered in fixed width
Q[3cm, c]

% Right-aligned in fixed width
Q[3cm, r]
```

______________________________________________________________________

## Migration from Old Packages

### From tabular

```latex
% Old:
\begin{tabular}{|c|c|c|}
  \hline
  A & B & C \\
  \hline
\end{tabular}

% New:
\begin{tblr}{
  colspec = {ccc},
  hlines, vlines
}
  A & B & C \\
\end{tblr}
```

### From tabularx

```latex
% Old:
\begin{tabularx}{\textwidth}{|l|X|r|}
  \hline
  Left & Middle & Right \\
  \hline
\end{tabularx}

% New:
\begin{tblr}{
  width = \textwidth,
  colspec = {lXr},
  hlines
}
  Left & Middle & Right \\
\end{tblr}
```

______________________________________________________________________

## Best Practices

1. **Use Q[width] for fixed columns** instead of p{width}
1. **Specify widths explicitly** when text might overflow
1. **Use X for flexible columns** that should expand
1. **Style headers with row{1}** instead of manual formatting
1. **Use colspec** for column properties, not inline commands
1. **Check package version**: `kpsewhich tabularray.sty` (should be recent)

______________________________________________________________________

## Quick Reference Card

```latex
% Minimal table
\begin{tblr}{colspec={ccc}}
  A & B & C \\
\end{tblr}

% With all lines
\begin{tblr}{colspec={ccc}, hlines, vlines}
  A & B & C \\
\end{tblr}

% Fixed widths
\begin{tblr}{colspec={Q[2cm] Q[3cm] Q[2cm]}, hlines}
  A & B & C \\
\end{tblr}

% Bold header
\begin{tblr}{
  colspec={ccc},
  row{1}={font=\bfseries}
}
  Header & Header & Header \\
  Data   & Data   & Data   \\
\end{tblr}
```

______________________________________________________________________

## See Also

- **Setup**: Use `latex/setup` skill for installing tabularray package
- **Build**: Use `latex/build` skill for compilation workflows
- **Official Docs**: Run `texdoc tabularray` for complete package documentation
