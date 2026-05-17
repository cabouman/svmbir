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
if [[ "$(uname)" == "Darwin" ]]; then
    conda install -n svmbir -y -c conda-forge llvm-openmp
fi
cd dev_scripts

