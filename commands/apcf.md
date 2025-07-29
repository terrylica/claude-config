# APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

**Usage**: When you request "APCF" or "apcf", I will analyze ALL changes and create audit-proof commit messages.

## Command Process

**Workflow**: Make changes → Request "APCF" or "apcf" → I analyze everything → Suggest commit strategy

### Analysis Steps
1. **Staged files** (`git diff --cached --name-status`) - ready to commit
2. **Modified files** (`git diff --name-status`) - unstaged changes  
3. **Untracked files** (`git status --porcelain`) - new files
4. **Recent commits** (`git log --oneline -5`) - understand commit patterns
5. Auto-derive SR&ED evidence from complete change analysis
6. Generate logical commit grouping and sequencing strategy
7. Execute commits in sequence with user approval
8. Verify clean working tree completion

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
- Authenticity: [Developer notes + work timestamps + debugging context for CRA contemporaneous compliance]

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

### Common Issues & Solutions
- **Git command errors**: Use `git diff --cached --name-status` not `git status --cached`
- **Commit message formatting**: Use HEREDOC with proper quoting for multi-line messages
- **File staging logic**: Group related functionality, respect dependencies
- **Clean verification**: Always check `git status` after completion