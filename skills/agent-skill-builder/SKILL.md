______________________________________________________________________

## name: agent-skill-builder description: Guide for creating Claude Code CLI Agent Skills following canonical format and best practices. Use when user wants to create, design, or learn about building Agent Skills. Covers SKILL.md structure, security, and token optimization.

# Agent Skill Builder

**Meta-Agent Skill teaching canonical Claude Code CLI Agent Skill creation using its own structure as the example.**

> ⚠️ **Scope**: This covers **Claude Code CLI** Agent Skills (`~/.claude/skills/`), not Claude.ai API skills (different format)
>
> **Terminology**: "Agent Skills" is Anthropic's official product name; "skills" in file/directory paths is implementation shorthand

## Purpose

Guide users to create properly formatted Claude Code Agent Skills following Anthropic's official standards, with emphasis on security and efficiency.

## When to Use

Triggers: "create skill", "agent skill", "build skill", "skill structure", "skill format", "how to write skills", "how to create agent skills"

______________________________________________________________________

## Part 1: Canonical Structure

### YAML Frontmatter (Required)

Every `SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-name-here
description: What this does and when to use it (max 1024 chars for CLI)
allowed-tools: Read, Grep, Bash # Optional, CLI-only feature
---
```

**Field Requirements:**

| Field           | Rules                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------- |
| `name`          | Lowercase, hyphens, numbers only. Max 64 chars. Must be unique.                                |
| `description`   | State WHAT it does + WHEN to use. Max 1024 chars (CLI) or 200 (API). Include trigger keywords! |
| `allowed-tools` | **CLI-only**. Comma-separated list restricts available tools. Optional.                        |

**Good vs Bad Descriptions:**

✅ **Good**: `"Extract text and tables from PDFs, fill forms, merge documents. Use when working with PDF files or when user mentions forms, contracts, document processing."`

❌ **Bad**: `"Helps with documents"` (too vague, no triggers)

### Directory Structure

**Personal Agent Skills** (user-specific):

```
~/.claude/skills/
└── your-skill-name/
    ├── SKILL.md           # Required: YAML + instructions
    ├── reference.md       # Optional: detailed docs
    ├── examples.md        # Optional: usage examples
    └── scripts/           # Optional: executable helpers
        └── process.py
```

**Project Agent Skills** (team-shared via git):

```
.claude/skills/
└── your-skill-name/
    └── SKILL.md
```

**File naming notes:**

- Use `SKILL.md` (uppercase) for CLI
- Use `Skill.md` (capitalized) for API skills
- Supporting files: `reference.md`, `examples.md` (singular, not directories)
- Directory path: `~/.claude/skills/` (lowercase "skills")

______________________________________________________________________

## Part 2: How Agent Skills Work (Token Efficiency)

### Progressive Disclosure Model

Agent Skills use a **three-tier loading system** to minimize token consumption:

1. **Metadata only** (30-50 tokens): Name + description loaded in system prompt for discovery
1. **SKILL.md content**: Loaded only when Agent Skill is relevant to current task
1. **Referenced files**: Loaded on-demand when explicitly referenced

**Result**: You can have unlimited Agent Skills without bloating context window! Each Agent Skill costs only 30-50 tokens until activated.

### Optimization Strategies

**Split large Agent Skills**:

- Keep mutually exclusive content in separate files
- Example: Put API v1 docs in `reference-v1.md`, API v2 in `reference-v2.md`
- Claude loads only the relevant version

**Reference files properly**:

```markdown
For authentication details, see reference.md section "OAuth Flow".
For examples, consult examples.md.
```

______________________________________________________________________

## Part 3: Security (Critical)

### 🚨 Security Threats

**1. Prompt Injection Attacks**

- Malicious input tricks Agent Skill into executing unintended actions
- **Recent CVEs**: CVE-2025-54794 (path bypass), CVE-2025-54795 (command injection)
- **Defense**: Validate inputs, use `allowed-tools` to restrict capabilities

**2. Tool Abuse**

- Adversary manipulates Agent Skill to run unsafe commands or exfiltrate data
- **Defense**: Minimize tool power, require confirmations for high-impact actions

**3. Data Exfiltration**

- Agent Skill could be tricked into leaking sensitive files
- **Defense**: Never hardcode secrets, use `allowed-tools` to block network commands

