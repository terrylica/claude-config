---
description: "Execute comprehensive workspace refactoring and technical debt reduction"
argument-hint: "[workspace_path] | --audit-only [path] | --modularize [script_file] | --dry-run [path]"
allowed-tools: Task, Bash, Glob, Grep, Read, Write
---

# Workspace Refactor: Comprehensive Technical Debt Reduction

**Usage Options**:

- `/workspace-refactor [workspace_path]` - Full workspace analysis and refactoring of specified path
- `/workspace-refactor --audit-only [path]` - Analysis and recommendations without execution
- `/workspace-refactor --modularize [script_file]` - Focus on single large file modularization
- `/workspace-refactor --dry-run [path]` - Preview all planned changes without execution

## Command Process

**Workflow**: Identify technical debt → Audit comprehensively → Plan modularization → Execute with safety → Verify alignment

### Integration Patterns

**Technical Debt Management**: Systematic workspace analysis with strategic modularization, safety-first execution, and comprehensive rollback preparation.

## Agent Deployment

**Usage**: Request "workspace-refactor" when workspace shows technical debt accumulation, configuration drift, or maintainability concerns requiring systematic refactoring and strategic modularization.
