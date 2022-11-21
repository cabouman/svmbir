#!/bin/bash

# Builds the sdist and wheels for python 3.7-3.10
#
# RUN AS: source build_dist.sh
# NOT AS: ./build_dist.sh
# (otherwise it may not activate conda environments)
#
# NOTES:
#   * Principally for macOS wheels. For linux, build using 'manylinux' from docker image
#
#   * Building with numpy==1.21.6, wheels appear compatible with numpy 1.21-1.23.5 at least
#     The install requirement numpy>=1.21 then allows support of python 3.7-3.10
#
#   * macOS/x86_64: Run build on macOS 10.14 for binaries to be compatibile with macOS>=10.14.
#     Wheels are delocated to fix a library incompatibility across macOS>=10.14.
#
#   * macOS/arm64 (M1,M2): CHECK THIS: Limited to python >= 3.8. 'delocation' section will be skipped.
#

python_versions=("3.7" "3.8" "3.9" "3.10")
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
    # see note above about numpy version
    pip install numpy==1.21.6
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
pyv=3.8
conda create --name sv${pyv} python=$pyv --yes
conda activate sv${pyv}
pip install -r requirements.txt
pip install setuptools
python setup.py sdist

# section for pre-M1 macs only
if [ $(uname -s) = "Darwin" ] && [ $(uname -m) = "x86_64" ]; then
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

