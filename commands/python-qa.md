---
description: "Comprehensive Python quality assurance with multi-layer validation"
argument-hint: "[--critical-only] [--check-only] [--import-focus] [--graph] [--verbose] [target-path]"
allowed-tools: Task, Bash, Glob, Grep, Read, Write
---

# Python QA: Comprehensive Quality Assurance

**Usage Options**:
- `/python-qa` - Full 6-layer quality validation with auto-fixing
- `/python-qa --critical-only` - Focus on production-blocking issues only
- `/python-qa --check-only` - Dry-run analysis without making changes
- `/python-qa --import-focus` - Specialized import health and circular dependency analysis
- `/python-qa --graph` - Generate import dependency visualization
- `/python-qa --verbose` - Detailed layer-by-layer analysis output
- `/python-qa [target-path]` - Quality analysis for specific directory or module

## Command Process

**Workflow**: Multi-layer static analysis → Auto-fixing → Import validation → Architecture verification → Comprehensive reporting

### Integration Patterns

**Comprehensive Quality Assurance**:
- Replaces separate ruff-fix and import-check workflows
- Unified quality reporting with actionable recommendations
- CI/CD integration guidance with quality gates
- Architecture-aware validation with dependency analysis

### Agent Deployment

**Specialized Agent**: Uses `python-qa` agent for comprehensive multi-tool Python quality assurance with 6-layer validation pipeline and intelligent error resolution.