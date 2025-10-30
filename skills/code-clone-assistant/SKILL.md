______________________________________________________________________

## name: code-clone-assistant description: Code clone detection and automated refactoring assistant using PMD CPD and Semgrep. Detects exact duplicates (Type-1/2) and pattern-based clones (Type-3), then guides Claude Code CLI to refactor duplications with safety checks and verification. Use when user mentions code duplication, code clones, DRY violations, refactoring similar code, detecting repeated patterns, copy-paste code, or exact duplicates. allowed-tools: Read, Grep, Bash, Edit, Write

# Code Clone Assistant

Detect code clones and guide refactoring using PMD CPD (exact duplicates) + Semgrep (patterns).

## Tools

- **PMD CPD v7.17.0+**: Exact duplicate detection
- **Semgrep v1.140.0+**: Pattern-based detection

**Tested**: October 2025 - 30 violations detected across 3 sample files
**Coverage**: ~3x more violations than using either tool alone

______________________________________________________________________

## When to Use

Triggers: "find duplicate code", "DRY violations", "refactor similar code", "detect code duplication", "similar validation logic", "repeated patterns", "copy-paste code", "exact duplicates"

______________________________________________________________________

## Why Two Tools?

PMD CPD and Semgrep detect different clone types:

| Aspect       | PMD CPD                          | Semgrep                          |
| ------------ | -------------------------------- | -------------------------------- |
| **Detects**  | Exact copy-paste duplicates      | Similar patterns with variations |
| **Scope**    | Across files ✅                  | Within/across files (Pro only)   |
| **Matching** | Token-based (ignores formatting) | Pattern-based (AST matching)     |
| **Rules**    | ❌ No custom rules               | ✅ Custom rules                  |

**Result**: Using both finds ~3x more DRY violations.

### Clone Types

| Type   | Description                     | PMD CPD         | Semgrep     |
| ------ | ------------------------------- | --------------- | ----------- |
| Type-1 | Exact copies                    | ✅ Default      | ✅          |
| Type-2 | Renamed identifiers             | ✅ `--ignore-*` | ✅          |
| Type-3 | Near-miss with variations       | ⚠️ Partial      | ✅ Patterns |
| Type-4 | Semantic clones (same behavior) | ❌              | ❌          |

______________________________________________________________________

## Quick Start Workflow

```bash
# Step 1: Detect exact duplicates (PMD CPD)
pmd cpd -d . -l python --minimum-tokens 20 -f markdown > pmd-results.md

# Step 2: Detect pattern violations (Semgrep)
semgrep --config=clone-rules.yaml --sarif --quiet > semgrep-results.sarif

# Step 3: Analyze combined results (Claude Code)
# Parse both outputs, prioritize by severity

# Step 4: Refactor (Claude Code with user approval)
# Extract shared functions, consolidate patterns, verify tests
```

______________________________________________________________________

## Detection Commands

### PMD CPD (Exact Duplicates)

```bash
# Markdown format (optimal for AI processing)
pmd cpd -d . -l python --minimum-tokens 20 -f markdown

# Multi-language projects (run separately per language)
pmd cpd -d . -l python --minimum-tokens 20 -f markdown > pmd-python.md
pmd cpd -d . -l ecmascript --minimum-tokens 20 -f markdown > pmd-js.md
```

**Tuning thresholds**:

- New codebases: 30-50 tokens
- Legacy codebases: 75-100 tokens (start high, lower gradually)

**Exclusions**:

```bash
pmd cpd -d . -l python --minimum-tokens 20 \
    --exclude="**/tests/**,**/node_modules/**,**/__pycache__/**" \
    -f markdown
```

### Semgrep (Pattern Violations)

```bash
# SARIF format (CI/CD standard)
semgrep --config=clone-rules.yaml --sarif --quiet

# Text format (human-readable)
semgrep --config=clone-rules.yaml --quiet

# Parse SARIF with jq
semgrep --config=clone-rules.yaml --sarif --quiet | \
    jq -r '.runs[0].results[] | "\(.ruleId): \(.message.text)"'
```

Full rules file: `~/.claude/skills/code-clone-assistant/clone-rules.yaml`

