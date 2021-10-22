#!/bin/bash
# This script destroys the conda environment named "svmbir" and uninstalls SVMBIR.
# It then creates an "svmbir" environment and reinstalls SVMBIR along with the documentation and demo requirements.

# Clean out old installation
source clean_svmbir.sh

# Create and activate new conda environment
cd ..
conda deactivate
conda remove env --name svmbir --all
conda create --name svmbir python=3.8
conda activate svmbir

# Install requirements and package
pip install -r requirements.txt
pip install .
pip install -r demo/requirements_demo.txt
pip install -r docs/requirements.txt 

# Build documentation
cd docs
SVMBIR_BUILD_DOCS=true make html
cd ../dev_scripts

