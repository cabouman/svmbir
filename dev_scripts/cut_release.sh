#!/bin/bash
set -euo pipefail
#
# Interactive release script for svmbir.
#
# Verifies preconditions, bumps the version, commits, tags, triggers the
# GitHub Actions draft release, builds macOS arm64 wheels locally, and
# prints the remaining manual steps.
#
# Usage (run from dev_scripts/):
#   ./cut_release.sh

# Always work from the repo root regardless of where the script is called from.
cd "$(dirname "$0")/.."

echo "=== svmbir release script ==="
echo ""

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

echo "Preflight checks:"

# Branch must be prerelease.
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "prerelease" ]; then
    echo "  FAIL  branch is '$BRANCH' (must be 'prerelease')"
    echo "        Switch with:  git checkout prerelease"
    exit 1
fi
echo "  OK    branch is prerelease"

# Fetch latest state from remote (also needed for tag checks later).
git fetch --tags --quiet
echo "  OK    fetched from remote"

# Local branch must not be behind remote.
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse "@{u}" 2>/dev/null || true)
if [ -n "$REMOTE" ] && [ "$LOCAL" != "$REMOTE" ]; then
    echo "  FAIL  local branch is behind remote"
    echo "        Run:  git pull"
    exit 1
fi
echo "  OK    up to date with remote"

# Working tree must be clean.
if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "  FAIL  working tree has uncommitted changes"
    echo "        Commit or stash all changes before cutting a release."
    exit 1
fi
echo "  OK    working tree is clean"

# Git submodule must be initialized.
if ! ls svmbir/sv-mbirct/src/*.c >/dev/null 2>&1; then
    echo "  FAIL  git submodule not initialized"
    echo "        Run:  git submodule update --init --recursive"
    exit 1
fi
echo "  OK    git submodule initialized"

# gh CLI must be authenticated.
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

# cibuildwheel must be installed.
if ! command -v cibuildwheel &>/dev/null; then
    echo "  FAIL  cibuildwheel not found"
    echo "        Run:  pip install cibuildwheel"
    exit 1
fi
echo "  OK    cibuildwheel available"

echo ""

# ---------------------------------------------------------------------------
# Version selection
# ---------------------------------------------------------------------------

# Read current version from pyproject.toml.
CURRENT=$(python3 -c "
import re, sys
m = re.search(r'^version = \"(.+)\"', open('pyproject.toml').read(), re.MULTILINE)
sys.exit(1) if not m else print(m.group(1))
")

# Read latest published release (strips leading 'v').
LATEST_TAG=$(gh release list --exclude-drafts --limit 1 --json tagName \
             -q '.[0].tagName' 2>/dev/null || true)
LATEST="${LATEST_TAG#v}"
[ -z "$LATEST" ] && LATEST_DISPLAY="(none)" || LATEST_DISPLAY="$LATEST"

echo "Current version in pyproject.toml : $CURRENT"
echo "Latest published GitHub release   : $LATEST_DISPLAY"
echo ""
read -rp "New version (X.Y.Z): " NEW_VERSION

# Must be valid semver.
if ! echo "$NEW_VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    echo "ERROR: '$NEW_VERSION' is not valid semver (expected X.Y.Z)."
    exit 1
fi

# Must differ from the current pyproject.toml version.
if [ "$NEW_VERSION" = "$CURRENT" ]; then
    echo "ERROR: $NEW_VERSION is already the version in pyproject.toml."
    exit 1
fi

# Must differ from the latest published release.
if [ -n "$LATEST" ] && [ "$NEW_VERSION" = "$LATEST" ]; then
    echo "ERROR: $NEW_VERSION is already the latest published release."
    exit 1
fi

# Must be strictly greater than the latest published release.
if [ -n "$LATEST" ]; then
    IS_GREATER=$(python3 -c "
a = tuple(int(x) for x in '$NEW_VERSION'.split('.'))
b = tuple(int(x) for x in '$LATEST'.split('.'))
print('yes' if a > b else 'no')
")
    if [ "$IS_GREATER" != "yes" ]; then
        echo "ERROR: $NEW_VERSION is not greater than the latest release ($LATEST)."
        exit 1
    fi
fi

TAG="v$NEW_VERSION"

# ---------------------------------------------------------------------------
# Confirmation
# ---------------------------------------------------------------------------

echo ""
echo "About to:"
echo "  1. Set version to $NEW_VERSION in pyproject.toml"
echo "  2. Commit: \"Release $TAG\""
echo "  3. Push commit to prerelease"
echo "  4. Create and push tag $TAG"
echo "     (GitHub Actions will create a draft release and build Linux wheels)"
echo "  5. Build macOS arm64 wheels locally and upload to the draft release"
echo ""
read -rp "Proceed? [yes/N]: " CONFIRM
[ "$CONFIRM" = "yes" ] || { echo "Aborted."; exit 0; }
echo ""

# Print a helpful message if anything fails from here on.
trap 'echo ""; echo "Script failed at the step above. The remaining steps can be run manually — see dev_scripts/README.md."' ERR

# ---------------------------------------------------------------------------
# Step 1/5 — Update pyproject.toml
# ---------------------------------------------------------------------------

echo "--- 1/5  Updating pyproject.toml ---"
python3 - <<PYEOF
import re
path = 'pyproject.toml'
txt = open(path).read()
new_txt = re.sub(
    r'^version = ".+"',
    'version = "$NEW_VERSION"',
    txt, count=1, flags=re.MULTILINE
)
assert new_txt != txt, "Version substitution had no effect — check pyproject.toml format."
open(path, 'w').write(new_txt)
PYEOF
echo "     version = \"$NEW_VERSION\""

# ---------------------------------------------------------------------------
# Step 2/5 — Commit
# ---------------------------------------------------------------------------

echo ""
echo "--- 2/5  Committing ---"
git add pyproject.toml
git commit -m "Release $TAG"

# ---------------------------------------------------------------------------
# Step 3/5 — Push commit
# ---------------------------------------------------------------------------

echo ""
echo "--- 3/5  Pushing commit to prerelease ---"
git push

# ---------------------------------------------------------------------------
# Step 4/5 — Tag and push
# ---------------------------------------------------------------------------

echo ""
echo "--- 4/5  Tagging and pushing $TAG ---"
git tag "$TAG"
git push origin "$TAG"
echo "     GitHub Actions is creating the draft release and building Linux wheels."

# ---------------------------------------------------------------------------
# Step 5/5 — Build macOS wheels locally
# ---------------------------------------------------------------------------

echo ""
echo "--- 5/5  Building macOS arm64 wheels ---"
dev_scripts/build_mac_wheels.sh "$TAG"

# ---------------------------------------------------------------------------
# Handoff
# ---------------------------------------------------------------------------

trap - ERR

REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)

echo ""
echo "============================================================"
echo "  Release $TAG is ready to review"
echo "============================================================"
echo ""
echo "Remaining steps:"
echo ""
echo "  1. Confirm all wheels are attached to the draft release"
echo "     (1 macOS arm64 + 2 Linux wheels per Python version, plus 1 sdist):"
echo "     https://github.com/$REPO/releases/tag/$TAG"
echo ""
echo "  2. Open a pull request from prerelease to master:"
echo "     gh pr create --base master --title \"Release $TAG\""
echo ""
echo "  3. After the PR merges, publish the draft release:"
echo "     Go to https://github.com/$REPO/releases/tag/$TAG"
echo "     Scroll to the bottom of the draft release page and click 'Publish release'."
echo ""
