# Claude Code User Memory

## Claude Code User Memory Documentation Principles
- **Scope**: These principles apply ONLY to this Claude Code user memory file
- **Purpose**: This document serves as a high-level pointer/reference only
- **Include**: Environment preferences, tool choices, file locations
- **Exclude**: Implementation details, parameters, version numbers, limitations, processing flows
- **Rationale**: Detailed specifications belong in the actual script files to avoid redundancy

## Tool Usage Preferences
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

## User Identity

- Terry Li is the Director of Operations of Eon Labs Ltd., who is responsible for features engineering for downstream see-2-seq model's consumption. 

## APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

- First get the current 'America/Vancouver' time using:
	```bashult
	TZ='America/Vancouver' date "+%A %Y-%m-%d %H:%M:%S %Z %z"
	```

### Usage: Claude Code Interaction

When you request "APCF", I will analyze ALL changes:

- **Staged files** (`git diff --cached`) - ready to commit
- **Modified files** (`git diff`) - unstaged changes  
- **Untracked files** (`git status --porcelain`) - new files
- Auto-derive SR&ED evidence from complete change analysis
- Generate logical commit grouping and sequencing strategy
- Create audit-proof commit messages for each logical group

**Workflow**: Make changes → Request "APCF" → I analyze everything → Suggest commit strategy

### Format Template

- Each commit in the sequence uses this format: auto-generated from workspace analysis
- Quote in backticks (`) any technical noun or proper noun per Markdown/GitHub style: package, library, tool, command, file, directory, language, class, function, config key, or other technical term; do not quote pronouns or non-technical nouns.

```
type(scope): description

- Knowledge Gap: [Auto-derived from file patterns + technical domain uncertainty + failed approaches]
- Motivation: [Auto-derived from commit intent + workspace changes + timeline context]
- Hypothesis: [Auto-derived from commit intent + proposed technical approach + risk factors] 
- Investigation: [Auto-derived from workspace analysis + systematic methodology + failures/iterations]
- Result: [Auto-derived from changes + technical advancement + specific measurements]
- Authenticity: [Developer notes + work timestamps + debugging context for CRA contemporaneous compliance]

The follow footer section display the lines of libraries involved seperated by commas and spaces. The lines are shown only if the pertaining libraries are involved:

- PyOpen: {Publicly available third-party Python libraries (on PyPI)}
- PyPriv: {Private or internal Python libraries not on PyPI}
- PyOthr: {Third-party programming libraries that are not Python, e.g. C++, JavaScript, Java, etc.}

Here in this line, the last line in the commit message, we display the result of the current 'America/Vancouver' time.
```

### Commit Grouping Logic

**Logical Sequencing Strategy**:

0. **Emergency First** (`hotfix:`, `revert:`) - Critical fixes and risk mitigation
1. **Infrastructure First** (`build:`, `config:`, `deps:`, `ci:`) - Foundation changes
2. **Core Implementation** (`feat:`, `refactor:`, `perf:`) - Main functionality  
3. **Quality Assurance** (`test:`, `fix:`, `security:`) - Validation and corrections
4. **Documentation** (`docs:`) - Knowledge capture
5. **Release Management** (`release:`) - Deployment readiness
6. **Maintenance** (`style:`, `chore:`) - Process improvements
7. **Work in Progress** (`wip:`) - Development snapshots (avoid in production)

**Atomic Grouping Rules**:

- **Related files together** - Files that implement the same feature
- **Dependency respect** - Infrastructure before features that depend on it
- **Audit trail clarity** - Each commit tells complete SR&ED story
- **Rollback safety** - Each commit is independently functional

### Auto-Derivation Intelligence (Workspace State → SR&ED Evidence)

#### File Pattern → Domain Detection

- `*.py, *.ipynb` → Algorithm/ML Development  
- `*.js, *.ts, *.jsx` → Frontend/API Innovation
- `*.sql, *.db` → Database Architecture Research
- `*.yaml, *.json, *.toml` → Configuration Investigation
- `test_*, *.test.*` → Validation Methodology
- `Dockerfile, *.sh` → Infrastructure Innovation
- `*.md, docs/` → Knowledge Capture Investigation

#### Workspace Analysis → SR&ED Scope & Priority

- **Single file change** → Focused technical uncertainty
- **Multiple related files** → Comprehensive investigation  
- **Cross-domain changes** → System-wide innovation
- **New file additions** → Experimental development
- **Dependency changes** → Technology integration research

#### APCF Evidence Standards

- **Specificity**: Use actual counts, technology names, file types ("modified 3 files" not "comprehensive changes")
- **Facts over Interpretation**: State direct technical actions ("what was built" not "how well it performs")  
- **CRA Compliance**: Include failure documentation, work-commit timestamps for contemporaneous evidence
- **Avoid derived metrics**: No "efficiency ratios", "performance improvements", or calculated benefits

### Search & Audit Trail Integration

- Every commit becomes searchable audit evidence
- Cross-repository SR&ED pattern recognition  
- Automatic evidence chain building for quarterly reports
- Government audit trail with direct commit verification

## 🧠 Workspace

- `uv run python -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

- **Tools**: uv, black, ruff, mypy, pytest  
- **Python**: 3.11+, type hints required  
- **Commands**: Use `make` or `uv run` for operations

### Documentation & README Audit Requirements

- **Link Validation**: Before editing README.md files, verify all directory links have README.md or point to existing files
- **GitHub Behavior**: Directory links without README.md show empty pages/404 on GitHub
- **Broken Link Types**: Check directory references, file paths, anchor links, relative paths
- **Security Audit**: Validate shell commands, file paths, user input handling in documentation examples
- **Root README Policy**: Aggregate links only; delegate content to target files/directories

## Development Environment Preferences

### Python Package Management
- **Primary Tool**: `uv` for all Python operations
- **Avoid**: pip, conda, pipenv

### System Environment
- **Platform**: macOS
- **Shell**: zsh
- **Working Directory**: `/Users/terryli/scripts`

### Cache System

- Uses `platformdirs` for platform-appropriate cache directories (not workspace dirs)

## Claude Code User Custom Extensions

### Intelligent Text-to-Speech Hook System
**Purpose**: Audio feedback for Claude Code responses

#### Core Files
- **Main Script**: `/Users/terryli/.claude/claude_response_speaker.sh`
- **Entry Point**: `/Users/terryli/.claude/tts_hook_entry.sh`
- **Configuration**: `/Users/terryli/.claude/settings.json`
- **Debug Logs**: `/tmp/claude_tts_debug.log`