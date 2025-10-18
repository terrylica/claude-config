# Repository Audit Plan: Prune & Grow Opportunities

**Version**: 1.0.0
**Created**: 2025-10-17
**Status**: pending
**Purpose**: Systematic audit to identify pruning (cleanup) and growth (improvement) opportunities

---

## Audit Principles

1. **Single Source of Truth**: Eliminate redundant documentation and code
2. **Minimize Maintenance Burden**: Remove unused/archived code that isn't serving a purpose
3. **Maximize Signal-to-Noise**: Keep what's valuable, remove what's confusing
4. **Follow the Money**: Focus on what's actually used in production
5. **Progressive Disclosure**: Documentation should point to details, not duplicate them

---

## Phase 1: Documentation Audit (Est: 2-3 hours)

### 1.1 Planning Documentation Audit

**Prune Candidates**:
- [ ] `docs/planning/legacy/` - Review all files, determine if any should be deleted vs archived
- [ ] `docs/planning/PRODUCTION_HARDENING_ROADMAP.md` - Check if superseded by completed work
- [ ] `docs/planning/current/hybrid-plan-phase1.md` - Mark as completed if done
- [ ] `docs/planning/current/walk-forward-pattern-recognition-system-session.txt` - Evaluate relevance
- [ ] Find all files with "obsolete", "deprecated", "old", "v1", "v2" in name
- [ ] Search for duplicate ADRs or decision records

**Grow Candidates**:
- [ ] Create `docs/planning/INDEX.md` - Hub for all planning docs with status
- [ ] Add "Status" field to all planning docs (pending/in_progress/completed/archived)
- [ ] Add "Supersedes" field to track evolution of plans
- [ ] Missing: Post-implementation reviews for completed plans

**Commands**:
```bash
# Find planning docs without status
rg -l "^# " docs/planning/ | while read f; do
  grep -q "Status:" "$f" || echo "Missing status: $f"
done

# Find legacy/obsolete markers
rg -i "obsolete|deprecated|legacy|old" docs/planning/

# Find duplicate headers
rg "^# " docs/planning/ -A0 | sort | uniq -d
```

### 1.2 Technical Documentation Audit

**Prune Candidates**:
- [ ] `docs/testing/test-data-guide.md` - Consolidate with test_utils documentation
- [ ] `test_data/README.md` - Check for redundancy with docs/testing/
- [ ] `README.md` (root) - Evaluate if it should exist (conflicts with .claude/ docs preference)
- [ ] Find all scattered README files, consolidate to docs/

**Grow Candidates**:
- [ ] Missing: API documentation for public crates (rangebar-core, rangebar-providers)
- [ ] Missing: Architecture Decision Records (ADRs) for v3.0.0→v5.0.0 changes
- [ ] Missing: Migration guide for threshold units change (1bps → 0.1bps)
- [ ] Missing: Exness provider integration guide
- [ ] Missing: Performance benchmarking guide

**Commands**:
```bash
# Find all README files
fd -H README.md

# Find docs without frontmatter
rg -L "^---" docs/ --type md

# Check for broken internal links
rg '\[.*\]\(\.\./' docs/ --type md
```

### 1.3 Code Documentation Audit

**Prune Candidates**:
- [ ] Find modules with no doc comments
- [ ] Find functions with outdated doc examples
- [ ] Remove `// TODO` comments that are completed or irrelevant

**Grow Candidates**:
- [ ] Missing: Crate-level documentation for all 8 crates
- [ ] Missing: Module-level examples in rangebar-core
- [ ] Missing: Error handling patterns documentation
- [ ] Add `#![warn(missing_docs)]` to public crates

**Commands**:
```bash
# Find TODO comments
rg "TODO|FIXME|XXX|HACK" --type rust

# Find public items without docs
rg "^pub (fn|struct|enum|trait|mod)" --type rust -A1 | rg -v "///"

# Count doc coverage per crate
for crate in crates/*/; do
  echo "=== $crate ==="
  rg "^pub " "$crate/src/" --type rust | wc -l
  rg "^pub.*\n\s*///" "$crate/src/" --type rust | wc -l
done
```

---

## Phase 2: Code Audit (Est: 4-5 hours)

### 2.1 Dead Code Audit

