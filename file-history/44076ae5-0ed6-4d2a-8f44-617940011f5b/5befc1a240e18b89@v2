#!/usr/bin/env bash
# Unified release script for RangeBar
# Automates: version bump, changelog generation, release notes, and GitHub release creation

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting RangeBar release process...${NC}\n"

# Step 1: Bump version with Commitizen
echo -e "${YELLOW}📌 Step 1/6: Bumping version with Commitizen...${NC}"
uvx --from commitizen cz bump --yes

# Step 2: Get new version
VERSION=$(grep '^version = ' .cz.toml | cut -d'"' -f2)
TAG="v${VERSION}"
echo -e "${GREEN}✓ New version: ${TAG}${NC}\n"

# Step 3: Generate detailed CHANGELOG.md
echo -e "${YELLOW}📝 Step 2/6: Generating CHANGELOG.md...${NC}"
git-cliff --config cliff.toml --output CHANGELOG.md
echo -e "${GREEN}✓ CHANGELOG.md updated${NC}\n"

# Step 4: Generate GitHub release notes
echo -e "${YELLOW}🎉 Step 3/6: Generating release notes...${NC}"
git-cliff --config cliff-release-notes.toml \
  --tag "${TAG}" \
  --latest \
  --output RELEASE_NOTES.md
echo -e "${GREEN}✓ RELEASE_NOTES.md generated${NC}\n"

# Step 5: Commit changelog update
echo -e "${YELLOW}💾 Step 4/6: Committing changelog updates...${NC}"
git add CHANGELOG.md RELEASE_NOTES.md
if git diff --cached --quiet; then
  echo -e "${GREEN}✓ No changelog changes to commit${NC}\n"
else
  git commit --amend --no-edit
  echo -e "${GREEN}✓ Changelog updates committed${NC}\n"
fi

# Step 6: Push with tags
echo -e "${YELLOW}🚀 Step 5/6: Pushing to GitHub...${NC}"
git push --follow-tags
echo -e "${GREEN}✓ Pushed to origin with tags${NC}\n"

# Step 7: Create GitHub release
echo -e "${YELLOW}📦 Step 6/6: Creating GitHub release...${NC}"
gh release create "${TAG}" \
  --verify-tag \
  --title "RangeBar ${TAG}" \
  -F RELEASE_NOTES.md
echo -e "${GREEN}✓ GitHub release created${NC}\n"

# Display summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Release ${TAG} published successfully!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "📦 ${BLUE}Release:${NC} https://github.com/Eon-Labs/rangebar/releases/tag/${TAG}"
echo -e "🔗 ${BLUE}CI Run:${NC}  $(gh run list --limit 1 --json url --jq '.[0].url')"
echo -e "📝 ${BLUE}Changelog:${NC} https://github.com/Eon-Labs/rangebar/blob/main/CHANGELOG.md"
