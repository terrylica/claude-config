# Tool Organization Standards

**Version**: 1.0.0
**Status**: Proposed
**Created**: 2025-10-23
**Purpose**: Define clear taxonomy and organization rules for tools, scripts, and utilities in the workspace

______________________________________________________________________

## Overview

This document establishes the **single source of truth** for organizing executable code, tools, and utilities in the `~/.claude/` workspace. Following these standards prevents organizational drift and ensures maintainability.

______________________________________________________________________

## Directory Taxonomy

### Decision Tree: Where Does My Script Go?

```
Is it a functional script?
├─ Is it an automation hook (runs on events)?
│  └─ → /automation/{system-name}/
│      Examples: CNS hooks, Prettier formatters, git hooks
│
├─ Is it a configuration utility (one-time setup)?
│  └─ → /tools/config/
│      Examples: disable-pyright.sh, setup-env.sh
│
├─ Is it a standalone tool with documentation?
│  └─ → /tools/{tool-name}/
│      Structure: README.md, tool-manifest.yaml, implementation
│      Examples: doc-intelligence, git-cliff, gfm-link-checker
│
├─ Is it an executable wrapper/entry point?
│  └─ → /tools/bin/
│      Purpose: Thin wrappers that delegate to implementations
│      Examples: install-all-tools.sh, workspace-health-check.sh
│
└─ Is it a minimal system integration script?
   └─ → /bin/
       Warning: Avoid creating new scripts here
       Use only for system-critical integrations
       Examples: cns-notify, gfm-check-direct
```

______________________________________________________________________

## Directory Purposes

### `/tools/` - Development Tools Hub

**Purpose**: Self-contained tools with full documentation

**Structure**:

```
/tools/
├── bin/                          # Executable entry points
│   ├── install-all-tools.sh      # Tool installation
│   ├── workspace-health-check.sh # Validation runner
│   └── README.md                 # Explains bin/ purpose
│
├── config/                       # Configuration utilities
│   ├── disable-pyright.sh
│   └── README.md
│
├── lib/                          # Shared libraries (optional)
│   ├── common.sh                 # Shell function library
│   ├── validators.py             # Python utilities
│   └── README.md
│
└── {tool-name}/                  # Individual tools
    ├── README.md                 # REQUIRED
    ├── tool-manifest.yaml        # REQUIRED
    ├── {implementation files}    # .py, .sh, etc.
    ├── config/                   # Tool-specific config (optional)
    └── tests/                    # Test suite (optional)
```

**Requirements for Tool Directories**:

1. **README.md** (Required) - Must include:

   - Purpose (one sentence)
   - Usage instructions
   - Dependencies
   - Installation steps
   - Maintenance status

1. **tool-manifest.yaml** (Required) - Machine-readable metadata:

   ```yaml
   name: "tool-name"
   version: "1.0.0"
   purpose: "Brief description"
   language: "python|bash|rust|..."
   dependencies: []
   executable: "path/to/main/script"
   maintainer: "github-handle or team"
   last_verified: "2025-10-23"
   ```

1. **Implementation** - Actual code files

**Examples**:

- `/tools/doc-intelligence/` - Document analysis tool
- `/tools/git-cliff/` - Changelog generator
- `/tools/notifications/` - Notification utilities

______________________________________________________________________

### `/automation/` - Event-Driven Automation

**Purpose**: Scripts triggered by hooks or automated processes

**Structure**:

```
/automation/
├── cns/                          # Claude Notification System
│   ├── cns_hook_entry.sh         # Main hook entry point
│   ├── config/                   # CNS configuration
│   ├── tests/                    # Test suite
│   └── README.md
│
├── prettier/                     # Markdown formatting
│   ├── format-markdown.sh        # Stop hook
│   └── README.md
│
└── hooks/                        # Future hook implementations
    └── README.md
```

**Characteristics**:

- Triggered by `settings.json` hooks
- Event-driven, not manually invoked
- Must be reliable (used in automation)
- Should have tests

**Examples**:

- `/automation/cns/cns_hook_entry.sh` - Runs on Stop hook
- `/automation/prettier/format-markdown.sh` - Runs on Stop hook

______________________________________________________________________

### `/bin/` - Minimal System Integration

**Purpose**: Minimal scripts for system-critical integration
**Policy**: **Avoid creating new scripts here** - prefer `/tools/bin/`

**Structure**:

```
/bin/
├── cns-notify                    # CNS notification wrapper
├── gfm-check-direct              # Direct GFM checker invocation
└── README.md
```

**When to Use**:

- System-level integration only
- Scripts that must be in PATH
- Symlinked to `~/.local/bin/`