**Prune Candidates**:
- [ ] Run `cargo udeps` to find unused dependencies
- [ ] Run `cargo machete` to find unused dependencies (alternative)
- [ ] Search for `#[allow(dead_code)]` and evaluate necessity
- [ ] Find private functions never called
- [ ] Check `archived_modules/` - delete or document preservation reason

**Commands**:
```bash
# Find unused dependencies
cargo +nightly udeps --all-targets

# Find dead code warnings
cargo build 2>&1 | rg "warning.*dead_code"

# Find allow dead_code
rg "#\[allow\(dead_code\)\]" --type rust

# Check archived modules usage
ls -lah archived_modules/
rg -l "archived_modules" --type rust
```

### 2.2 Archived Code Audit

**Prune Candidates**:
- [ ] `src-archived/` (1.4MB) - Document why it's kept or delete
  - [ ] Review: Is v4.0.0 monolithic structure referenced anywhere?
  - [ ] Decision: Keep as historical reference or remove?
- [ ] `archived_modules/debug/` - Still referenced? Delete if not
- [ ] `archived_modules/experiments/` - Extract learnings, then delete

**Grow Candidates**:
- [ ] If keeping archived code: Add `ARCHIVED.md` explaining what's archived and why
- [ ] Extract any valuable patterns from archived code into current codebase
- [ ] Document migration path from v4.0.0 → v5.0.0 if not already done

**Commands**:
```bash
# Check size of archived code
du -sh src-archived/ archived_modules/

# Find references to archived code
rg "src-archived|archived_modules" --type rust

# List all archived files
fd . src-archived/ archived_modules/
```

### 2.3 Binary/CLI Tools Audit

**Prune Candidates**:
- [ ] Check `crates/rangebar-cli/src/bin/` - Are all 6+ binaries still used?
  - [ ] `data_structure_validator` - Production use?
  - [ ] `polars-benchmark` - One-time use? Archive results?
  - [ ] `temporal-integrity-validator` - Still needed?
  - [ ] `rangebar-analyze` - Active?
  - [ ] `rangebar-export` - Active?
  - [ ] `tier1-symbol-discovery` - Still relevant?

**Grow Candidates**:
- [ ] Missing: CLI integration tests
- [ ] Missing: Binary usage documentation in `--help` text
- [ ] Consider: Consolidate multiple binaries into subcommands of single binary

**Commands**:
```bash
# List all binaries
ls -la crates/rangebar-cli/src/bin/

# Check which are referenced in docs
for bin in crates/rangebar-cli/src/bin/*.rs; do
  name=$(basename "$bin" .rs)
  echo "=== $name ==="
  rg -c "$name" docs/ README.md || echo "Not documented"
done

# Check git activity on binaries
for bin in crates/rangebar-cli/src/bin/*.rs; do
  echo "=== $bin ==="
  git log --oneline --since="6 months ago" "$bin" | wc -l
done
```

---

## Phase 3: Dependency Audit (Est: 2 hours)

### 3.1 Unused Dependencies

**Prune Candidates**:
- [ ] Run `cargo udeps` on all crates
- [ ] Check for dependencies only used in examples/tests
- [ ] Find duplicate dependencies across crates (different versions)
- [ ] Identify heavy dependencies used for trivial tasks

**Commands**:
```bash
# Check for unused dependencies
cargo +nightly udeps --all-targets

# Find duplicate dependencies
cargo tree --duplicates

# Check dependency sizes
cargo tree --edges normal --prefix depth | head -50

# List all dependencies
rg "^\w.*=" Cargo.toml crates/*/Cargo.toml
```

### 3.2 Dependency Versions Audit

**Prune Candidates**:
- [ ] Check for pinned versions that could use ranges
- [ ] Find dependencies with major version updates available
- [ ] Identify deprecated dependencies

**Grow Candidates**:
- [ ] Document why specific versions are pinned
- [ ] Add `[workspace.dependencies]` for shared dependencies
- [ ] Set up `cargo deny` for dependency policies

**Commands**:
```bash
# Check for outdated dependencies
cargo outdated --workspace

# Find pinned (exact) versions
rg '^.*= "\d' Cargo.toml crates/*/Cargo.toml

# Check workspace dependencies
rg "\[workspace.dependencies\]" Cargo.toml
```

### 3.3 Feature Flags Audit

