#!/bin/bash
#
# Tests from pypi or testpypi
#
# RUN AS: source test_pypi.sh
# NOT AS: ./test_pypi.sh
# (otherwise it may not activate conda environments)
#
# Set these accordingly:

python_versions=("3.8" "3.9" "3.10")
svmbir_version=0.3.0

echo "*********************************************************"
echo "**** Test install "
echo "**** Python ${python_versions[@]}"
echo "*********************************************************"

cd ..

for pyv in ${python_versions[@]}; do
    echo "*********** Create environment ${pyv} *************"
    conda create --name sv${pyv} python=$pyv --yes
    conda activate sv${pyv}

    echo "*********** Installing svmbir ${svmbir_version} *************"
    pip install --no-cache-dir -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple svmbir==$svmbir_version
    #pip install --no-cache-dir svmbir==$svmbir_version

    cd demo
    echo "**** Spinning "
    python -c "import svmbir"
    echo "**** Running demo "
    pip install -r requirements_demo.txt
    python demo_2D_microscopy.py
    cd ..

    echo "**** Install inplace and run pytest"
    /bin/rm -v -r build dist 2> /dev/null
    /bin/rm -v -r svmbir.egg-info 2> /dev/null
    /bin/rm -v svmbir/interface_cy_c.c 2> /dev/null
    /bin/rm -v svmbir/*.so 2> /dev/null
    pip install -r requirements.txt
    CC=gcc python setup.py build_ext --inplace
    pytest

    echo "**** Removing env "
    conda deactivate
    conda remove --name sv${pyv} --all --yes
done

cd dev_scripts

