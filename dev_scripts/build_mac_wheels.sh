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

# Verify the gh CLI is authenticated; offer to log in if not.
if ! gh auth status &>/dev/null; then
    echo "gh CLI not authenticated — launching 'gh auth login' now ..."
    echo "(This is a one-time step. Follow the prompts to log in via browser.)"
    gh auth login
    if ! gh auth status &>/dev/null; then
        echo "ERROR: gh auth login did not succeed. Re-run this script to try again."
        exit 1
    fi
fi

echo "Building macOS arm64 wheels for $TAG ..."
cibuildwheel --platform macos

echo "Uploading wheels to draft release $TAG ..."
gh release upload "$TAG" wheelhouse/*.whl --clobber

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo ""
echo "macOS wheels uploaded. Verify the draft release:"
echo "  https://github.com/$REPO/releases/"
echo ""
echo "Expected: 1 macOS arm64 + 2 Linux (x86_64 + i686) wheels per Python version,"
echo "plus 1 sdist. Check that all are present and have reasonable file sizes."
echo ""
echo "If this is a test run (tag ends in -bump-test), continue to verify the"
echo "draft release as described in the next step from test_release.sh."
echo ""
echo "If this is a real release: after verifying all assets and merging the"
echo "prerelease -> master PR, go to the URL above, scroll to the bottom of"
echo "the draft release page, and click 'Publish release'."
