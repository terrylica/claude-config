# Development Toolchain

Complete tool preferences and package standards for the workspace.

---

## Core Development Stack

### Python Stack
- **Management**: `uv` (package management, virtual environments)
- **Execution**: `uv run --active python -m <module>` (ALWAYS use this format)
- **Build Backend**: `hatchling`
- **Rust Integration**: `maturin`
- **Version**: 3.12+

**Avoid**: pip, conda, setuptools, poetry, standalone script execution

**Examples**:
```bash
# Install dependencies
uv add httpx platformdirs orjson

# Run Python module
uv run --active python -m mypackage.module

# Development install
uv pip install -e .
```

---

### Rust Stack
- **Build**: `cargo build --release`
- **Test**: `cargo nextest run`
- **Security**: `cargo deny check`
- **Coexistence**: Works alongside Python via maturin

**Mandatory Quality Enforcement**:
- All commits blocked unless passing: `cargo fmt --check`, `cargo clippy -- -D warnings`, `cargo test`
- Pre-commit hooks enabled
- GitHub Actions validation

**Setup**:
```bash
chmod +x .git/hooks/pre-commit && pre-commit install
```

---

### Container Runtime
- **Runtime**: Colima (lightweight Docker Desktop replacement)
- **CLI**: Docker CLI (Homebrew)
- **Removed**: Docker Desktop (31 GB bloat)

---

## Package Preferences

### Python Packages
**Prefer**:
- `httpx` over `requests`
- `platformdirs` over hardcoded paths
- `orjson` over `json`
- `ciso8601` over `dateutil`, `arrow`, `maya`

### Claude Code Tools
**Prefer**: Built-in tools over MCP
- `Read`, `LS`, `Glob`, `Grep`

---

## Specialized Tools

### Text Editor
- **Helix** (`hx`) - https://github.com/helix-editor/helix
- Modal editor with built-in LSP
- Tree-sitter syntax highlighting

### Code Analysis
- **Semgrep** - Pattern-based code analysis
- **ast-grep** - AST-based code search
- **ShellCheck** - Shell script linting

### GPU Computing
- `tensorflow-metal` (macOS)
- `jax`
- `torch`
- `cupy`

---

## Document Processing

### PDF Processing
**Input (born-digital PDFs)**:
- **Primary**: `mupdf-tools` (`mutool draw -F html`) - Clean HTML/block grouping
- **Alternative**: Poppler `pdftohtml -xml` - Exact coordinates, complex column layouts

**Generation**:
- **LaTeX** with `tabularray` package
- See: [`latex-workflow.md`](latex-workflow.md)

---

## Finance & Trading Tools

### Backtesting
- **Allowed**: `backtesting.py` ONLY
- **Allowed**: `rangebar` crate (Rust)
- **Prohibited**: bt, vectorbt, mlfinlab, commercial libraries

### Indicators
**Pattern**: Reference talipp (github.com/nardew/talipp) for O(1) incremental updates when rolling metrics required

---

## Data Storage

### File Formats
- **Tabular Data**: Parquet with zstd-9 compression (prefer over CSV)
- **Configuration**: YAML, TOML
- **Machine-Readable Specs**: OpenAPI 3.1.1, JSON Schema

---

## Documentation Standards

### Code Documentation
**All examples** must use `uv run --active python -m` format, never standalone execution

**Good**:
```bash
uv run --active python -m mypackage.cli --help
```

**Bad**:
```bash
python mypackage/cli.py --help
```

### API Documentation
**Pattern**: Pydantic v2 models + Rich docstrings
**Specification**: [`specifications/pydantic-api-documentation-standard.yaml`](../../specifications/pydantic-api-documentation-standard.yaml)
