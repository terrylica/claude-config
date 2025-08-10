---
description: "Generate audit-proof commit messages for SR&ED compliance"
argument-hint: "[scope] [--extract-evidence] [--compliance-check] [--full-workflow]"
allowed-tools: Task, Bash, Glob, Grep, Read, Write, TodoWrite
---

# APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

**Usage Options**:
- `/apcf` - Full APCF workflow with SR&ED evidence extraction and compliance validation
- `/apcf [scope]` - Target specific files or directories for commit analysis
- `/apcf --extract-evidence` - Use SR&ED evidence extractor for commit analysis
- `/apcf --compliance-check` - Run compliance audit on proposed commit messages
- `/apcf --full-workflow` - Complete SR&ED workflow with evidence extraction and compliance validation

## Command Process

**Workflow**: Make changes → Request "APCF" or "apcf" → I analyze everything → Suggest commit strategy

### Analysis Steps
1. **Third-party protection check** - Identify and protect third-party submodules from accidental commits
2. **Gitignore conflict detection** - Detect and auto-resolve tracked files matching .gitignore patterns
3. **Change analysis** - Comprehensive git status, staged, modified, and untracked file assessment
4. **SR&ED evidence extraction** - Deploy `sred-evidence-extractor` agent for commit analysis and evidence generation
5. **Commit strategy planning** - Generate logical commit grouping and sequencing strategy
6. **Compliance validation** - Deploy `compliance-auditor` agent for audit-ready message validation
7. **Execution coordination** - Execute commits in sequence with user approval and safety verification

### Agent Integration Workflow

**Multi-Agent Orchestration**:
- **Primary**: APCF orchestrates the complete SR&ED compliance workflow
- **Evidence Extraction**: `sred-evidence-extractor` analyzes git commits and code changes for Canadian tax credit compliance
- **Compliance Review**: `compliance-auditor` ensures government audit readiness and CRA compliance
- **Coordinated Output**: Unified commit message generation with full evidence chain and compliance validation
10. Verify clean working tree completion

### Timestamp Requirement
First get the current 'America/Vancouver' time using:
```bash
TZ='America/Vancouver' date "+%A %Y-%m-%d %H:%M:%S %Z %z"
```

## Commit Message Template

Each commit uses this format (auto-generated from workspace analysis):

```
type(scope): description

- Knowledge Gap: [Auto-derived from file patterns + technical domain uncertainty + failed approaches]
- Motivation: [Auto-derived from commit intent + workspace changes + timeline context]
- Hypothesis: [Auto-derived from commit intent + proposed technical approach + risk factors] 
- Investigation: [Auto-derived from workspace analysis + systematic methodology + failures/iterations]
- Result: [Auto-derived from changes + technical advancement + specific measurements]
- Authenticity: [Real-time technical discoveries + debugging breakthrough moments + tool-specific implementation challenges + personal developer insights demonstrating contemporaneous hands-on technical work]

The follow footer section display the lines of libraries involved seperated by commas and spaces. The lines are shown only if the pertaining libraries are involved:

- PyOpen: {Publicly available third-party Python libraries (on PyPI)}
- PyPriv: {Private or internal Python libraries not on PyPI}
- PyOthr: {Third-party programming libraries that are not Python, e.g. C++, JavaScript, Java, etc.}

Here in this line, the last line in the commit message, we display the result of the current 'America/Vancouver' time.
```

