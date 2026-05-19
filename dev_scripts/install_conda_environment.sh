#!/bin/bash
# This script destroys the conda environment named "svmbir" and reinstall it.

# On macOS, Xcode Command Line Tools are required for clang, git, and SDK headers.
if [[ "$(uname)" == "Darwin" ]]; then
    if ! xcode-select -p &>/dev/null; then
        echo ""
        echo "ERROR: Xcode Command Line Tools are not installed."
        echo "Run the following command and follow the prompts, then retry:"
        echo ""
        echo "    xcode-select --install"
        echo ""
        return 1
    fi
fi

# Create and activate new conda environment
cd ..
conda deactivate
conda remove -y --name svmbir --all
conda create -y --name svmbir python=3.12
conda activate svmbir

# macOS: llvm-openmp is required for OpenMP support with Apple Clang.
if [[ "$(uname)" == "Darwin" ]]; then
    conda install -n svmbir -y -c conda-forge llvm-openmp
fi

# gh (GitHub CLI) — used by cut_release.sh and build_mac_wheels.sh to create
# and upload to GitHub Releases. 'gh auth login' must be run once after install.
conda install -n svmbir -y -c conda-forge gh

# cibuildwheel — used by build_mac_wheels.sh to build macOS wheels locally.
pip install cibuildwheel==2.22.0

cd dev_scripts

