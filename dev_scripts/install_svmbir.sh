#!/bin/bash
# This script just installs svmbir along with requirements of svmbir, demos, and documation.. 
# However, it does not remove the existing installation of svmbir.
# The optional argument can be set to -e to install the source in editable form.

cd ..
pip install -r requirements.txt
pip install .
pip install -r demo/requirements_demo.txt
pip install -r docs/requirements.txt 
cd dev_scripts