**Prune Candidates**:
- [ ] Find unused feature flags
- [ ] Check for features that should be default
- [ ] Identify overlapping features

**Grow Candidates**:
- [ ] Missing: Documentation of what each feature enables
- [ ] Consider: Splitting large crates by features

**Commands**:
```bash
# List all features
rg "^\[features\]" -A 20 Cargo.toml crates/*/Cargo.toml

# Check feature usage
cargo tree --features

# Find code behind features
rg "#\[cfg\(feature" --type rust
```

---

## Phase 4: Test Audit (Est: 3-4 hours)

### 4.1 Test Coverage Audit

**Prune Candidates**:
- [ ] Find duplicate tests (same functionality tested multiple times)
- [ ] Identify slow tests that could be optimized or removed
- [ ] Check for tests that always pass (tautologies)
- [ ] Remove tests for removed functionality

**Grow Candidates**:
- [ ] Missing: Integration tests for CLI binaries
- [ ] Missing: Property-based tests for core algorithm
- [ ] Missing: Benchmark tests for regression detection
- [ ] Add test coverage reporting

**Commands**:
```bash
# Count tests
cargo test -- --list | wc -l

# Find slow tests
cargo test -- --nocapture 2>&1 | rg "test.*ok" | rg -o "finished in.*" | sort -t' ' -k3 -nr

# List test files
fd test.rs tests/

# Check test documentation
rg "^/// Test" --type rust
```

### 4.2 Test Data Audit

**Prune Candidates**:
- [ ] `test_data/` directory - Is all data still used?
- [ ] Large test files that could be generated instead
- [ ] Duplicate test data across different test files

**Grow Candidates**:
- [ ] Missing: Test data generation scripts
- [ ] Missing: Documentation of test data format
- [ ] Consider: Synthetic test data generators vs stored files

**Commands**:
```bash
# Check test data size
du -sh test_data/

# Find references to test data
rg "test_data/" --type rust

# List large test files
fd . test_data/ -t f -x du -h {} | sort -hr | head -20
```

### 4.3 Example Code Audit

**Prune Candidates**:
- [ ] `examples/` - Are all examples working and relevant?
  - [ ] `examples/educational/` - Still valuable?
  - [ ] `examples/analysis/` - Outdated?
  - [ ] `examples/interactive/` - Used?
  - [ ] `examples/validation/` - Redundant with tests?

**Grow Candidates**:
- [ ] Missing: Examples for each major use case
- [ ] Missing: Examples using latest API (v5.0.0)
- [ ] Convert working examples to integration tests

**Commands**:
```bash
# List all examples
ls -la examples/*/

# Test all examples compile
cargo build --examples

# Check example freshness
for ex in examples/*/*.rs; do
  echo "=== $ex ==="
  git log --oneline --since="1 year ago" "$ex" | wc -l
done
```

---

## Phase 5: Architecture Audit (Est: 4-5 hours)

### 5.1 Crate Boundaries Audit

**Prune Candidates**:
- [ ] Check for circular dependencies between crates
- [ ] Find crates that are too small (could merge)
- [ ] Identify crates with unclear purpose

**Grow Candidates**:
- [ ] Missing: Architecture diagram showing crate relationships
- [ ] Consider: Split large crates (rangebar-core > 5000 LOC?)
- [ ] Document: Why 8 crates vs more/fewer

**Commands**:
```bash
# Check crate dependencies
cargo tree --workspace --depth 1

# Count lines per crate
for crate in crates/*/; do
  echo "=== $crate ==="
  tokei "$crate/src" --type rust
done

# Find circular deps
cargo build --workspace 2>&1 | rg "cyclic"
```

### 5.2 Public API Audit

**Prune Candidates**:
- [ ] Find `pub` items that should be `pub(crate)`
- [ ] Identify overly complex public APIs
- [ ] Check for breaking changes since last major version

**Grow Candidates**:
- [ ] Missing: Semantic versioning policy documentation
- [ ] Missing: API stability guarantees
- [ ] Add `#[non_exhaustive]` to enums/structs that may grow

**Commands**:
```bash
# List all public items
rg "^pub " --type rust | wc -l

# Find public items in binary crates (shouldn't have many)
rg "^pub " crates/rangebar-cli/src/ --type rust

# Check for #[non_exhaustive]
rg "#\[non_exhaustive\]" --type rust
```

