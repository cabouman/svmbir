#!/bin/bash
# This script is an alias for clean_install_conda_svmbir_docs.sh, which destroys the conda environment named "svmbir"
# and uninstalls svmbir, then creates an "svmbir" environment and reinstalls svmbir along with the documentation
# and demo requirements.

# Clean and install everything.  The optional argument can be set to -e to install the source in editable form.
source clean_install_conda_svmbir_docs.sh $1



