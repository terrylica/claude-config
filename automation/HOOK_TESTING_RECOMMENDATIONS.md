# Shell Script Hook Testing - Off-the-Shelf Solutions Survey

**Purpose**: Prevent regression of "Stop hook error" issues in Claude Code CLI through automated testing and validation.

**Date**: 2025-10-27
**Version**: 1.0.0
**Related Tags**: v0.2.0-stop-hook-error-fixed, v0.2.1-cns-output-fix

______________________________________________________________________

## Executive Summary

This document surveys industry-standard tools and frameworks for automated shell script testing, specifically targeting output redirection issues that cause Claude Code CLI hook errors. Based on research of current (2025) best practices, we recommend a **three-tier approach**:

1. **Static Analysis** - ShellCheck (detect issues before runtime)
1. **Automated Testing** - BATS-core + Custom output validation
1. **Git Hook Automation** - pre-commit framework (enforce checks before commits)

______________________________________________________________________

## 1. Static Analysis: ShellCheck

### Overview

**Project**: https://github.com/koalaman/shellcheck
**Website**: https://www.shellcheck.net/
**License**: GNU GPL v3.0
**Status**: Actively maintained (2025)
**Platform**: Cross-platform (Linux, macOS, BSD, Windows)

### Key Features

- **Comprehensive coverage**: Detects beginner syntax errors, intermediate semantic issues, and advanced edge cases
- **Multiple output formats**: JSON, CheckStyle XML, GCC-compatible warnings, human-readable text
- **Shell support**: bash, dash, ksh, POSIX shells
- **Integration options**: Web interface, CLI, editor plugins, CI/CD pipelines

### Example Usage

```bash
# Install via Homebrew (macOS)
brew install shellcheck

# Check a single hook
shellcheck automation/cns/cns_hook_entry.sh

# Check all hooks with JSON output
shellcheck -f json automation/**/*.sh
```

### Limitations for Our Use Case

**IMPORTANT**: ShellCheck focuses on shell syntax and semantics, but **does not specifically detect missing output redirection on background processes**. This is a logic/design pattern issue rather than a syntax error.

ShellCheck **will** detect:

- Syntax errors
- Unquoted variables
- Incorrect command usage
- Many common pitfalls

ShellCheck **will NOT** detect:

- Missing `> /dev/null 2>&1` on `} &` background blocks
- Insufficient output redirection depth
- Output leaks from deeply nested background processes

**Recommendation**: Use ShellCheck for general shell script quality, but supplement with custom output testing.

______________________________________________________________________

## 2. Automated Testing Frameworks

### 2.1 BATS-core (Bash Automated Testing System)

**Project**: https://github.com/bats-core/bats-core
**Status**: Community-maintained (original archived 2021, bats-core is successor)
**Language**: Bash
**TAP-compliant**: Yes (Test Anything Protocol)

#### Overview

BATS provides a TAP-compliant testing framework designed specifically for testing Bash scripts and UNIX programs.

#### Example Test for Hook Output

```bash
#!/usr/bin/env bats

# Test: CNS hook produces zero output
@test "cns_hook_entry.sh produces no output" {
  run bash -c 'echo "{}" | "$HOME/.claude/automation/cns/cns_hook_entry.sh" 2>&1'
  [ "$status" -eq 0 ]
  [ -z "$output" ]  # Assert output is empty
}

# Test: All hooks produce zero output
@test "all hooks produce zero output" {
  hooks=(
    "$HOME/.claude/automation/cns/cns_hook_entry.sh"
    "$HOME/.claude/automation/prettier/format-markdown.sh"
    "$HOME/.claude/automation/lychee/runtime/hook/check-links-hybrid.sh"
  )

  for hook in "${hooks[@]}"; do
    run bash -c "echo '{}' | \"$hook\" 2>&1"
    [ "$status" -eq 0 ]
    [ -z "$output" ]
  done
}
```

#### Advantages

- Simple, readable test syntax
- TAP-compliant output works with CI/CD systems
- Can test any UNIX command/script
- Active community support

#### Disadvantages