### 5.3 Error Handling Audit

**Prune Candidates**:
- [ ] Find `unwrap()` calls in production code (completed in Quick Wins)
- [ ] Check for `panic!()` in libraries
- [ ] Identify inconsistent error types

**Grow Candidates**:
- [ ] Missing: Error handling guidelines documentation
- [ ] Consider: Unified error type across crates
- [ ] Add error context (use `anyhow` or custom Context trait)

**Commands**:
```bash
# Find unwrap in production
rg "\.unwrap\(\)" --type rust crates/*/src/ | rg -v test

# Find panic in libraries
rg "panic!" --type rust crates/*/src/ | rg -v test

# List error types
rg "^pub enum.*Error" --type rust
```

---

## Phase 6: File Organization Audit (Est: 2-3 hours)

### 6.1 Directory Structure Audit

**Prune Candidates**:
- [ ] Check for empty directories
- [ ] Find directories with single file (could inline)
- [ ] Identify misplaced files

**Grow Candidates**:
- [ ] Missing: Consistent directory naming convention
- [ ] Document: Project structure in ARCHITECTURE.md
- [ ] Consider: Moving all docs to docs/ (currently scattered)

**Commands**:
```bash
# Find empty directories
fd -t d -x sh -c 'test -z "$(ls -A {})" && echo {}'

# Find single-file directories
fd -t d -x sh -c 'test $(ls -A {} | wc -l) -eq 1 && echo {}'

# Check for consistent naming
fd -t d | rg -i "test|tests|test_" | sort
```

### 6.2 File Naming Audit

**Prune Candidates**:
- [ ] Find files with inconsistent naming (snake_case vs kebab-case)
- [ ] Check for files with version numbers in name (v1, v2, etc.)
- [ ] Identify temp/scratch files (.bak, .old, .tmp)

**Grow Candidates**:
- [ ] Document: File naming conventions
- [ ] Standardize: All Rust files snake_case, docs kebab-case

**Commands**:
```bash
# Find version suffixed files
fd -e rs -e md | rg "_v[0-9]|\.v[0-9]"

# Find temp files
fd "\.(bak|old|tmp|swp)$"

# Find non-snake-case Rust files
fd -e rs | rg "[A-Z]"
```

### 6.3 Module Organization Audit

**Prune Candidates**:
- [ ] Find modules that re-export everything (unnecessary indirection)
- [ ] Check for `mod.rs` that only contains `pub mod` declarations
- [ ] Identify modules with single public item (could inline)

**Grow Candidates**:
- [ ] Convert remaining `mod.rs` to file-based modules (Rust 2018 style)
- [ ] Group related modules into parent modules
- [ ] Add module-level documentation

**Commands**:
```bash
# Find mod.rs files
fd mod.rs

# Find single-export modules
rg "^pub use" --type rust -c | rg ":1$"

# Check module structure
tree -L 3 crates/*/src/
```

---

## Phase 7: Git History Audit (Est: 2 hours)

### 7.1 Large Files Audit

**Prune Candidates**:
- [ ] Find large files in history (even if deleted)
- [ ] Check for accidentally committed binaries
- [ ] Identify large test data files

**Commands**:
```bash
# Find largest files in repo
fd -t f -x du -h {} | sort -hr | head -20

# Find large files in git history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -20

# Check .gitignore coverage
git status --ignored
```

### 7.2 Commit Message Audit

