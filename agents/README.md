# Agents Directory

**Purpose**: Custom agent configurations and specialized sub-agents for Claude Code

## Available Agents

### [Research Scout](./research-scout.md) (`research-scout`)
Explores research directions from seed keywords. Use when you need systematic exploration of topics.

### [Compliance Auditor](./compliance-auditor.md) (`compliance-auditor`)
Specialized agent for compliance auditing and regulatory analysis.

### [SR&ED Evidence Extractor](./sred-evidence-extractor.md) (`sred-evidence-extractor`)
Extracts and documents Scientific Research and Experimental Development evidence from codebases.

### [Simple Helper](./simple-helper.md) (`simple-helper`)
Basic utility agent for straightforward tasks and assistance.

### [Python Import Validator](./python-import-validator.md) (`python-import-validator`)
Comprehensive Python import health validation using multi-tool static analysis approach.

### [Workspace Sync](./workspace-sync.md) (`workspace-sync`)
Specialized agent for Claude Code workspace and session synchronization with remote GPU workstation. Manages bidirectional sync operations and cross-environment development workflows.

## Usage
Use agents with the Task tool:
```
Task(description="Research task", prompt="Your request", subagent_type="research-scout")
```

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user-defined agents and is not part of Claude Code's core functionality.