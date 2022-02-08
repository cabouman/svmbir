#!/bin/bash
#
# Tests from pypi or testpypi
#
# RUN AS: source test_pypi.sh
# NOT AS: ./test_pypi.sh
# (otherwise it may not activate conda environments)
#
# Set these accordingly:

python_versions=("3.7" "3.8" "3.9")
svmbir_version=0.2.7

echo "*********************************************************"
echo "**** Test install "
echo "**** Python ${python_versions[@]}"
echo "*********************************************************"

for pyv in ${python_versions[@]}; do
    echo "*********** Create environment ${pyv} *************"
    conda create --name sv${pyv} python=$pyv --yes
    conda activate sv${pyv}

    echo "*********** Installing svmbir ${svmbir_version} *************"
    #pip install -i https://test.pypi.org/simple/ svmbir==$svmbir_version
    pip install svmbir==$svmbir_version
    pip install -r ../demo/requirements_demo.txt

    echo "**** Spinning "
    python -c "import svmbir"
    echo "**** Running demo "
    python ../demo/demo_2D_microscopy.py

    echo "**** Removing env "
    conda deactivate
    conda remove --name sv${pyv} --all --yes
done