- Less mature than general testing frameworks (JUnit, PyTest)
- Limited mocking/stubbing capabilities
- "Swallows" alias definitions (can complicate mocking)

### 2.2 shUnit2

**Project**: https://github.com/kward/shunit2
**License**: LGPL
**Pattern**: xUnit-style for shell scripts

#### Overview

shUnit2 provides xUnit-style testing for Bourne-based shell scripts, similar to JUnit/PyUnit patterns.

#### Example

```bash
#!/bin/sh

testHookOutputIsEmpty() {
  output=$(echo '{}' | "$HOME/.claude/automation/cns/cns_hook_entry.sh" 2>&1)
  assertEquals "Hook should produce no output" "" "$output"
}

# Load shUnit2
. shunit2
```

#### Recommendation

shUnit2 is more familiar to developers with xUnit experience, but BATS-core has better TAP integration for CI/CD. Choose based on team preference.

______________________________________________________________________

## 3. Git Hook Automation: pre-commit Framework

### Overview

**Project**: https://pre-commit.com/
**GitHub**: https://github.com/pre-commit/pre-commit
**Language**: Python
**Latest Release**: August 9, 2025
**Requires**: Python >=3.9

### Key Features

- **Language-agnostic**: Python, JavaScript, Go, Shell, Rust, Ruby, and more
- **Multi-hook orchestration**: Run multiple validation tools in sequence
- **Built-in hooks**: JSON/YAML/TOML syntax validation, trailing whitespace, debugger detection
- **Custom hook support**: Easy integration of custom shell scripts
- **Fast execution**: Only runs on changed files (with `stages` configuration)

### Why pre-commit > Husky for Our Use Case

| Feature                | pre-commit              | Husky                 |
| ---------------------- | ----------------------- | --------------------- |
| **Platform**           | Python (cross-platform) | Node.js/npm required  |
| **Multi-language**     | Native support          | Limited               |
| **Shell script focus** | Excellent               | JavaScript-focused    |
| **Maturity**           | Mature, stable          | Younger ecosystem     |
| **Our stack**          | Python (uv), Shell      | No Node.js dependency |

**Decision**: Use **pre-commit** since we already use Python (uv) and have no Node.js requirement.

### Example Configuration

Create `/Users/terryli/.claude/.pre-commit-config.yaml`:

```yaml
# .pre-commit-config.yaml - Hook validation automation
repos:
  # ShellCheck static analysis
  - repo: https://github.com/koalaman/shellcheck-precommit
    rev: v0.10.0
    hooks:
      - id: shellcheck
        name: ShellCheck - Static analysis
        files: \.sh$
        exclude: ^(node_modules|\.git)/

  # Custom hook output validation
  - repo: local
    hooks:
      - id: validate-hook-output
        name: Validate Claude Code hooks produce zero output
        entry: /Users/terryli/.claude/automation/testing/validate-hook-output.sh
        language: script
        pass_filenames: false
        files: \.sh$
        # Only run when hook files change
        files: ^automation/(cns|lychee|prettier)/.*\.sh$

  # General shell script quality
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: check-executables-have-shebangs
      - id: check-shebang-scripts-are-executable
      - id: check-json
      - id: check-yaml
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

### Custom Hook Output Validator

Create `/Users/terryli/.claude/automation/testing/validate-hook-output.sh`:

```bash
#!/usr/bin/env bash
# Validate that all Claude Code hooks produce zero output
set -euo pipefail

hooks=(
  "$HOME/.claude/automation/cns/cns_hook_entry.sh"
  "$HOME/.claude/automation/cns/cns_notification_hook.sh"
  "$HOME/.claude/automation/cns/conversation_handler.sh"
  "$HOME/.claude/automation/prettier/format-markdown.sh"
  "$HOME/.claude/automation/lychee/runtime/hook/check-links-hybrid.sh"
)

failed=0
for hook in "${hooks[@]}"; do
  output=$(echo '{}' | "$hook" 2>&1 || true)
  if [[ -n "$output" ]]; then
    echo "❌ FAIL: $(basename "$hook") produced output:"
    echo "$output" | head -5
    failed=1
  else
    echo "✅ PASS: $(basename "$hook")"
  fi
