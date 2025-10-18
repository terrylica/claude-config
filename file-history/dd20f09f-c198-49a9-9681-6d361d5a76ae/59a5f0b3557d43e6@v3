# Repository Audit Quick Reference

**Version**: 1.0.0
**Created**: 2025-10-16
**Status**: reference
**Purpose**: Quick command reference for repository audit

---

## Quick Command Index

### Setup
```bash
# Install audit tools
cargo install cargo-udeps cargo-outdated cargo-audit cargo-deny cargo-machete tokei

# Create baseline
git tag audit-baseline-$(date +%Y%m%d)
git checkout -b audit/repository-prune-grow

# Document current state
echo "=== Baseline Metrics ===" > audit-baseline.txt
tokei crates/ >> audit-baseline.txt
fd . crates/ -t f | wc -l >> audit-baseline.txt
du -sh crates/ >> audit-baseline.txt
```

---

## Phase 1: Documentation Audit

```bash
# Find docs without status
rg -l "^# " docs/planning/ | while read f; do grep -q "Status:" "$f" || echo "$f"; done

# Find legacy markers
rg -i "obsolete|deprecated|legacy|old" docs/planning/

# Find all README files
fd -H README.md

# Check for broken links
rg '\[.*\]\(\.\./' docs/ --type md
```

---

## Phase 2: Code Audit

```bash
# Find unused dependencies (requires nightly)
cargo +nightly udeps --all-targets

# Find dead code
cargo build 2>&1 | rg "warning.*dead_code"

# Find TODO/FIXME
rg "TODO|FIXME|XXX|HACK" --type rust

# Check archived code size
du -sh src-archived/ archived_modules/

# List binaries
ls -la crates/rangebar-cli/src/bin/

# Check binary usage
for bin in crates/rangebar-cli/src/bin/*.rs; do
  name=$(basename "$bin" .rs)
  echo "=== $name ==="
  rg -c "$name" docs/ README.md || echo "Not documented"
done
```

---

## Phase 3: Dependency Audit

```bash
# Check for unused dependencies
cargo +nightly udeps --all-targets

# Find duplicate dependencies
cargo tree --duplicates

# Check for outdated
cargo outdated --workspace

# Find pinned versions
rg '^.*= "\d' Cargo.toml crates/*/Cargo.toml

# List features
rg "^\[features\]" -A 20 Cargo.toml crates/*/Cargo.toml
```

---

## Phase 4: Test Audit

```bash
# Count tests
cargo test -- --list | wc -l

# Find slow tests
cargo test -- --nocapture 2>&1 | rg "test.*ok" | rg -o "finished in.*" | sort -t' ' -k3 -nr

# Check test data size
du -sh test_data/

# Test examples compile
cargo build --examples

# Check example freshness
for ex in examples/*/*.rs; do
  echo "=== $ex ==="
  git log --oneline --since="1 year ago" "$ex" | wc -l
done
```

---

## Phase 5: Architecture Audit

```bash
# Check crate dependencies
cargo tree --workspace --depth 1

# Count lines per crate
for crate in crates/*/; do
  echo "=== $crate ==="
  tokei "$crate/src" --type rust
done

# Find unwrap in production
rg "\.unwrap\(\)" --type rust crates/*/src/ | rg -v test

# Find panic in libraries
rg "panic!" --type rust crates/*/src/ | rg -v test

# List error types
rg "^pub enum.*Error" --type rust
```

---

## Phase 6: File Organization Audit

```bash
# Find empty directories
fd -t d -x sh -c 'test -z "$(ls -A {})" && echo {}'

# Find single-file directories
fd -t d -x sh -c 'test $(ls -A {} | wc -l) -eq 1 && echo {}'

# Find version-suffixed files
fd -e rs -e md | rg "_v[0-9]|\.v[0-9]"

# Find temp files
fd "\.(bak|old|tmp|swp)$"

# Find mod.rs files
fd mod.rs

# Module structure
tree -L 3 crates/*/src/
```

---

## Phase 7: Git History Audit

```bash
# Find largest files
fd -t f -x du -h {} | sort -hr | head -20

# Find large files in history
git rev-list --objects --all | \
  git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | \
  sed -n 's/^blob //p' | \
  sort --numeric-sort --key=2 | \
  tail -20

# Check commit format
git log --oneline -50 | rg -v "^[a-f0-9]+ (feat|fix|docs|style|refactor|test|chore|perf):"

# Find merged branches
git branch --merged main | rg -v "main|master"

# Find stale branches
git for-each-ref --sort=-committerdate refs/heads/ --format='%(committerdate:short) %(refname:short)'
```

---

## Phase 8: Configuration Audit

```bash
# Check Cargo.toml files
fd Cargo.toml -x cat {}

# List workflows
ls -la .github/workflows/

# Check for IDE configs
fd -H "(.vscode|.idea|.fleet)" -t d

# Check editorconfig
cat .editorconfig 2>/dev/null || echo "Missing"
```

---

## Phase 9: Security Audit

```bash
# Search for secrets
rg -i "api[_-]?key|secret|password|token" --type rust | rg -v "// test"

# Find .env files
fd "\.env$" -H

# Run security audit
cargo audit

# Check for yanked crates
cargo deny check

# Find unsafe blocks
rg "unsafe " --type rust | rg -v "// Safety:"

# Count unsafe usage
rg "unsafe " --type rust -c | sort -t: -k2 -nr
```

---

## Generate Reports

