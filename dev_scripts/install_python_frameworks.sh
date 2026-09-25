#!/bin/bash
set -euo pipefail
#
# Install official Python.org framework builds required by cibuildwheel.
#
# cibuildwheel builds portable macOS wheels using the official Python.org
# installers, which live in /Library/Frameworks/Python.framework/Versions/.
# These are entirely separate from conda and must be installed system-wide.
# This is a one-time setup per machine.
#
# The script finds the latest patch release of each supported minor version
# that has a macOS installer available, and installs it. Already-installed
# versions are skipped.
#
# sudo is NOT needed to run this script — it calls 'sudo installer' internally
# only for the installation step and will prompt for your password then.
#
# Usage (run from dev_scripts/ or anywhere):
#   ./install_python_frameworks.sh

# Keep this list in sync with python-version in .github/workflows/ci.yml
# and the build setting in [tool.cibuildwheel] in pyproject.toml.
MINOR_VERSIONS=(3.10 3.11 3.12 3.13 3.14)

echo "=== Installing Python.org framework builds for cibuildwheel ==="
echo ""

for MINOR in "${MINOR_VERSIONS[@]}"; do

    # Skip if this minor version is already installed.
    if [ -d "/Library/Frameworks/Python.framework/Versions/$MINOR" ]; then
        echo "Python $MINOR: already installed — skipping."
        continue
    fi

    echo "Python $MINOR: finding latest patch release with a macOS installer ..."

    # Get all patch versions for this minor from the FTP index, newest first.
    # The || true prevents set -e from exiting when grep finds no matches (exit 1).
    ALL_PATCHES=$(curl -s "https://www.python.org/ftp/python/" \
                  | grep -oE "${MINOR//\./\\.}\.[0-9]+" \
                  | sort -V | tail -r || true)

    PKG_NAME=""
    PATCH=""

    # Walk from newest to oldest until we find a version that has a macOS pkg.
    while IFS= read -r CANDIDATE; do
        FOUND=$(curl -s "https://www.python.org/ftp/python/${CANDIDATE}/" \
                | grep -oE "python-${CANDIDATE//\./\\.}-macos[0-9a-z]+\.pkg" \
                | head -1 || true)
        if [ -n "$FOUND" ]; then
            PATCH="$CANDIDATE"
            PKG_NAME="$FOUND"
            break
        fi
    done <<< "$ALL_PATCHES"

    if [ -z "$PATCH" ]; then
        echo "Python $MINOR: WARNING — no macOS installer found on python.org. Skipping."
        continue
    fi

    URL="https://www.python.org/ftp/python/${PATCH}/${PKG_NAME}"
    DEST="/tmp/${PKG_NAME}"

    echo "Python $MINOR: downloading $PATCH ($PKG_NAME) ..."
    curl -# -o "$DEST" "$URL"

    # Verify the download is actually a pkg (xar archive), not a 404 HTML page.
    if ! file "$DEST" | grep -q "xar archive"; then
        echo "Python $MINOR: ERROR — downloaded file is not a valid package. Skipping."
        rm -f "$DEST"
        continue
    fi

    echo "Python $MINOR: installing (requires sudo) ..."
    sudo installer -pkg "$DEST" -target /
    rm -f "$DEST"
    echo "Python $MINOR: installed."
    echo ""

done

echo "Done. Installed versions:"
ls /Library/Frameworks/Python.framework/Versions/ 2>/dev/null | grep -E '^3\.' | sort -V || true
echo ""
echo "You can now run ./test_release.sh or ./cut_release.sh."
