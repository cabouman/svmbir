#!/bin/bash

conda deactivate &&

conda remove env --name svmbir --all &&

conda env create -f environment.yml &&

conda activate svmbir &&

pip install -r demo/requirements_demo.txt

source clean_svmbir &&

pip install . &&

cd demo &&

python demo_2D_shepp_logan.py

cd .. 
