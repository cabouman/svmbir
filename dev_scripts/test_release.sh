#!/bin/bash
set -euo pipefail
#
# Test the release workflow end-to-end using a throwaway tag.
# Run this before ./cut_release.sh to verify that GitHub Actions builds
# the Linux wheels correctly and the local macOS build works.
#
# The script creates a test tag (e.g. v0.4.1-test) based on the current
# version in pyproject.toml, triggers the GitHub Actions release workflow,
# builds the macOS wheels locally, then cleans everything up after you
# confirm it all looks right.
#
# Usage (run from dev_scripts/):
#   ./test_release.sh

cd "$(dirname "$0")/.."

echo "=== svmbir release workflow test ==="
echo ""

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

echo "Preflight checks:"

git fetch --tags --quiet
echo "  OK    fetched from remote"

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "  FAIL  working tree has uncommitted changes"
    echo "        Commit or stash changes before testing."
    exit 1
fi
echo "  OK    working tree is clean"

if ! ls svmbir/sv-mbirct/src/*.c >/dev/null 2>&1; then
    echo "  FAIL  git submodule not initialized"
    echo "        Run:  git submodule update --init --recursive"
    exit 1
fi
echo "  OK    git submodule initialized"

if ! gh auth status &>/dev/null; then
    echo "  gh CLI not authenticated — launching 'gh auth login' now ..."
    echo "  (This is a one-time step. Follow the prompts to log in via browser.)"
    gh auth login
    if ! gh auth status &>/dev/null; then
        echo "  FAIL  gh auth login did not succeed. Re-run this script to try again."
        exit 1
    fi
fi
echo "  OK    gh CLI authenticated"

if ! command -v cibuildwheel &>/dev/null; then
    echo "  FAIL  cibuildwheel not found"
    echo "        Run:  pip install cibuildwheel==2.22.0"
    exit 1
fi
echo "  OK    cibuildwheel available"

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo ""

# ---------------------------------------------------------------------------
# Determine test tag
# ---------------------------------------------------------------------------

CURRENT=$(python3 -c "
import re, sys
m = re.search(r'^version = \"(.+)\"', open('pyproject.toml').read(), re.MULTILINE)
sys.exit(1) if not m else print(m.group(1))
")
TEST_TAG="v${CURRENT}-bump-test"

echo "Current version in pyproject.toml : $CURRENT"
echo "Test tag                          : $TEST_TAG"
echo "(Wheels will carry version $CURRENT — expected for a test run."
echo " The real release will update pyproject.toml to the new version before building.)"
echo ""

# If the test tag already exists, offer to remove it and start fresh.
if git rev-parse "$TEST_TAG" >/dev/null 2>&1; then
    echo "WARNING: tag $TEST_TAG already exists."
    read -rp "Delete it and start fresh? [yes/N]: " REDO
    if [ "$REDO" = "yes" ]; then
        gh release delete "$TEST_TAG" --yes 2>/dev/null && echo "  deleted existing draft release" || true
        git push --delete origin "$TEST_TAG" 2>/dev/null && echo "  deleted remote tag" || true
        git tag -d "$TEST_TAG" 2>/dev/null && echo "  deleted local tag" || true
        echo ""
    else
        echo "Aborted."
        exit 0
    fi
fi

# ---------------------------------------------------------------------------
# Confirmation
# ---------------------------------------------------------------------------

echo "About to:"
echo "  1. Create and push test tag $TEST_TAG"
echo "     (GitHub Actions will create a draft release and build Linux wheels)"
echo "  2. Build macOS arm64 wheels locally and upload to the draft release"
echo "  3. Pause for you to verify the draft release on GitHub"
echo "  4. Delete the test tag and draft release"
echo ""
read -rp "Proceed? [yes/N]: " CONFIRM
[ "$CONFIRM" = "yes" ] || { echo "Aborted."; exit 0; }
echo ""

# Print cleanup instructions if anything fails from here on.
trap '
echo ""
echo "Script failed. The test tag may still exist — clean up with:"
echo "  gh release delete '"$TEST_TAG"' --yes"
echo "  git push --delete origin '"$TEST_TAG"'"
echo "  git tag -d '"$TEST_TAG"'"
' ERR

# ---------------------------------------------------------------------------
# Step 1/3 — Create and push test tag
# ---------------------------------------------------------------------------

echo "--- 1/3  Creating and pushing test tag $TEST_TAG ---"
git tag "$TEST_TAG"
git push --tags
echo ""
echo "     GitHub Actions is now creating the draft release and building"
echo "     Linux wheels. Watch progress at:"
echo "     https://github.com/$REPO/actions"
echo ""

# ---------------------------------------------------------------------------
# Step 2/3 — Build macOS wheels locally
# ---------------------------------------------------------------------------

echo "--- 2/3  Building macOS arm64 wheels locally ---"
dev_scripts/build_mac_wheels.sh "$TEST_TAG"
echo ""

# ---------------------------------------------------------------------------
# Step 3/3 — Verify
# ---------------------------------------------------------------------------

echo "--- 3/3  Verify the draft release ---"
echo ""
echo "Once the GitHub Actions Linux build finishes, confirm that all wheels"
echo "(Linux + macOS arm64, all Python versions) and the source distribution"
echo "are attached at:"
echo "  https://github.com/$REPO/releases/tag/$TEST_TAG"
echo ""
echo "Optional: test-install a wheel to confirm it works:"
echo "  pip install <URL copied from the release page>"
echo ""
read -rp "Did everything look correct? [yes/N]: " VERIFIED

trap - ERR

echo ""
if [ "$VERIFIED" = "yes" ]; then
    echo "Cleaning up ..."
    gh release delete "$TEST_TAG" --yes 2>/dev/null && echo "  deleted draft release" || true
    git push --delete origin "$TEST_TAG" 2>/dev/null && echo "  deleted remote tag" || true
    git tag -d "$TEST_TAG" 2>/dev/null && echo "  deleted local tag" || true
    echo ""
    echo "Release workflow verified. Run ./cut_release.sh when ready for the real release."
else
    echo "Leaving the draft release in place for investigation."
    echo "When done, clean up manually:"
    echo "  gh release delete $TEST_TAG --yes"
    echo "  git push --delete origin $TEST_TAG"
    echo "  git tag -d $TEST_TAG"
fi