done

exit $failed
```

Make it executable:

```bash
chmod +x /Users/terryli/.claude/automation/testing/validate-hook-output.sh
```

### Installation

```bash
# Install pre-commit via uv (recommended for our setup)
uv tool install pre-commit

# Or via Homebrew
brew install pre-commit

# Install hooks in repository
cd /Users/terryli/.claude
pre-commit install

# Run manually to test
pre-commit run --all-files

# Run only on changed files
pre-commit run
```

______________________________________________________________________

## 4. Continuous Integration (CI/CD)

### GitHub Actions Example

```yaml
# .github/workflows/hook-validation.yml
name: Hook Validation

on: [push, pull_request]

jobs:
  validate-hooks:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit on all files
        run: pre-commit run --all-files

      - name: Test hook output directly
        run: |
          chmod +x automation/testing/validate-hook-output.sh
          automation/testing/validate-hook-output.sh
```

______________________________________________________________________

## 5. Recommendations Summary

### Tier 1: Immediate Implementation (High Priority)

1. **Create custom hook output validator** (like `/tmp/test-all-hooks.sh` we already created)

   - Location: `/Users/terryli/.claude/automation/testing/validate-hook-output.sh`
   - Purpose: Detect output leaks before they cause errors
   - Effort: 30 minutes

1. **Install ShellCheck via Homebrew**

   ```bash
   brew install shellcheck
   ```

   - Run manually before commits: `shellcheck automation/**/*.sh`
   - Effort: 5 minutes

### Tier 2: Short-term Implementation (Medium Priority)

3. **Set up pre-commit framework**

   - Install via `uv tool install pre-commit`
   - Create `.pre-commit-config.yaml` (see example above)
   - Run `pre-commit install`
   - Effort: 1 hour

1. **Add BATS test suite**

   - Install: `brew install bats-core`
   - Create `automation/testing/hooks.bats`
   - Run: `bats automation/testing/hooks.bats`
   - Effort: 2 hours

### Tier 3: Long-term Implementation (Lower Priority)

5. **GitHub Actions CI/CD** (if using GitHub)

   - Create `.github/workflows/hook-validation.yml`
   - Automate on every push/PR
   - Effort: 1 hour

1. **Editor Integration**

   - Install ShellCheck plugin for Helix/VS Code/etc.
   - Get real-time feedback while editing
   - Effort: 15 minutes

______________________________________________________________________

## 6. Testing Strategy for Output Redirection Issues

### The Challenge

Our specific issue (missing `> /dev/null 2>&1` on background processes) is a **design pattern problem**, not a syntax error. Static analysis tools like ShellCheck cannot detect this.

### Solution: Custom Runtime Testing

The most effective approach is **runtime output capture testing**:

```bash
# Principle: Simulate Claude Code's exact invocation
output=$(echo '{}' | hook_script 2>&1)

# Assert: Zero bytes output
if [[ -n "$output" ]]; then
  echo "FAIL: Hook leaked output"
  exit 1