### Security Best Practices

**DO:**

- ✅ Run Claude Code in sandboxed environment (VM/container)
- ✅ Use `allowed-tools` to restrict dangerous tools (block WebFetch, Bash curl/wget)
- ✅ Validate all user inputs before file operations
- ✅ Use deny-by-default permission configs
- ✅ Audit downloaded Agent Skills before enabling
- ✅ Red-team test for prompt injection

**DON'T:**

- ❌ Hardcode API keys, passwords, or secrets in SKILL.md
- ❌ Run as root
- ❌ Trust Agent Skills from unknown sources
- ❌ Use unchecked `sudo` or `rm -rf` operations
- ❌ Enable all tools by default

### Security Example

**Insecure Agent Skill**:

```yaml
---
name: unsafe-api
description: Calls API with hardcoded key
---
API_KEY = "sk-1234..." # ❌ NEVER DO THIS
```

**Secure Agent Skill**:

```yaml
---
name: safe-api
description: Calls API using environment variables
allowed-tools: Read, Bash # Blocks WebFetch to prevent data exfiltration
---
# Safe API Client
Use environment variable $API_KEY from user's shell.
Validate all inputs before API calls.
```

______________________________________________________________________

## Part 4: Content Sections (Recommended)

After YAML frontmatter, organize content:

````markdown
# Agent Skill Name

Brief introduction (1-2 sentences).

## Instructions

Step-by-step guidance in **imperative mood**:

1. Read the file using Read tool
2. Process content with scripts/helper.py
3. Verify output

## Examples

Concrete usage:

```
Input: process_data.csv
Action: Run scripts/validate.py && scripts/process.py
Output: cleaned_data.csv with 1000 rows
```

## References

For detailed API specs, see reference.md.
For advanced examples, see examples.md.
````

**Writing style**:

- ✅ **Imperative**: "Read the file", "Run the script"
- ❌ **Suggestive**: "You should read", "Maybe try"

______________________________________________________________________

## Part 5: Agent Skill Composition & Limitations

### What Agent Skills CAN'T Do

❌ **Explicitly reference other Agent Skills**:

```markdown
# ❌ WRONG - Agent Skills can't call each other directly

"First use the api-auth skill, then use api-client skill"
```

### What Agent Skills CAN Do

✅ **Claude uses multiple Agent Skills automatically**:

- If both `api-auth` and `api-client` are relevant, Claude loads both
- No explicit coordination needed
- Agent Skills work together organically based on descriptions

______________________________________________________________________

## Part 6: CLI vs API Differences

| Feature           | Claude Code CLI        | Claude.ai API            |
| ----------------- | ---------------------- | ------------------------ |
| File name         | `SKILL.md` (uppercase) | `Skill.md` (capitalized) |
| Location          | `~/.claude/skills/`    | ZIP upload               |
| Description limit | 1024 characters        | 200 characters           |
| `allowed-tools`   | ✅ Supported           | ❌ Not supported         |
| Privacy           | Personal or project    | Individual account only  |
| Package install   | Pre-installed only     | Pre-installed only       |

**This Agent Skill teaches CLI format only.**

______________________________________________________________________

## Part 7: Creation Workflow

### Step 1: Define Purpose and Triggers

Answer:

- What specific problem does this solve?
- What keywords would users naturally mention?
- What file types or domains?

### Step 2: Initialize Structure

```bash
mkdir -p ~/.claude/skills/your-skill-name
touch ~/.claude/skills/your-skill-name/SKILL.md
```

### Step 3: Write YAML Frontmatter

Focus on description that enables autonomous discovery.

### Step 4: Write Instructions

- Use imperative mood
- Be specific and actionable
- Include examples

### Step 5: Test Activation

1. Start new conversation (or `/clear`)
1. Ask question using trigger keywords
1. Verify Claude loads Agent Skill (check output mentions skill)
1. Refine description if not activating

### Step 6: Security Audit

- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] `allowed-tools` restricts dangerous operations
- [ ] Tested for prompt injection
- [ ] No unsafe file operations

______________________________________________________________________

## Part 8: Common Patterns

### Pattern 1: Minimal Agent Skill (Single File)

```yaml
---
name: code-formatter
description: Format Python code using black. Use when formatting Python files.
allowed-tools: Read, Edit, Bash
---

# Code Formatter

## Instructions

1. Read Python file with Read tool
2. Run: black filename.py
3. Verify formatting changes
```

