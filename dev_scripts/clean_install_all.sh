#!/bin/bash
# This script destroys the conda environment named "svmbir" and uninstalls svmbir.
# It then creates an "svmbir" environment and reinstalls svmbir along with the documentation and demo requirements.

# Clean out old installation
source clean_svmbir.sh

# Destroy conda environement named svmbir and reinstall it
source install_conda_environment.sh

# Install svmbir
source install_svmbir.sh

# Build documentation
source install_docs.sh


