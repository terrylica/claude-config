# Ruff Auto-Fix Command

Automatically fix Python code issues using `ruff` with comprehensive error resolution.

## Usage
```
/ruff-fix
```

## Process
1. **Auto-fix everything possible**: `ruff check --fix .`
2. **Check critical issues**: `ruff check --select="F,E9,E4,E7,B"`
3. **Resolve remaining issues**: Analyze and fix any remaining problems

## Error Categories Checked
- **F**: Pyflakes (undefined names, unused imports, etc.)
- **E9**: Runtime errors (syntax errors, indentation)
- **E4**: Import errors (import formatting)
- **E7**: Statement errors (statement formatting)
- **B**: Flake8-bugbear (likely bugs and design problems)

## Implementation
The command will:
1. **Ensure `ruff` is current**: `uv tool install ruff` (installs or updates to latest version)
2. **Run automatic fixes**: `ruff check --fix .`
3. **Check critical issues**: `ruff check --select="F,E9,E4,E7,B"`
4. **Resolve remaining problems**: Analyze and fix any issues that auto-fix couldn't handle
5. **Show summary**: Report all changes made

## Tool Management
Always ensures latest `ruff` version via `uv`:
- **Auto-install**: If not present, installs automatically
- **Auto-update**: If outdated, updates to latest version
- **Seamless**: No user intervention required

This ensures comprehensive Python code quality with the latest `ruff` features and minimal manual intervention.