fi
```

This is exactly what our `/tmp/test-all-hooks.sh` does, and should be:

1. Moved to `/Users/terryli/.claude/automation/testing/validate-hook-output.sh`
1. Integrated with pre-commit framework
1. Run before every commit to hook files

______________________________________________________________________

## 7. Alternative Tools Considered

### Shellharden

**Project**: https://github.com/anordal/shellharden
**Purpose**: Automatic shell script hardening
**Verdict**: More opinionated than ShellCheck, auto-fixes can be aggressive. Stick with ShellCheck for validation.

### ShellSpec

**Project**: https://shellspec.info/
**Purpose**: BDD-style testing for shells
**Verdict**: More complex than BATS, overkill for our needs. Use BATS-core instead.

### GitLeaks (via pre-commit)

**Project**: https://github.com/gitleaks/gitleaks
**Purpose**: Prevent secrets in commits
**Verdict**: Not relevant for output redirection, but **recommended** for general security.

______________________________________________________________________

## 8. Implementation Roadmap

### Week 1: Foundation

- [x] Create custom hook output validator (DONE - `/tmp/test-all-hooks.sh`)
- [ ] Move to permanent location: `automation/testing/validate-hook-output.sh`
- [ ] Install ShellCheck: `brew install shellcheck`
- [ ] Run ShellCheck on all hooks and fix warnings

### Week 2: Automation

- [ ] Install pre-commit: `uv tool install pre-commit`
- [ ] Create `.pre-commit-config.yaml`
- [ ] Test pre-commit locally: `pre-commit run --all-files`
- [ ] Install git hooks: `pre-commit install`

### Week 3: Testing Suite

- [ ] Install BATS-core: `brew install bats-core`
- [ ] Create `automation/testing/hooks.bats`
- [ ] Write comprehensive test cases
- [ ] Document how to run tests in README

### Week 4: CI/CD (Optional)

- [ ] Create GitHub Actions workflow (if applicable)
- [ ] Test on CI environment
- [ ] Document CI setup

______________________________________________________________________

## 9. Maintenance

### Regular Tasks

- **Before committing hook changes**: `pre-commit run` (automatic if installed)
- **Before releases**: `pre-commit run --all-files`
- **After hook modifications**: `automation/testing/validate-hook-output.sh`
- **Monthly**: `pre-commit autoupdate` (update hook versions)

### Regression Prevention

To prevent the "Stop hook error" from recurring:

1. **Pre-commit validation** catches issues before commit
1. **BATS tests** provide regression test suite
1. **ShellCheck** catches general shell issues
1. **Documentation** (this file) preserves institutional knowledge

______________________________________________________________________

## 10. Cost-Benefit Analysis

| Solution                | Setup Time | Ongoing Maintenance | Benefit                    | ROI        |
| ----------------------- | ---------- | ------------------- | -------------------------- | ---------- |
| Custom output validator | 30 min     | Near-zero           | High - Catches exact issue | ⭐⭐⭐⭐⭐ |
| ShellCheck              | 5 min      | Zero                | Medium - General quality   | ⭐⭐⭐⭐⭐ |
| pre-commit framework    | 1 hour     | 5 min/month         | High - Automation          | ⭐⭐⭐⭐   |
| BATS test suite         | 2 hours    | Low                 | Medium - Regression tests  | ⭐⭐⭐     |
| GitHub Actions CI/CD    | 1 hour     | Near-zero           | Medium - Auto-validation   | ⭐⭐⭐     |

**Recommendation**: Implement Tiers 1 and 2 (custom validator, ShellCheck, pre-commit). Tier 3 is optional.

______________________________________________________________________

## 11. References

- ShellCheck: https://www.shellcheck.net/
- BATS-core: https://github.com/bats-core/bats-core
- pre-commit: https://pre-commit.com/
- pre-commit hooks: https://github.com/pre-commit/pre-commit-hooks
- ShellCheck pre-commit: https://github.com/koalaman/shellcheck-precommit
- "Effortless Code Quality: The Ultimate Pre-Commit Hooks Guide for 2025": https://gatlenculp.medium.com/effortless-code-quality-the-ultimate-pre-commit-hooks-guide-for-2025-57ca501d9835

______________________________________________________________________

## Appendix A: Root Cause Pattern

The core issue we encountered:

```bash
# ❌ WRONG - Output can leak from background process
{
  some_command
  other_command
} &

# ✅ CORRECT - Block-level redirection prevents all leaks
{
  some_command
  other_command
} > /dev/null 2>&1 &
```

**Why this happens**: The background process `} &` can output to stdout/stderr AFTER the parent script exits. Without block-level redirection, Claude Code captures this delayed output and shows "Stop hook error".

**Testing pattern**:

```bash
# Simulate Claude Code's exact behavior
output=$(echo '{}' | hook_script 2>&1)
# Assert zero output
[[ -z "$output" ]] || echo "FAIL"
```

______________________________________________________________________

**Document Version**: 1.0.0
**Last Updated**: 2025-10-27
**Author**: Terry Li (with Claude Code assistance)
**Related Issues**: Stop hook error in Claude Code CLI v2.0.27-v2.0.28