**Examples**:

- Notification system wrappers
- Shell function loaders

______________________________________________________________________

## Script Standards

### Naming Conventions

| Type           | Convention                                   | Example                    |
| -------------- | -------------------------------------------- | -------------------------- |
| Directories    | `kebab-case`                                 | `/tools/doc-intelligence/` |
| Shell scripts  | `kebab-case.sh`                              | `install-all-tools.sh`     |
| Python scripts | `kebab-case.py`                              | `workspace-cleanup.py`     |
| Documentation  | `SCREAMING_SNAKE_CASE.md` or `kebab-case.md` | `TOOL_ORGANIZATION.md`     |
| Specifications | `kebab-case.yaml`                            | `tool-manifest.yaml`       |

### Script Header Template

Every script should start with a standard header:

**Shell Script**:

```bash
#!/usr/bin/env bash
#
# Name: script-name.sh
# Purpose: Brief one-line description
# Usage: script-name.sh [OPTIONS]
# Dependencies: list, of, dependencies
# Maintainer: github-handle
# Last Updated: 2025-10-23
# Version: 1.0.0
#

set -euo pipefail # Strict mode
```

**Python Script**:

```python
#!/usr/bin/env python3
"""
Name: script-name.py
Purpose: Brief one-line description
Usage: python script-name.py [OPTIONS]
Dependencies: See requirements.txt or pyproject.toml
Maintainer: github-handle
Last Updated: 2025-10-23
Version: 1.0.0
"""

import sys
from pathlib import Path
```

### File Permissions

| Type                | Permissions         | Rationale                         |
| ------------------- | ------------------- | --------------------------------- |
| Executable scripts  | `755` (`rwxr-xr-x`) | Owner can modify, all can execute |
| Library scripts     | `644` (`rw-r--r--`) | Sourced, not executed directly    |
| Configuration files | `644` (`rw-r--r--`) | Read-only for non-owner           |
| Secrets/credentials | `600` (`rw-------`) | Owner only                        |

Set permissions:

```bash
chmod 755 executable-script.sh
chmod 644 config-file.yaml
chmod 600 secret-file.env
```

______________________________________________________________________

## Tool Development Workflow

### Creating a New Tool

1. **Choose Location** (use decision tree above)

1. **Create Directory Structure**:

   ```bash
   mkdir -p /tools/new-tool/{config,tests}
   ```

1. **Create Required Files**:

   ```bash
   touch /tools/new-tool/README.md
   touch /tools/new-tool/tool-manifest.yaml
   touch /tools/new-tool/new-tool.sh  # or .py
   ```

1. **Populate README.md**:

   ````markdown
   # New Tool

   **Purpose**: One-sentence description

   ## Usage

   ```bash
   ./new-tool.sh [OPTIONS]
   ```
   ````

   ## Dependencies

   - List dependencies here

   ## Installation

   Steps to install/setup

   ## Maintenance

   Status: Active | Deprecated | Experimental
   Last Updated: YYYY-MM-DD

   ```

   ```

1. **Populate tool-manifest.yaml**:

   ```yaml
   name: "new-tool"
   version: "1.0.0"
   purpose: "Brief description"
   language: "bash"
   dependencies: []
   executable: "new-tool.sh"
   maintainer: "your-github-handle"
   last_verified: "2025-10-23"
   ```

1. **Implement Tool** with standard header

1. **Add to Tool Registry**: Update `/tools/tool-manifest.yaml` (global registry)

1. **Test**: Create tests in `/tools/new-tool/tests/`

1. **Document**: Update `/docs/INDEX.md` if user-facing

______________________________________________________________________

## File Organization Anti-Patterns

### DON'T Do This

❌ **Root-level scripts**:

```
/install-all-tools        # Bad: clutters root
/some-utility.sh          # Bad: unclear purpose
```

✅ **Proper location**:

```
/tools/bin/install-all-tools.sh  # Good: clear taxonomy
/tools/config/some-utility.sh    # Good: purpose clear
```

______________________________________________________________________

❌ **Backup files in production**:

```
/tools/script.sh.backup    # Bad: use git history
/automation/hook.sh.old    # Bad: confusing
```

✅ **Use git history**:

```bash
git log script.sh          # View history
git show HEAD~1:script.sh  # View previous version
```

______________________________________________________________________

❌ **Scripts without documentation**:

```
/tools/mystery-tool/
└── run.sh                 # Bad: no README, no manifest
```

✅ **Documented tools**:

```
/tools/mystery-tool/
├── README.md              # Good: explains purpose
├── tool-manifest.yaml     # Good: metadata
└── run.sh                 # Implementation
```

