# git-cliff Release Automation

AI coding agent prompt for automated conventional commits and release management.

## Prerequisites

- `cargo` (Rust toolchain)
- `uvx` (Python package runner)
- `gh` (GitHub CLI)

## AI Agent Prompt

Use this prompt with any AI coding agent (Claude Code, Cursor, etc.) to automate releases:

```bash
# git-cliff Release Workflow (zero-config, AI-driven)
# Prerequisites: cargo, uvx, gh CLI

# Pre-flight: AI workspace analysis
git status --short --untracked-files=all > /tmp/git_status.txt
git diff --stat > /tmp/diff_unstaged.txt
git diff --cached --stat > /tmp/diff_staged.txt
# AI Decision: Stage relevant files, skip artifacts/logs, skip sensitive files

# 1) Auto-install git-cliff if missing
command -v git-cliff >/dev/null || cargo install git-cliff

# 2) Initialize configs from templates if missing
for f in cliff.toml cliff-release-notes.toml .cz.toml; do
  [ ! -f "$f" ] && [ -f ~/.claude/tools/git-cliff/templates/${f%.toml.template}.toml ] && \
    cp ~/.claude/tools/git-cliff/templates/${f%.toml.template}.toml ./$f
done

# 3) Parse project version (language-agnostic detection)
if [ -f Cargo.toml ]; then
  VERSION=$(grep '^version = ' Cargo.toml | head -1 | cut -d'"' -f2)
elif [ -f package.json ]; then
  VERSION=$(grep '"version"' package.json | head -1 | cut -d'"' -f4)
elif [ -f pyproject.toml ]; then
  VERSION=$(grep '^version = ' pyproject.toml | head -1 | cut -d'"' -f2)
else
  VERSION="0.1.0"
fi

# 4) Update .cz.toml with detected version if exists
if [ -f .cz.toml ] && [ -n "$VERSION" ]; then
  sed -i.bak "s/^version = .*/version = \"$VERSION\"/" .cz.toml && rm .cz.toml.bak
fi

# 5) Commit with conventional commits (AI synthesizes message from git diff --cached)
uvx --from commitizen cz check --message "$MSG"
git commit -m "$MSG"

# 6) Version bump + changelog generation
uvx --from commitizen cz bump --yes
git-cliff --config cliff.toml --output CHANGELOG.md
git-cliff --config cliff-release-notes.toml --latest --output RELEASE_NOTES.md
git add CHANGELOG.md RELEASE_NOTES.md cliff.toml cliff-release-notes.toml .cz.toml && git commit --amend --no-edit

# 7) Push with tags
git push --follow-tags

# 8) Check for automated release workflows (conflict detection)
CONFLICTING_WORKFLOWS=$(find .github/workflows -name "*.yml" -o -name "*.yaml" 2>/dev/null | xargs grep -l "actions/create-release\|ncipollo/release-action\|softprops/action-gh-release" 2>/dev/null || echo "")
if [ -n "$CONFLICTING_WORKFLOWS" ]; then
  echo "⚠️  WARNING: Automated release workflows detected - skipping manual release"
  SKIP_MANUAL_RELEASE=true
else
  SKIP_MANUAL_RELEASE=false
fi

# 9) Create GitHub release (handle 125K char limit)
TAG="v$(grep '^version = ' .cz.toml | cut -d'"' -f2)"
if [ "$SKIP_MANUAL_RELEASE" = false ]; then
  head -50 RELEASE_NOTES.md > RELEASE_NOTES_SHORT.md
  echo -e "\n\n---\n*Full changelog: [CHANGELOG.md](https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/blob/$TAG/CHANGELOG.md)*" >> RELEASE_NOTES_SHORT.md
  gh release create "$TAG" --verify-tag --title "$(basename $(pwd)) $TAG" -F RELEASE_NOTES_SHORT.md
fi

# 10) Telemetry: milestone commit SHA and tag, surface all URLs
echo "📦 Release: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases/tag/$TAG"
echo "🔗 CI Run: $(gh run list --limit 1 --json url --jq '.[0].url')"
echo "📝 Commit: $(git rev-parse HEAD)"
```

## Simplified Usage for AI Agents

**For commits only:**
```bash
command -v git-cliff >/dev/null || cargo install git-cliff
# AI: analyze `git diff --cached` → synthesize conventional commit message
uvx --from commitizen cz check --message "$MSG"
git commit -m "$MSG"
```

**For full release:**
```bash
# AI: ensure configs exist (copy from templates if needed)
# AI: run version bump → changelog → push → GitHub release
# AI: handle 125K char limit for release notes
# AI: output telemetry URLs
```

## Template Configs

Located in `~/.claude/tools/git-cliff/templates/`:
- `cliff.toml` - Detailed changelog (developer-focused, all commits)
- `cliff-release-notes.toml` - Release notes (user-facing, latest release only)
- `cz.toml.template` - Commitizen config (SemVer version tracking)

## Features

- **AI Workspace Analysis**: Intelligent file staging (skip artifacts, logs, sensitive files)
- **Language-Agnostic**: Auto-detects version from Cargo.toml, package.json, or pyproject.toml
- **GitHub 125K Limit**: Creates RELEASE_NOTES_SHORT.md to avoid API errors
- **Conflict Detection**: Skips manual release if automated workflows exist
- **Zero-Config**: Auto-installs dependencies and initializes configs from templates

## Integration with Global CLAUDE.md

This workflow is documented in `~/.claude/CLAUDE.md` under "git-cliff Release Automation".
