---
description: "Execute comprehensive module housekeeping and refactoring"
argument-hint: "[workspace_path] | --audit-only [path] | --modularize [script_file] | --dry-run [path]"
allowed-tools: Task, Bash, Glob, Grep, Read, Write
---

# MHR: Module Housekeep Refactoring Command

**Usage Options**:
- `/mhr [workspace_path]` - Full MHR analysis and refactoring of specified path
- `/mhr --audit-only [path]` - Analysis and recommendations without execution  
- `/mhr --modularize [script_file]` - Focus on single large file modularization
- `/mhr --dry-run [path]` - Preview all planned changes without execution

## Command Process

**Workflow**: Identify technical debt → Audit comprehensively → Plan modularization → Execute with safety → Verify alignment

### Integration Patterns

**Technical Debt Management**: Systematic workspace analysis with strategic modularization, safety-first execution, and comprehensive rollback preparation.  

## Agent Deployment

**Usage**: Request "MHR" when workspace shows technical debt accumulation, configuration drift, or maintainability concerns requiring systematic housekeeping and strategic refactoring.