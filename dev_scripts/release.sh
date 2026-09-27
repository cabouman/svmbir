#!/bin/bash
# Start a release of svmbir: the first of the three release steps in
# docs/source/dev_maintenance.rst.
#
#   dev_scripts/release.sh 0.4.1
#
# What this does, on the prerelease branch:
#   1. Sets the version in pyproject.toml, commits, and pushes.
#   2. Tags the commit v0.4.1 and pushes the tag.  GitHub Actions then builds
#      the wheels and the sdist and attaches them to a draft release.
#   3. Opens the pull request from prerelease to main.
#
# The remaining two steps are done on GitHub: merge the pull request, then
# publish the draft release, which uploads the files to PyPI.
#
# Requires the gh command, logged in.
set -euo pipefail

cd "$(dirname "$0")/.."
VERSION="${1:?usage: dev_scripts/release.sh X.Y.Z}"
TAG="v$VERSION"

if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "Version must look like X.Y.Z, got '$VERSION'" >&2
  exit 2
fi
if [[ "$(git rev-parse --abbrev-ref HEAD)" != "prerelease" ]]; then
  echo "Check out the prerelease branch first" >&2
  exit 1
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "The working tree has uncommitted changes; commit or stash them first" >&2
  exit 1
fi
git fetch -q --tags origin
if git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
  echo "Tag $TAG already exists" >&2
  exit 1
fi
git pull -q origin prerelease
gh auth status >/dev/null 2>&1 || { echo "Run 'gh auth login' first" >&2; exit 1; }

# The last CI run on prerelease must have passed on the current commit.
read -r CI_SHA CI_RESULT < <(gh run list --workflow CI --branch prerelease --limit 1 \
    --json headSha,conclusion -q '.[0] | "\(.headSha) \(.conclusion)"')
if [[ "$CI_SHA" != "$(git rev-parse HEAD)" || "$CI_RESULT" != "success" ]]; then
  echo "The last CI run on prerelease is '$CI_RESULT' for commit ${CI_SHA:0:7};" >&2
  echo "HEAD is $(git rev-parse --short HEAD).  Wait for CI to pass on HEAD, then retry." >&2
  exit 1
fi

# 1. Set the version, commit, push.
sed -i '' "s/^version = \".*\"/version = \"$VERSION\"/" pyproject.toml
grep -q "^version = \"$VERSION\"" pyproject.toml
git add pyproject.toml
git commit -q -m "Set version to $VERSION"
git push -q origin prerelease

# 2. Tag and push the tag; GitHub Actions builds the draft release.
git tag "$TAG"
git push -q origin "$TAG"

# 3. Open the pull request to main, unless one is already open.
if gh pr list --base main --head prerelease --state open --json number -q '.[0].number' | grep -q .; then
  echo "The pull request from prerelease to main is already open and now carries $VERSION."
else
  gh pr create --base main --head prerelease --title "Release $TAG" --body "Release $TAG."
fi

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo ""
echo "Version $VERSION is committed and tagged.  GitHub Actions is building the"
echo "wheels and the sdist into a draft release:"
echo "  https://github.com/$REPO/releases"
echo ""
echo "Next, on GitHub:"
echo "  1. When the checks pass, merge the pull request from prerelease to main."
echo "  2. Open the draft release $TAG, check that the wheels and the sdist are"
echo "     attached, and click 'Publish release'.  That uploads them to PyPI."