**Prune Candidates**:
- [ ] N/A (can't prune history without rewrite)

**Grow Candidates**:
- [ ] Check compliance with Conventional Commits
- [ ] Missing: Commit message template
- [ ] Missing: Pre-commit hooks for message validation

**Commands**:
```bash
# Check recent commit format
git log --oneline -50 | rg -v "^[a-f0-9]+ (feat|fix|docs|style|refactor|test|chore|perf):"

# Find commits without type
git log --pretty=format:"%s" -100 | rg -v "^(feat|fix|docs):"
```

### 7.3 Branch Audit

**Prune Candidates**:
- [ ] List stale local branches
- [ ] Find merged branches not deleted
- [ ] Identify long-lived feature branches

**Commands**:
```bash
# List local branches
git branch -vv

# Find merged branches
git branch --merged main | rg -v "main|master"

# Find stale branches
git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)'
```

---

## Phase 8: Configuration Audit (Est: 1-2 hours)

### 8.1 Cargo Configuration Audit

**Prune Candidates**:
- [ ] Check for unused `[profile.*]` settings
- [ ] Find duplicate `[dependencies]` across workspace
- [ ] Identify unused `[features]`

**Grow Candidates**:
- [ ] Missing: Workspace-level dependency management
- [ ] Missing: Custom profiles for different use cases
- [ ] Document: Why specific compiler flags are set

**Commands**:
```bash
# Check all Cargo.toml files
fd Cargo.toml -x cat {}

# Find profile settings
rg "^\[profile\." Cargo.toml crates/*/Cargo.toml

# Check workspace config
rg "^\[workspace" Cargo.toml
```

### 8.2 CI/CD Configuration Audit

**Prune Candidates**:
- [ ] Check `.github/workflows/` for unused workflows
- [ ] Find duplicate job definitions
- [ ] Identify slow CI jobs that could be optimized

**Grow Candidates**:
- [ ] Missing: Automated dependency updates (Dependabot configured?)
- [ ] Missing: Security scanning workflow
- [ ] Missing: Benchmark regression detection
- [ ] Add: Artifact caching for faster CI

**Commands**:
```bash
# List workflows
ls -la .github/workflows/

# Check workflow runs
gh run list --limit 20

# Find slow jobs
gh run view --log | rg "took.*[0-9]+m"
```

### 8.3 Editor/IDE Configuration Audit

**Prune Candidates**:
- [ ] Check for committed IDE config (should be in .gitignore)
- [ ] Find unused editor config files

**Grow Candidates**:
- [ ] Missing: .editorconfig for consistency
- [ ] Missing: rust-analyzer configuration
- [ ] Document: Recommended IDE setup

**Commands**:
```bash
# Find IDE config files
fd -H "(.vscode|.idea|.fleet)" -t d

# Check .editorconfig
cat .editorconfig 2>/dev/null || echo "Missing"

# Check rust-analyzer config
cat rust-analyzer.toml 2>/dev/null || echo "Missing"
```

---

## Phase 9: Security Audit (Est: 2-3 hours)

### 9.1 Secrets Audit

**Prune Candidates**:
- [ ] Search for hardcoded API keys/tokens
- [ ] Find committed .env files
- [ ] Check for database connection strings

**Commands**:
```bash
# Search for potential secrets
rg -i "api[_-]?key|secret|password|token" --type rust | rg -v "// test"

# Find .env files
fd "\.env$" -H

# Check git history for secrets
git log -p | rg -i "password|secret|api.?key"
```

### 9.2 Dependency Security Audit

**Prune Candidates**:
- [ ] N/A (just fix vulnerabilities)

**Grow Candidates**:
- [ ] Add `cargo audit` to CI
- [ ] Add `cargo deny` for supply chain security
- [ ] Document: Security update policy

**Commands**:
```bash
# Run security audit
cargo audit

# Check for yanked crates
cargo deny check

# List security advisories
cargo audit --json | jq '.vulnerabilities'
```

### 9.3 Code Safety Audit

**Prune Candidates**:
- [ ] Find unnecessary `unsafe` blocks
- [ ] Check for unsafe transmutes
- [ ] Identify potential buffer overflows

**Grow Candidates**:
- [ ] Add `#![forbid(unsafe_code)]` to appropriate crates
- [ ] Document: When unsafe is acceptable
- [ ] Add MIRI tests for unsafe code

**Commands**:
```bash
# Find unsafe blocks
rg "unsafe " --type rust | rg -v "// Safety:"

# Check for forbid unsafe
rg "#!\[forbid\(unsafe_code\)\]" --type rust

# Count unsafe usage
rg "unsafe " --type rust -c | sort -t: -k2 -nr
```

---

## Phase 10: Generate Recommendations (Est: 2-3 hours)

### 10.1 Pruning Recommendations

**Output**: `docs/planning/current/pruning-recommendations.md`

**Contents**:
- [ ] List of files/directories to delete (with reasoning)
- [ ] Archived code decision (keep vs delete)
- [ ] Dependencies to remove
- [ ] Redundant tests/docs to consolidate
- [ ] Estimated disk space savings
- [ ] Estimated maintenance burden reduction

### 10.2 Growth Recommendations

**Output**: `docs/planning/current/growth-recommendations.md`

**Contents**:
- [ ] Missing documentation to add
- [ ] Test coverage gaps to fill
- [ ] Architecture improvements to implement
- [ ] New features/capabilities to add
- [ ] Developer experience improvements
- [ ] Estimated effort for each recommendation

### 10.3 Prioritization Matrix

**Output**: `docs/planning/current/audit-prioritization.md`

**Matrix Axes**:
- Impact: High/Medium/Low
- Effort: High/Medium/Low
- Urgency: Critical/Important/Nice-to-have

**Categories**:
- **Quick Wins**: High impact, low effort
- **Major Projects**: High impact, high effort
- **Fill Ins**: Low impact, low effort
- **Avoid**: Low impact, high effort

---

## Execution Checklist

### Pre-Audit
- [ ] Create feature branch: `audit/repository-prune-grow`
- [ ] Backup current state: `git tag audit-baseline-$(date +%Y%m%d)`
- [ ] Document current metrics (LOC, file count, dependency count)

### During Audit
- [ ] Execute each phase in order
- [ ] Document findings in phase-specific markdown files
- [ ] Take screenshots of tool outputs for reference
- [ ] Note any blockers or questions

### Post-Audit
- [ ] Compile final recommendations document
- [ ] Present findings to stakeholders (if applicable)
- [ ] Create implementation plan for high-priority items
- [ ] Update this audit plan with lessons learned

---

## Success Metrics

### Quantitative
- [ ] Reduce total LOC by X% (target: 10-15% through pruning)
- [ ] Reduce number of dependencies by Y (target: 5-10)
- [ ] Increase test coverage to Z% (target: 80%+)
- [ ] Reduce compilation time by N% (target: 10-20%)
- [ ] Delete M GB of unused data (target: >100MB)

### Qualitative
- [ ] Clearer separation of concerns between crates
- [ ] More discoverable documentation
- [ ] Easier onboarding for new contributors
- [ ] Faster CI/CD pipelines
- [ ] Better security posture

---

## Tools Required

### Rust Ecosystem
```bash
cargo install cargo-udeps       # Find unused dependencies
cargo install cargo-outdated    # Check for updates
cargo install cargo-audit       # Security vulnerabilities
cargo install cargo-deny        # Dependency policies
cargo install cargo-machete     # Alternative unused deps
cargo install tokei             # Count lines of code
cargo install cargo-tarpaulin   # Code coverage (Linux)
```

### General Tools
```bash
brew install fd                 # Fast find
brew install ripgrep            # Fast grep
brew install tokei              # LOC counter
brew install dust               # Disk usage
brew install gh                 # GitHub CLI
brew install jq                 # JSON processor
```

---

## Risk Assessment

### Low Risk Activities (Safe to execute immediately)
- Running read-only audit commands
- Generating reports and documentation
- Identifying candidates for pruning

### Medium Risk Activities (Require review)
- Deleting unused dependencies
- Removing archived code
- Consolidating duplicate tests
- Refactoring module boundaries

### High Risk Activities (Require thorough testing)
- Breaking API changes
- Removing public functions
- Deleting test data
- Restructuring crate boundaries

---

## Timeline Estimate

| Phase | Estimated Time | Dependencies |
|-------|---------------|--------------|
| Phase 1: Documentation | 2-3 hours | None |
| Phase 2: Code | 4-5 hours | None |
| Phase 3: Dependencies | 2 hours | Phase 2 |
| Phase 4: Tests | 3-4 hours | Phase 2 |
| Phase 5: Architecture | 4-5 hours | Phase 2, 3 |
| Phase 6: File Organization | 2-3 hours | None |
| Phase 7: Git History | 2 hours | None |
| Phase 8: Configuration | 1-2 hours | Phase 3 |
| Phase 9: Security | 2-3 hours | Phase 3 |
| Phase 10: Recommendations | 2-3 hours | All phases |
| **Total** | **24-33 hours** | **~3-4 working days** |

---

## Notes

- This audit is read-only and non-destructive
- All recommendations require review before implementation
- Some phases can be executed in parallel
- Tool installation time not included in estimates
- Focus on high-value findings first (80/20 rule)

---

**END OF REPOSITORY AUDIT PLAN**
