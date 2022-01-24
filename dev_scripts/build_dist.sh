#!/bin/bash

# Builds the sdist and wheels for python 3.7, 3.8, 3.9
#
# RUN AS: source build_dist.sh
# NOT AS: ./build_dist.sh
# (otherwise it may not activate conda environments)
#
# IMPORTANT: If building macOS wheels, run script on macOS 10.14 so that binaries will be
# compatibile with macOS>=10.14
#
# Wheels are delocated to fix a library incompatibility across macOS >= 10.14.
#

# Set these accordingly:

python_versions=("3.7" "3.8" "3.9")
CC=gcc

# check for a valid compiler
if ${CC} --version &> /dev/null; then
    ${CC} --version
else
    echo "error: compiler ${CC} not found"
    return 2> /dev/null || exit
fi

cd ..
/bin/rm -fr dist build
/bin/rm -r svmbir.egg-info

echo "*********************************************************"
echo "**** Building wheels"
echo "**** Python ${python_versions[@]}"
echo "**** Compiler: ${CC}"
echo "*********************************************************"

for pyv in ${python_versions[@]}; do
    echo "*********** Create environment ${pyv} *************"
    conda create --name sv${pyv} python=$pyv --yes
    conda activate sv${pyv}
    pip install -r requirements.txt
    pip install setuptools

    echo "****"
    echo "**** Building wheel for python ${pyv}, CC=${CC} "
    echo "****"
    CC=$CC python setup.py bdist_wheel

    conda deactivate
    conda remove --name sv${pyv} --all --yes
done


pyv=3.8
conda create --name sv${pyv} python=$pyv --yes
conda activate sv${pyv}
pip install -r requirements.txt
pip install setuptools delocate

echo "*************** sdist ******************"
python setup.py sdist

echo "*************** Delocating wheels ******************"
cd dist
for f in *.whl; do
    delocate-wheel -w fixed_wheels -v $f
    mv fixed_wheels/$f .
done
rm -f -r fixed_wheels
cd ..

conda deactivate
conda remove --name sv${pyv} --all --yes


cd dev_scripts

