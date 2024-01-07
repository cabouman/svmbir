#!/bin/bash

# Need manylinux image. To download:
#       sudo docker pull quay.io/pypa/manylinux2014_x86_64 
# Open a container:
#       sudo docker run -it quay.io/pypa/manylinux2014_x86_64 bash
# In another terminal, copy repo into container:
#       sudo docker ps      # get CONTAINER ID
#       sudo docker cp . <CONTAINER_ID>:/io
# In docker terminal, enter /io and run:
#       ./manylinux.sh      # DON'T source this, otherwise an exitcode 1 will close shell
# In host terminal, copy wheels out:
#       sudo rm -fr wheelhouse
#       sudo docker cp <CONTAINER_ID>:/io/wheelhouse ./wheelhouse
#       sudo chown -R $USER wheelhouse
#       sudo chgrp -R $USER wheelhouse

set -e -u -x

function repair_wheel {
    wheel="$1"
    if ! auditwheel show "$wheel"; then
        echo "Skipping non-platform wheel $wheel"
    else
        auditwheel repair "$wheel" --plat "$AUDITWHEEL_PLAT" -w /io/wheelhouse/
    fi
}

/bin/rm -frv wheelhouse 2> /dev/null

# Compile wheels
#for PYBIN in /opt/python/*/bin; do
#for PYBIN in /opt/python/{cp37,cp38,cp39,cp310,pp37,pp38,pp39}*/bin; do
for PYBIN in /opt/python/{cp39,cp310,cp311}*/bin; do
    echo "***"
    echo "*** building for $PYBIN"
    #"${PYBIN}/pip" install -r /io/dev_scripts/dev-requirements.txt
    "${PYBIN}/pip" install numpy==1.26.3    # build with 1.26.3 seems compatible w/ numpy>=1.26
    CC=gcc "${PYBIN}/pip" wheel /io/ --no-deps -w wheelhouse/
    #CC=gcc "${PYBIN}/python" setup.py bdist_wheel
done

# Bundle external shared libraries into the wheels
for whl in wheelhouse/*.whl; do
    echo "***"
    echo "*** repairing $whl"
    repair_wheel "$whl"
    /bin/rm -v $whl
done

# Install packages and test
#for PYBIN in /opt/python/*/bin/; do
#    "${PYBIN}/pip" install python-manylinux-demo --no-index -f /io/wheelhouse
#    (cd "$HOME"; "${PYBIN}/nosetests" pymanylinuxdemo)
#done