**Tokens**: ~30-50 until activated, ~200 when loaded

### Pattern 2: Agent Skill with Scripts

```yaml
---
name: data-validator
description: Validate CSV files for data quality. Use with CSV or tabular data.
allowed-tools: Read, Bash
---

# Data Validator

## Instructions

1. Run scripts/validate.py --input data.csv
2. Review validation report
3. Fix errors if found

## Scripts

- validate.py: Checks schema, nulls, duplicates
```

**Directory**:

```
data-validator/
├── SKILL.md
└── scripts/
    └── validate.py
```

### Pattern 3: Agent Skill with References

```yaml
---
name: api-client
description: Call internal REST API following company standards. Use for API requests.
allowed-tools: Read, Bash
---

# API Client

## Instructions

1. Consult reference.md for endpoint details
2. Build request per examples.md
3. Execute with curl (within allowed-tools)

## Files

- reference.md: API specification
- examples.md: Request/response examples
```

______________________________________________________________________

## Part 9: Validation Checklist

Before finalizing:

- [ ] YAML frontmatter valid (name, description)
- [ ] `name` follows rules (lowercase, hyphens, \<64 chars)
- [ ] `description` includes WHAT + WHEN (\<1024 chars, specific triggers)
- [ ] Instructions use imperative mood
- [ ] At least one concrete example
- [ ] Security audit passed (no secrets, input validation)
- [ ] `allowed-tools` restricts dangerous operations
- [ ] Tested activation with trigger keywords
- [ ] File paths relative or documented
- [ ] No duplicate functionality
- [ ] Supporting files in scripts/, reference.md, examples.md

______________________________________________________________________

## Part 10: Quick Reference

**Minimal valid Agent Skill**:

```yaml
---
name: my-skill
description: Does X when user mentions Y (specific triggers)
---
# My Skill

1. Do this
2. Then this
3. Finally this
```

**Locations**:

- Personal: `~/.claude/skills/my-skill/SKILL.md`
- Project: `.claude/skills/my-skill/SKILL.md`

**Reload**: Agent Skills auto-reload. For manual: `/clear` or restart conversation.

**Token cost**: 30-50 tokens until activated (unlimited Agent Skills possible!)

**Security**: Sandbox, restrict tools, validate inputs, no secrets.

______________________________________________________________________

## Resources

- **Official Docs**: https://docs.claude.com/en/docs/claude-code/skills
- **Official Repo**: https://github.com/anthropics/skills
- **Template**: https://github.com/anthropics/skills/tree/main/template-skill
- **Support**: https://support.claude.com/en/articles/12512198-how-to-create-custom-skills

______________________________________________________________________

## Meta-Example: This Agent Skill

This `agent-skill-builder` demonstrates its own principles:

1. ✅ **Clear name**: `agent-skill-builder` (lowercase, hyphenated, precise)
1. ✅ **Specific description**: Mentions "agent skill", "create", "build", "structure" as triggers
1. ✅ **Structured content**: Progressive disclosure with 10 parts
1. ✅ **Security included**: Dedicated section on threats and best practices
1. ✅ **Token efficient**: Core guidance here, could add reference.md for advanced topics
1. ✅ **CLI-specific**: Clarifies this is for Claude Code CLI, not API
1. ✅ **Examples**: Multiple concrete patterns
1. ✅ **Validation**: Includes checklist
1. ✅ **Official terminology**: Uses "Agent Skills" (formal) and `skills/` (file paths)

**Token usage**: ~50 tokens when inactive, ~2000 when fully loaded

______________________________________________________________________

## Summary

**Creating effective Claude Code CLI Agent Skills requires:**

1. **Specific naming/descriptions** for autonomous discovery (WHAT + WHEN + triggers)
1. **YAML frontmatter** with name, description, optional allowed-tools
1. **Security-first mindset** (sandbox, restrict tools, validate inputs, no secrets)
1. **Token optimization** (progressive disclosure, split large content)
1. **Structured content** (imperative instructions, concrete examples)
1. **Validation testing** (verify activation, security audit)
1. **Single focus** (one capability per Agent Skill)

This meta-Agent Skill teaches Agent Skill creation by being a canonical example itself.
