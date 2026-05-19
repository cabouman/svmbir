#!/bin/bash
set -euo pipefail
#
# Test-install svmbir from the GitHub release assets before publishing to PyPI.
#
# Downloads the wheels and sdist attached to the given tag's draft release,
# installs the appropriate wheel into a fresh conda environment, runs pytest,
# then cleans up.  Run this after cut_release.sh and before publishing the
# draft release.
#
# Usage (run from dev_scripts/ or the repo root):
#   ./test_pypi.sh v0.4.1

cd "$(dirname "$0")/.."

TAG=${1:?"Usage: test_pypi.sh <tag>  e.g.  ./test_pypi.sh v0.4.1"}
VERSION="${TAG#v}"

echo "=== Test-installing svmbir $VERSION from GitHub release assets ==="
echo ""

# Verify the gh CLI is authenticated; offer to log in if not.
if ! gh auth status &>/dev/null; then
    echo "gh CLI not authenticated — launching 'gh auth login' now ..."
    gh auth login
    if ! gh auth status &>/dev/null; then
        echo "ERROR: gh auth login did not succeed. Re-run this script to try again."
        exit 1
    fi
fi

# Download all wheels and the sdist from the release.
DIST_DIR=$(mktemp -d)
trap 'rm -rf "$DIST_DIR"' EXIT

echo "Downloading release assets for $TAG ..."
gh release download "$TAG" \
    --pattern "*.whl" \
    --pattern "*.tar.gz" \
    --dir "$DIST_DIR"

echo ""
echo "Downloaded assets:"
ls -lh "$DIST_DIR"
echo ""

# Pick the wheel that matches the current platform and Python version.
# On macOS arm64, cibuildwheel produces macosx_*_arm64 wheels.
PYVER=$(python3 -c "import sys; print(f'cp{sys.version_info.major}{sys.version_info.minor}')")
WHEEL=$(ls "$DIST_DIR"/svmbir-*-${PYVER}-*.whl 2>/dev/null | head -1 || true)

if [ -n "$WHEEL" ]; then
    INSTALL_TARGET="$WHEEL"
    echo "Selected wheel: $(basename "$WHEEL")"
else
    # Fall back to the sdist — builds from source, slower but platform-independent.
    SDIST=$(ls "$DIST_DIR"/svmbir-*.tar.gz 2>/dev/null | head -1 || true)
    if [ -z "$SDIST" ]; then
        echo "ERROR: No wheel matching $PYVER and no sdist found in release assets."
        echo "Available files:"
        ls "$DIST_DIR"
        exit 1
    fi
    INSTALL_TARGET="$SDIST"
    echo "No wheel matching $PYVER found — falling back to sdist: $(basename "$SDIST")"
fi
echo ""

# Create a clean conda environment, install, and test.
ENV_NAME="svmbir_release_test_$$"
echo "Creating clean conda environment $ENV_NAME ..."
conda create -y -n "$ENV_NAME" python=3.12 -q

echo "Installing $(basename "$INSTALL_TARGET") ..."
conda run -n "$ENV_NAME" pip install -q "$INSTALL_TARGET"

echo ""
echo "Smoke test — import and version check:"
conda run -n "$ENV_NAME" python -c "
import svmbir
print(f'  svmbir {svmbir.__version__} imported OK')
assert svmbir.__version__ == '$VERSION', \
    f'Version mismatch: expected $VERSION, got {svmbir.__version__}'
print('  Version matches tag.')
"

echo ""
echo "Running pytest ..."
conda run -n "$ENV_NAME" pip install -q pytest
conda run -n "$ENV_NAME" pytest svmbir/tests/ -v

echo ""
echo "Cleaning up conda environment ..."
conda remove -y -n "$ENV_NAME" --all -q

echo ""
echo "============================================================"
echo "  All tests passed for $TAG."
echo "  Ready to publish the draft release on GitHub."
echo "============================================================"
echo ""
echo "To publish (triggers automatic PyPI upload):"
echo "  1. Merge the prerelease -> master PR if you haven't already."
echo "  2. Go to https://github.com/cabouman/svmbir/releases/tag/$TAG"
echo "  3. Scroll to the bottom of the draft release and click 'Publish release'."