______________________________________________________________________

❌ **Virtual environments in source tree**:

```
/tools/some-tool/.venv     # Bad: per user standards
```

✅ **Use `uv` per standards**:

```bash
uv run --active python -m some_tool
```

______________________________________________________________________

## Tool Discovery & Registry

### Global Tool Manifest

**Location**: `/tools/tool-manifest.yaml`

**Purpose**: Machine-readable registry of ALL tools in workspace

**Format**:

```yaml
tools:
  - name: "doc-intelligence"
    location: "/tools/doc-intelligence"
    purpose: "Document analysis and processing"
    language: "python"
    executable: "demo.py"
    version: "1.0.0"
    maintainer: "workspace"
    last_verified: "2025-10-23"
    status: "active"

  - name: "git-cliff"
    location: "/tools/git-cliff"
    purpose: "Changelog generation"
    language: "rust"
    executable: "git-cliff"
    version: "2.0.0"
    maintainer: "external"
    last_verified: "2025-10-23"
    status: "active"
```

**Maintenance**:

- Update when adding new tools
- Mark deprecated tools with `status: "deprecated"`
- Record last verification date
- Used by installation scripts

______________________________________________________________________

## Integration with User Standards

This taxonomy aligns with user's stated preferences in `/CLAUDE.md`:

1. **Universal Tool Access**: Executables symlinked to `~/.local/bin/`
1. **Python Management**: Use `uv`, not pip/conda/venv
1. **PATH Standard**: Only `~/.local/bin` in PATH
1. **Working Directory Preservation**: Scripts use absolute paths, avoid `cd`

**Example Integration**:

```bash
# Install tool to ~/.local/bin/
ln -sf /Users/terryli/.claude/tools/bin/install-all-tools.sh \
       ~/.local/bin/install-all-tools

# Run with preserved working directory
/Users/terryli/.claude/tools/bin/some-tool.sh --work-dir "$PWD"
```

______________________________________________________________________

## Validation & Health Checks

### Automated Validation

Create `/tools/bin/workspace-health-check.sh` to validate:

1. **Tool Manifest Completeness**:

   - Every tool in `/tools/` has `README.md`
   - Every tool in `/tools/` has `tool-manifest.yaml`
   - Global manifest up to date

1. **Executable Permissions**:

   - Scripts have correct permissions (755 for executable)
   - No scripts in wrong locations

1. **Symlink Integrity**:

   - All symlinks in `~/.local/bin/` valid
   - Point to existing files

1. **Documentation Links**:

   - All markdown links valid (via `gfm-check`)

1. **No Anti-Patterns**:

   - No backup files in production directories
   - No root-level scripts
   - No `.venv` in tool directories

______________________________________________________________________

## Migration Path

For existing workspace, follow phased migration in `/specifications/reorg-move-map.yaml`:

1. **Phase 1**: Create new directory structure (`/tools/bin/`, `/tools/config/`)
1. **Phase 2**: Move root-level scripts to appropriate locations
1. **Phase 3**: Create manifests for existing tools
1. **Phase 4**: Update documentation and references
1. **Phase 5**: Validate and test

See `/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md` for detailed migration guide.

______________________________________________________________________

## Quick Reference

### Where Should I Put...?

| Type                  | Location                | Example                    |
| --------------------- | ----------------------- | -------------------------- |
| Installation script   | `/tools/bin/`           | `install-all-tools.sh`     |
| Configuration utility | `/tools/config/`        | `disable-pyright.sh`       |
| Automation hook       | `/automation/{system}/` | `cns_hook_entry.sh`        |
| Standalone tool       | `/tools/{tool-name}/`   | `/tools/doc-intelligence/` |
| Shared library        | `/tools/lib/`           | `common.sh`                |
| System integration    | `/bin/` (avoid)         | `cns-notify`               |

### Required Files for Tools

- ✅ `README.md` - Always required
- ✅ `tool-manifest.yaml` - Always required
- ⚠️ `tests/` - Strongly recommended
- ⚠️ `config/` - If tool has configuration

______________________________________________________________________

## Related Documentation

- [Workspace Reorganization Specification](/specifications/workspace-reorganization.yaml) - Target architecture
- [Reorganization Move Map](/specifications/reorg-move-map.yaml) - File migration plan
- [Architecture Overview](/docs/architecture/ARCHITECTURE.md) - Overall workspace design
- [Artifact Retention Policy](/docs/maintenance/ARTIFACT_RETENTION.md) - Runtime artifact management

______________________________________________________________________

**Status**: Proposed standard for workspace reorganization
**Next Steps**: Review and implement via phased migration
**Questions**: Document in `/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md`