**Formatting Rules**:
- Quote in backticks (`) any technical noun or proper noun per Markdown/GitHub style: package, library, tool, command, file, directory, language, class, function, config key, or other technical term
- Do not quote pronouns or non-technical nouns

## Commit Grouping Logic

### Logical Sequencing Strategy

0. **Emergency First** (`hotfix:`, `revert:`) - Critical fixes and risk mitigation
1. **Infrastructure First** (`build:`, `config:`, `deps:`, `ci:`) - Foundation changes
2. **Core Implementation** (`feat:`, `refactor:`, `perf:`) - Main functionality  
3. **Quality Assurance** (`test:`, `fix:`, `security:`) - Validation and corrections
4. **Documentation** (`docs:`) - Knowledge capture
5. **Release Management** (`release:`) - Deployment readiness
6. **Maintenance** (`style:`, `chore:`) - Process improvements
7. **Work in Progress** (`wip:`) - Development snapshots (avoid in production)

### Atomic Grouping Rules

- **Related files together** - Files that implement the same feature
- **Dependency respect** - Infrastructure before features that depend on it
- **Audit trail clarity** - Each commit tells complete SR&ED story
- **Rollback safety** - Each commit is independently functional

### Third-Party Submodule Protection Rules

- **Never commit third-party submodule changes** - Protects against tampering with external repositories
- **Auto-reset protection** - Third-party submodules are automatically reset to prevent accidental commits
- **Third-party repositories**: `repos/nautilus_trader`, `repos/finplot`, `repos/claude-flow`
- **Allowed repositories**: `repos/data-source-manager` (Eon-Labs private)
- **Use safe commit process** - APCF automatically uses `git-commit-safe` script for protection

## Auto-Derivation Intelligence (Workspace State → SR&ED Evidence)

### File Pattern → Domain Detection

- `*.py, *.ipynb` → Algorithm/ML Development  
- `*.js, *.ts, *.jsx` → Frontend/API Innovation
- `*.sql, *.db` → Database Architecture Research
- `*.yaml, *.json, *.toml` → Configuration Investigation
- `test_*, *.test.*` → Validation Methodology
- `Dockerfile, *.sh` → Infrastructure Innovation
- `*.md, docs/` → Knowledge Capture Investigation
- `automation/*, hooks/*` → Workflow Integration Research
- `settings.json, CLAUDE.md` → System Configuration Investigation

### Workspace Analysis → SR&ED Scope & Priority

- **Single file change** → Focused technical uncertainty
- **Multiple related files** → Comprehensive investigation  
- **Cross-domain changes** → System-wide innovation
- **New file additions** → Experimental development
- **Dependency changes** → Technology integration research

### APCF Evidence Standards

- **Specificity**: Use actual counts, technology names, file types ("modified 5 files" not "comprehensive changes")
- **Facts over Interpretation**: State direct technical actions ("what was built" not "how well it performs")  
- **CRA Compliance**: Include failure documentation, work-commit timestamps for contemporaneous evidence
- **Avoid derived metrics**: No "efficiency ratios", "performance improvements", or calculated benefits
- **Platform Coverage**: Document cross-platform compatibility investigations when applicable
- **Portability Evidence**: Include user-specific reference elimination and workspace sharing preparations

## Search & Audit Trail Integration

- Every commit becomes searchable audit evidence
- Cross-repository SR&ED pattern recognition  
- Automatic evidence chain building for quarterly reports
- Government audit trail with direct commit verification

## Execution Best Practices

### Successful APCF Patterns
- **Infrastructure → Core → Documentation** sequencing maximizes audit clarity
- **Platform detection** investigations provide strong technical uncertainty evidence
- **File deletion metrics** (e.g., "−2,977 deletions") demonstrate systematic simplification research
- **User approval workflow** ensures commit strategy alignment before execution

### Gitignore Conflict Detection & Resolution

**Purpose**: Automatically detect and resolve tracked files that should be ignored per .gitignore rules

#### Detection Process
```bash
# Identify tracked files matching .gitignore patterns
git ls-files -i --exclude-standard -c
```

#### Auto-Resolution Workflow
When conflicts are detected:
1. **Display conflicted files**: Show which tracked files match .gitignore
2. **Auto-untrack files**: Use `git rm --cached` to untrack while preserving local files
3. **Dedicated commit**: Create separate commit for gitignore hygiene
4. **Continue APCF**: Proceed with normal workflow after resolution

#### Implementation Commands
```bash
# Detection
git ls-files -i --exclude-standard -c

# Resolution (when conflicts found)
git ls-files -i --exclude-standard -c | xargs -r git rm --cached

# Verification
git status --porcelain | grep -v "^??" | wc -l  # Should be 0 for clean state
```

#### Commit Message Pattern
```
chore(gitignore): resolve tracking conflicts with ignore patterns

- Knowledge Gap: Repository hygiene maintenance with .gitignore precedence rules
- Investigation: Detected N tracked files matching .gitignore patterns via `git ls-files -i --exclude-standard`
- Result: Untracked conflicted files while preserving local copies for continued development
```

### Common Issues & Solutions
- **Git command errors**: Use `git diff --cached --name-status` not `git status --cached`
- **Commit message formatting**: Use HEREDOC with proper quoting for multi-line messages
- **File staging logic**: Group related functionality, respect dependencies
- **Clean verification**: Always check `git status` after completion
- **IDE change indicators**: Gitignore conflicts resolved to prevent persistent change notifications