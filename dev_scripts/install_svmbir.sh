#!/bin/bash
# Install svmbir in editable mode together with all dev, docs, and demo dependencies.
# Does not remove an existing installation — run clean_svmbir.sh first if needed.

cd ..
git submodule update --init --recursive
pip install -e ".[dev,docs,demo]"
cd dev_scripts
