#!/bin/bash
# Build macOS arm64 wheels locally and upload them to the draft GitHub Release
# for the given tag.
#
# Prerequisites:
#   pip install cibuildwheel   (once; any Python environment)
#   gh auth login              (once; authenticates the gh CLI)
#
# Usage (run from dev_scripts/):
#   ./build_mac_wheels.sh v0.4.1

set -euo pipefail

TAG=${1:?"Usage: build_mac_wheels.sh <tag>  e.g.  ./build_mac_wheels.sh v0.4.1"}

# Always work from the repo root regardless of where the script is called from.
cd "$(dirname "$0")/.."

# Fetch tags from remote so we can verify the tag exists.
echo "Fetching tags ..."
git fetch --tags --quiet

# Verify the tag exists.
git rev-parse "$TAG" >/dev/null 2>&1 || {
    echo "ERROR: Tag $TAG not found on remote. Push the tag first:"
    echo "  git tag $TAG && git push --tags"
    exit 1
}

# Verify HEAD matches the tag so the wheel is built from the correct commit.
HEAD_COMMIT=$(git rev-parse HEAD)
TAG_COMMIT=$(git rev-parse "$TAG")
if [ "$HEAD_COMMIT" != "$TAG_COMMIT" ]; then
    echo "ERROR: HEAD does not match tag $TAG."
    echo "Check out the tagged commit first:"
    echo "  git checkout $TAG"
    exit 1
fi

# Verify the working tree is clean.
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: Working tree has uncommitted changes."
    echo "Commit or stash all changes before building a release wheel."
    exit 1
fi

# Verify the git submodule is initialized.
if ! ls svmbir/sv-mbirct/src/*.c >/dev/null 2>&1; then
    echo "ERROR: C source files not found — git submodule not initialized."
    echo "Run:  git submodule update --init --recursive"
    exit 1
fi

# Verify cibuildwheel is available.
if ! command -v cibuildwheel &>/dev/null; then
    echo "ERROR: cibuildwheel not found."
    echo "Install it with:  pip install cibuildwheel"
    exit 1
fi

# Verify the gh CLI is authenticated.
if ! gh auth status &>/dev/null; then
    echo "ERROR: gh CLI is not authenticated."
    echo "Run:  gh auth login"
    exit 1
fi

echo "Building macOS arm64 wheels for $TAG ..."
cibuildwheel --platform macos

echo "Uploading wheels to draft release $TAG ..."
gh release upload "$TAG" wheelhouse/*.whl --clobber

echo ""
echo "macOS wheels uploaded. Check that the Linux wheels are also attached, then"
echo "publish the release at:"
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "  https://github.com/$REPO/releases/tag/$TAG"