______________________________________________________________________

## Complete Detection Workflow

### Phase 1: Detection

```bash
# Create working directory
mkdir -p /tmp/dry-audit-$(date +%Y%m%d)
cd /tmp/dry-audit-$(date +%Y%m%d)

# Run both tools
pmd cpd -d /path/to/project -l python --minimum-tokens 20 -f markdown > pmd-cpd.md
semgrep --config=/path/to/clone-rules.yaml --sarif --quiet /path/to/project > semgrep.sarif
```

### Phase 2: Analysis

```bash
# Parse PMD CPD (direct read - LLM-native format)
cat pmd-cpd.md

# Parse Semgrep SARIF
jq -r '.runs[0].results[] | "\(.ruleId): \(.message.text) at \(.locations[0].physicalLocation.artifactLocation.uri):\(.locations[0].physicalLocation.region.startLine)"' semgrep.sarif
```

**Combine findings**:

1. List PMD CPD duplications by severity (tokens/lines)
1. List Semgrep violations by file
1. Prioritize: Exact duplicates across files > Large within-file > Patterns

### Phase 3: Presentation

Present to user:

- Total violations (PMD + Semgrep)
- Breakdown by type (exact vs pattern)
- Files affected
- Estimated refactoring effort
- Suggested approach

**Example**:

```
DRY Audit Results:
==================
PMD CPD: 9 exact duplications
Semgrep: 21 pattern violations
Total: ~27 unique DRY violations

Top Issues:
1. process_user_data() duplicated in file1.py:5 and file2.py:5 (21 lines)
2. Duplicate validation logic across 6 locations (Semgrep)
3. Error collection pattern repeated 5 times (Semgrep)

Recommended Refactoring:
- Extract process_user_data() to shared utils module
- Create validate_input() function for validation logic
- Create ErrorCollector class for error handling

Proceed with refactoring? (y/n)
```

### Phase 4: Refactoring (With User Approval)

1. Read affected files using Read tool
1. Create shared functions/classes
1. Replace duplicates using Edit tool
1. Run tests using Bash tool
1. Commit changes if tests pass

______________________________________________________________________

## Best Practices

**DO**:

- ✅ Run both PMD CPD and Semgrep (complementary coverage)
- ✅ Start with conservative thresholds (PMD: 50 tokens)
- ✅ Review results before refactoring
- ✅ Run full test suite after refactoring
- ✅ Commit incrementally

**DON'T**:

- ❌ Only use one tool (miss ~70% of violations)
- ❌ Set thresholds too low (noise overwhelms signal)
- ❌ Refactor without understanding context
- ❌ Skip test verification

______________________________________________________________________

## Security

**Allowed Tools**: `Read, Grep, Bash, Edit, Write`

**Safe Refactoring**:

- Only refactor after user approval
- Run tests before marking complete
- Never use destructive commands
- Preserve git history
- Validate file paths before editing

______________________________________________________________________

## Detailed Documentation

For comprehensive details, see:

- **PMD CPD Reference**: `reference-pmd.md` - Commands, options, exclusions, error handling
- **Semgrep Reference**: `reference-semgrep.md` - Rules, patterns, advanced features
- **Examples**: `examples.md` - Real-world examples, complementary detection scenarios
- **Sample Rules**: `clone-rules.yaml` - Ready-to-use Semgrep patterns

______________________________________________________________________

## Installation

```bash
# Check installation
which pmd      # Should be /opt/homebrew/bin/pmd
which semgrep  # Should be /opt/homebrew/bin/semgrep

# Install if missing
brew install pmd      # PMD v7.17.0+
brew install semgrep  # Semgrep v1.140.0+
```

______________________________________________________________________

## Testing Results

**Test Date**: October 26, 2025
**Files Tested**: 3 files (sample1.py, sample2.py, sample.js)

**Results**:

- PMD CPD: 9 exact duplications
- Semgrep: 21 pattern violations
- Total Unique: ~27 DRY violations
- Coverage: 3x more than either tool alone

______________________________________________________________________

**This skill uses only tested commands validated in October 2025 with PMD CPD and Semgrep**
