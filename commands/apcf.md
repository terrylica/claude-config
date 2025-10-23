# APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

**Usage**: When you request "APCF" or "apcf", I will spawn specialized sub-tasks to analyze ALL changes and create audit-proof commit messages using token-efficient parallel processing.

## Command Process

**Token-Efficient Workflow**: Make changes → Request "APCF" or "apcf" → I spawn sub-tasks for analysis → Consolidate results → Suggest commit strategy

**Key Advantage**: All analysis operations are delegated to spawn sub-tasks, preserving main session tokens for final coordination and user interaction.

### Analysis Steps (All Executed via Spawn Sub-Tasks)

**Phase 1: Parallel Data Collection Sub-Tasks**

1. **Repository Analysis Sub-Task**: Third-party protection check, staged/modified/untracked files analysis
2. **Git History Sub-Task**: Recent commits analysis and commit pattern recognition
3. **Workspace Pattern Sub-Task**: File type analysis, domain detection, dependency mapping

**Phase 2: SR&ED Evidence Generation Sub-Task** 4. **Evidence Derivation Sub-Task**: Auto-derive SR&ED evidence from complete change analysis using workspace state intelligence

**Phase 3: Strategy Planning Sub-Task** 5. **Commit Strategy Sub-Task**: Generate logical commit grouping and sequencing strategy with atomic grouping rules

**Phase 4: Main Session Coordination** 6. Present consolidated analysis and strategy to user for approval 7. Execute commits in sequence with user approval (using safe commit process) 8. Verify clean working tree completion

**Token Efficiency**: Steps 1-5 consume sub-task tokens, preserving main session capacity for user interaction and coordination.

### Timestamp Requirement (Sub-Task Delegated)

Timestamp generation is delegated to the **Repository Analysis Sub-Task** to get current 'America/Vancouver' time using:

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

**Sub-Task Implementation**: All file pattern analysis and workspace intelligence is executed by the **Workspace Pattern Sub-Task** and **Evidence Derivation Sub-Task** to preserve main session tokens.

### File Pattern → Domain Detection (Sub-Task Processed)

- `*.py, *.ipynb` → Algorithm/ML Development
- `*.js, *.ts, *.jsx` → Frontend/API Innovation
- `*.sql, *.db` → Database Architecture Research
- `*.yaml, *.json, *.toml` → Configuration Investigation
- `test_*, *.test.*` → Validation Methodology
- `Dockerfile, *.sh` → Infrastructure Innovation
- `*.md, docs/` → Knowledge Capture Investigation
- `automation/*, hooks/*` → Workflow Integration Research
- `settings.json, CLAUDE.md` → System Configuration Investigation

### Workspace Analysis → SR&ED Scope & Priority (Sub-Task Processed)

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

## Sub-Task Delegation Patterns

### Spawn Sub-Task Types and Responsibilities

**Repository Analysis Sub-Task** (`sred-evidence-extractor` agent):

- Git status analysis, diff processing, file change detection
- Third-party submodule protection verification
- Timestamp generation for Vancouver timezone
- Staged, modified, and untracked file cataloging

**Git History Sub-Task** (`sred-evidence-extractor` agent):

- Recent commit analysis and pattern recognition
- Commit message style consistency analysis
- Repository history context building

**Workspace Pattern Sub-Task** (`sred-evidence-extractor` agent):

- File type analysis and domain detection
- Dependency mapping and technology stack analysis
- Cross-platform pattern recognition

**Evidence Derivation Sub-Task** (`sred-evidence-extractor` agent):

- SR&ED evidence auto-generation from workspace state
- Knowledge gap, motivation, hypothesis derivation
- Investigation and result synthesis

**Commit Strategy Sub-Task** (`general-purpose` agent):

- Logical grouping strategy based on atomic rules
- Commit sequencing with dependency awareness
- Safe commit execution planning

## Execution Best Practices

### Token-Efficient APCF Patterns

- **Parallel Sub-Task Spawning**: Launch all Phase 1 sub-tasks simultaneously for maximum speed
- **Main Session Preservation**: Only user interaction and final coordination in main session
- **Infrastructure → Core → Documentation** sequencing maximizes audit clarity
- **Platform detection** investigations provide strong technical uncertainty evidence
- **File deletion metrics** (e.g., "−2,977 deletions") demonstrate systematic simplification research
- **User approval workflow** ensures commit strategy alignment before execution

### Common Issues & Solutions (Sub-Task Delegated)

- **Git command errors**: Sub-tasks use `git diff --cached --name-status` not `git status --cached`
- **Commit message formatting**: Sub-tasks use HEREDOC with proper quoting for multi-line messages
- **File staging logic**: Strategy sub-task groups related functionality, respects dependencies
- **Clean verification**: Final verification in main session checks `git status` after completion
