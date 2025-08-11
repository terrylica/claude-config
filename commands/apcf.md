---
description: "Generate audit-proof commit messages for SR&ED compliance with automatic git hygiene (uses sub-tasks)"
argument-hint: "[scope] [--extract-evidence] [--compliance-check] [--full-workflow] [--clean-untracked] [--update-gitignore]"
allowed-tools: Task
---

# APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

**Sub-Task Delegation**: This command delegates all operations to the specialized `apcf-agent` to conserve main session tokens.

**Usage Options**:
- `/apcf` - Full APCF workflow with SR&ED evidence extraction and compliance validation
- `/apcf [scope]` - Target specific files or directories for commit analysis
- `/apcf --extract-evidence` - Use SR&ED evidence extractor for commit analysis
- `/apcf --compliance-check` - Run compliance audit on proposed commit messages
- `/apcf --full-workflow` - Complete SR&ED workflow with evidence extraction and compliance validation
- `/apcf --clean-untracked` - Automatic git hygiene: analyze untracked files and recommend .gitignore updates
- `/apcf --update-gitignore` - Update .gitignore based on untracked file analysis and commit the changes

All APCF operations will be handled by the specialized agent with full SR&ED compliance, git hygiene management, and audit-proof commit generation capabilities.