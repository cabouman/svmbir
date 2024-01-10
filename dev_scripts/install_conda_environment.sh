#!/bin/bash
# This script destroys the conda environment named "svmbir" and reinstall it.

# Create and activate new conda environment
cd ..
conda deactivate
conda remove env --name svmbir --all
conda create --name svmbir python=3.10
conda activate svmbir
cd dev_scripts

