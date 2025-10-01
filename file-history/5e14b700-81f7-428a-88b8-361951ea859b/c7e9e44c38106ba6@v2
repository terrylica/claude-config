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

# 1) Auto-install git-cliff if missing
command -v git-cliff >/dev/null || cargo install git-cliff

# 2) Initialize configs from templates if missing
for f in cliff.toml cliff-release-notes.toml .cz.toml; do
  [ ! -f "$f" ] && [ -f ~/.claude/tools/git-cliff/templates/${f%.toml.template}.toml ] && \
    cp ~/.claude/tools/git-cliff/templates/${f%.toml.template}.toml ./$f
done

# 3) Parse project version (Cargo.toml, package.json, or default)
if [ -f Cargo.toml ]; then
  VERSION=$(grep '^version = ' Cargo.toml | head -1 | cut -d'"' -f2)
elif [ -f package.json ]; then
  VERSION=$(grep '"version"' package.json | head -1 | cut -d'"' -f4)
else
  VERSION="0.1.0"
fi

# 4) Update .cz.toml with detected version if exists
if [ -f .cz.toml ] && [ -n "$VERSION" ]; then
  sed -i.bak "s/^version = .*/version = \"$VERSION\"/" .cz.toml && rm .cz.toml.bak
fi

# 5) Commit with conventional commits (AI synthesizes message from staged diff)
# AI Agent: analyze git diff --cached and create $MSG following conventional commits spec
git commit -m "$MSG"

# 6) Version bump + changelog generation
uvx --from commitizen cz bump --yes
git-cliff --config cliff.toml --output CHANGELOG.md
git-cliff --config cliff-release-notes.toml --latest --output RELEASE_NOTES.md
git add CHANGELOG.md RELEASE_NOTES.md && git commit --amend --no-edit

# 7) Push with tags
git push --follow-tags

# 8) Create GitHub release
TAG="v$(grep '^version = ' .cz.toml | cut -d'"' -f2)"
gh release create "$TAG" --verify-tag --title "$(basename $(pwd)) $TAG" -F RELEASE_NOTES.md

# 9) Surface telemetry
echo "📦 Release: https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases/tag/$TAG"
echo "🔗 CI: $(gh run list --limit 1 --json url --jq '.[0].url')"
echo "📝 Commit: $(git rev-parse HEAD)"
```

## Simplified Usage for AI Agents

**For commits only:**
```bash
command -v git-cliff >/dev/null || cargo install git-cliff
# AI: analyze `git diff --cached` → synthesize conventional commit message
git commit -m "$MSG"
```

**For full release:**
```bash
# AI: ensure configs exist (copy from templates if needed)
# AI: run version bump → changelog → push → GitHub release
# AI: output telemetry URLs
```

## Template Configs

Located in `~/.claude/tools/git-cliff/templates/`:
- `cliff.toml` - Detailed changelog (developer-focused)
- `cliff-release-notes.toml` - Release notes (user-focused)
- `cz.toml.template` - Commitizen config (update version field)

## Integration with Global CLAUDE.md

This workflow is documented in `~/.claude/CLAUDE.md` under release automation section.
