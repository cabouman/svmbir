#!/bin/bash

# Builds the sdist and wheels
#
# RUN AS: source build_dist.sh
# NOT AS: ./build_dist.sh
# (otherwise it may not activate conda environments)
#
# NOTES:
#   * Principally for macOS wheels. For linux, build using 'manylinux' from docker image
#
#   * Currently supports Python 3.9-3.12
#
#   * Because we compile using numpy C API, need to set numpy minor version for build 
#     consistent with user environment version.
#     Build with numpy==1.26.3 appears compatible with >=1.26.0, allowing support of Python 3.9-3.12.
#
#   * macOS/x86_64: Run build on macOS 10.14 for binaries to be compatibile with macOS>=10.14.
#     Wheels are delocated to fix a library incompatibility across macOS>=10.14.
#
#   * macOS/arm64 (M1,M2): Wheels are delocated to include any linked libraries (OpenMP).
#

python_versions=("3.9" "3.10" "3.11" "3.12")
numpy_build_ver=1.26.3
CC=gcc

# check for a valid compiler
if ${CC} --version &> /dev/null; then
    ${CC} --version
else
    echo "error: compiler ${CC} not found"
    return 2> /dev/null || exit
fi

cd ..
/bin/rm -v -r dist build 2> /dev/null
/bin/rm -v -r svmbir.egg-info 2> /dev/null

echo "*********************************************************"
echo "**** Building wheels"
echo "**** Python ${python_versions[@]}"
echo "**** Compiler: ${CC}"
echo "*********************************************************"

for pyv in ${python_versions[@]}; do

    echo "**** Cleaning ****"
    /bin/rm -v -r svmbir.egg-info 2> /dev/null
    /bin/rm -v svmbir/interface_cy_c.c 2> /dev/null
    /bin/rm -v svmbir/*.so 2> /dev/null

    echo "**** Create environment ${pyv} *****"
    conda create --name sv${pyv} python=$pyv --yes
    conda activate sv${pyv}
    pip install numpy==$numpy_build_ver     # see note above about numpy version
    pip install -r requirements.txt
    pip install setuptools

    echo "****"
    echo "**** Building wheel for python ${pyv}, CC=${CC} "
    echo "****"
    CC=$CC python setup.py bdist_wheel

    conda deactivate
    conda remove --name sv${pyv} --all --yes
done

echo "*************** sdist ******************"
/bin/rm -v -r svmbir.egg-info 2> /dev/null
/bin/rm -v svmbir/interface_cy_c.c 2> /dev/null
/bin/rm -v svmbir/*.so 2> /dev/null
pyv=3.10
conda create --name sv${pyv} python=$pyv --yes
conda activate sv${pyv}
pip install -r requirements.txt
pip install setuptools
python setup.py sdist

# Delocate to add libgomp.dylib to wheel (macOS only)
if [ $(uname -s) = "Darwin" ]; then
    pip install delocate
    echo "******* Delocating wheels *******"
    cd dist
    for f in *.whl; do
        delocate-wheel -w fixed_wheels -v $f
        mv fixed_wheels/$f .
    done
    rm -f -r fixed_wheels
    cd ..
fi

conda deactivate
conda remove --name sv${pyv} --all --yes

cd dev_scripts

