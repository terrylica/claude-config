# Agents Directory

**Purpose**: Custom agent configurations and specialized sub-agents for Claude Code

## Available Agents

### [Research Scout](../../agents/research-scout.md) (`research-scout`)
Explores research directions from seed keywords. Use when you need systematic exploration of topics.

### [Compliance Auditor](../../agents/compliance-auditor.md) (`compliance-auditor`)
Specialized agent for compliance auditing and regulatory analysis.

### [SR&ED Evidence Extractor](../../agents/sred-evidence-extractor.md) (`sred-evidence-extractor`)
Extracts and documents Scientific Research and Experimental Development evidence from codebases.

### [Simple Helper](../../agents/simple-helper.md) (`simple-helper`)
Basic utility agent for straightforward tasks and assistance.

### [APCF Agent](../../agents/apcf-agent.md) (`apcf-agent`)
SR&ED-compliant commit message generator with automatic git hygiene and audit-proof formatting.

### [Python QA](../../agents/python-qa.md) (`python-qa`)
Comprehensive Python import health validation using multi-tool static analysis approach.

### [MHR Refactor](../../agents/mhr-refactor.md) (`mhr-refactor`)
Specialized refactoring agent for complex code transformations.

### [Workspace Sync](../../agents/workspace-sync.md) (`workspace-sync`)
Specialized agent for Claude Code workspace and session synchronization with remote GPU workstation. Manages bidirectional sync operations and cross-environment development workflows.

## Usage
Use agents with the Task tool:
```
Task(description="Research task", prompt="Your request", subagent_type="research-scout")
```

## ⚠️ CRITICAL: Agent Directory Requirements

### Frontmatter Requirements
**ALL agent files MUST include these required fields:**
```yaml
---
name: agent-name
description: "Agent description"
tools: Tool1, Tool2, Tool3
---
```

**Missing `name` field will cause parsing failures.**

### Directory Purity Rules
- **ONLY agent `.md` files** belong in `/agents/` directory
- **NO documentation files** (README.md, guides, etc.)
- **NO non-agent content** - everything gets parsed as an agent

### Documentation Placement
- **Agent documentation** → `/docs/AGENTS.md` (this file)
- **Command documentation** → `/commands/` directory  
- **General docs** → `/docs/` directory

### Common Mistakes That Cause Parsing Failures
1. ❌ `README.md` in `/agents/` directory → Move to `/docs/AGENTS.md`
2. ❌ Missing `name:` field in frontmatter → Add required field
3. ❌ Documentation files in `/agents/` → Move to appropriate `/docs/` location
4. ❌ Non-agent `.md` files in `/agents/` → Move or rename

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user-defined agents and is not part of Claude Code's core functionality.