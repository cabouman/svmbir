#!/bin/bash
# This script installs the documentation.
# You can view documentation pages from svmbir/docs/build/index.html .

# Build documentation
cd ../docs
SVMBIR_BUILD_DOCS=true make html
cd ../dev_scripts
