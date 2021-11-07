#!/bin/bash
# This script destroys the conda environment named "svmbir" and uninstalls SVMBIR.
# It then creates an "svmbir" environment and reinstalls SVMBIR along with the documentation and demo requirements.

# Clean out old installation
source clean_svmbir.sh

# Destroy conda environement named svmbir and reinstall it
source reinstall_conda_environment.sh

# Install svmbir
source install_svmbir.sh

# Build documentation
source install_docs.sh