```bash
# Create reports directory
mkdir -p audit-reports/

# Documentation audit report
{
  echo "# Documentation Audit Report"
  echo "## Files without status"
  rg -l "^# " docs/planning/ | while read f; do grep -q "Status:" "$f" || echo "- $f"; done
  echo "## Legacy markers"
  rg -i "obsolete|deprecated|legacy" docs/planning/ -l
} > audit-reports/01-documentation.md

# Code audit report
{
  echo "# Code Audit Report"
  echo "## Archived code size"
  du -sh src-archived/ archived_modules/
  echo "## TODO/FIXME count"
  rg "TODO|FIXME" --type rust -c | sort -t: -k2 -nr | head -20
  echo "## Dead code warnings"
  cargo build 2>&1 | rg "warning.*dead_code"
} > audit-reports/02-code.md

# Dependency audit report
{
  echo "# Dependency Audit Report"
  echo "## Duplicates"
  cargo tree --duplicates
  echo "## Outdated"
  cargo outdated --workspace
} > audit-reports/03-dependencies.md

# Test audit report
{
  echo "# Test Audit Report"
  echo "## Test count"
  cargo test -- --list | wc -l
  echo "## Test data size"
  du -sh test_data/
  echo "## Examples"
  ls -la examples/*/
} > audit-reports/04-tests.md

# Architecture audit report
{
  echo "# Architecture Audit Report"
  echo "## Lines of code per crate"
  for crate in crates/*/; do
    echo "### $crate"
    tokei "$crate/src" --type rust
  done
  echo "## Unwraps in production"
  rg "\.unwrap\(\)" --type rust crates/*/src/ | rg -v test | wc -l
} > audit-reports/05-architecture.md

# Security audit report
{
  echo "# Security Audit Report"
  echo "## Cargo audit"
  cargo audit
  echo "## Unsafe usage"
  rg "unsafe " --type rust -c | sort -t: -k2 -nr
} > audit-reports/09-security.md

# Generate summary
{
  echo "# Audit Summary"
  echo "**Date**: $(date)"
  echo "**Baseline**: $(git describe --tags)"
  echo ""
  echo "## Metrics"
  echo "### Code"
  tokei crates/ --type rust
  echo "### Files"
  fd . crates/ -t f | wc -l
  echo "### Size"
  du -sh crates/
  echo ""
  echo "## Key Findings"
  echo "- Documentation files: $(fd . docs/ -t f | wc -l)"
  echo "- Test files: $(fd test.rs | wc -l)"
  echo "- Examples: $(fd . examples/ -t f | wc -l)"
  echo "- Binaries: $(ls crates/rangebar-cli/src/bin/*.rs 2>/dev/null | wc -l)"
} > audit-reports/00-summary.md

echo "Reports generated in audit-reports/"
```

---

## Analysis Commands

```bash
# Top 10 largest Rust files
fd -e rs -x wc -l {} | sort -nr | head -10

# Most complex files (by line count)
fd -e rs -x tokei {} | sort -k4 -nr | head -20

# Files with most dependencies
for f in crates/*/Cargo.toml; do
  echo "=== $f ==="
  rg "^\w.*=" "$f" | wc -l
done | paste - - | sort -k2 -nr

# Crates with most public items
for crate in crates/*/src; do
  echo "=== $crate ==="
  rg "^pub " "$crate" --type rust | wc -l
done | paste - - | sort -k2 -nr

# Test to code ratio
for crate in crates/*/; do
  echo "=== $crate ==="
  code_lines=$(tokei "$crate/src" --type rust 2>/dev/null | rg "Rust" | awk '{print $5}')
  test_lines=$(tokei "$crate/tests" "$crate/src" --type rust 2>/dev/null | rg "#[cfg(test)]" -A 1000 | wc -l)
  echo "Code: $code_lines, Tests: $test_lines"
done
```

---

## Cleanup Candidates Generator

```bash
# Generate deletion candidates list
{
  echo "# Deletion Candidates"
  echo ""
  echo "## Empty directories"
  fd -t d -x sh -c 'test -z "$(ls -A {})" && echo "- {}"'
  echo ""
  echo "## Temp files"
  fd "\.(bak|old|tmp|swp)$" -x echo "- {}"
  echo ""
  echo "## Large files"
  fd -t f -x du -h {} | sort -hr | head -20 | awk '{print "- " $2 " (" $1 ")"}'
} > deletion-candidates.md
```

---

## Validation Commands

```bash
# After pruning, validate everything still works
cargo build --release --all-targets
cargo test --all-targets
cargo clippy --all-targets -- -D warnings
cargo fmt -- --check
cargo doc --no-deps

# Check no broken links in docs
fd -e md -x rg '\[.*\]\(' {} | rg -v "http" | rg "\.\./"

# Verify no orphaned files
fd -t f | while read f; do
  git ls-files --error-unmatch "$f" &>/dev/null || echo "Orphaned: $f"
done
```

---

## Post-Audit Metrics

```bash
# Generate comparison report
{
  echo "# Audit Results Comparison"
  echo ""
  echo "## Before"
  cat audit-baseline.txt
  echo ""
  echo "## After"
  tokei crates/
  fd . crates/ -t f | wc -l
  du -sh crates/
  echo ""
  echo "## Savings"
  # Calculate manually or with script
} > audit-results.md
```

---

**Quick Tips**:

1. Run commands from repository root
2. Pipe output to files for analysis: `command > output.txt`
3. Use `tee` to see and save: `command | tee output.txt`
4. Combine with `xargs` for batch operations
5. Use `--` to separate cargo flags from test flags
6. Add `2>&1` to capture stderr with stdout

**Safety**:
- All listed commands are read-only
- Create backups before any deletions
- Test changes on feature branch first
- Review all candidates before deletion

---

**END OF QUICK REFERENCE**
