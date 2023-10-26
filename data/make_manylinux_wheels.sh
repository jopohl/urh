#!/bin/bash

# for adapted jopohl/urh_manylinux
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib64/:/usr/local/lib/:/usr/lib64/


touch /tmp/urh_releasing
for PYBIN in /opt/python/*$PYVER*/bin; do   # for all if PYVER not set
    echo -e "\033[1mInstalling requirements for $PYBIN\033[0m"
    "${PYBIN}/pip" install -r /io/data/requirements.txt

    cd /io || return
    echo -e "\033[1mBuilding extentions for $PYBIN\033[0m"
    "${PYBIN}/python3" setup.py build_ext "-j$(nproc)"

    echo -e "\033[1mBuilding wheel for $PYBIN\033[0m"
    "${PYBIN}/pip" wheel --no-deps /io/ -w /wheelhouse/
done

# Bundle external libs into wheels
echo -e '\033[92mRepairing wheels...\033[0m'
for whl in /wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done
