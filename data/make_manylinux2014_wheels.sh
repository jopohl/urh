#!/bin/bash

AIRSPY_VERSION="1.0.9"
BLADERF_VERSION="2018.08"
LIMESUITE_VERSION="20.01.0"
SDRPLAY_VERSION="2.13"

echo -e '\n\033[92mInstalling dependencies...\033[0m'
yum -y install wget cmake cmake3 rtl-sdr-devel hackrf-devel uhd-devel
yum -y install https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm

echo -e '\n\033[92Compiling Airspy...\033[0m'
cd /tmp
wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz
tar xf v$AIRSPY_VERSION.tar.gz && rm v$AIRSPY_VERSION.tar.gz
cd /tmp/airspyone_host-$AIRSPY_VERSION
mkdir build_airspy && cd build_airspy
cmake .. && make -j$(nproc) && make install

echo -e '\n\033[92mCompiling BladeRF...\033[0m'
cd /tmp
wget https://github.com/Nuand/bladeRF/archive/$BLADERF_VERSION.tar.gz
tar xf $BLADERF_VERSION.tar.gz && rm $BLADERF_VERSION.tar.gz
cd /tmp/bladeRF-$BLADERF_VERSION
mkdir build_blade && cd build_blade
cmake3 .. && make -j$(nproc) && make install

echo -e '\n\033[92mCompiling LimeSuite...\033[0m'
cd /tmp
wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz
tar xf v$LIMESUITE_VERSION.tar.gz && rm v$LIMESUITE_VERSION.tar.gz
cd /tmp/LimeSuite-$LIMESUITE_VERSION
mkdir build_lime && cd build_lime
cmake3 .. && make -j$(nproc) && make install

echo -e '\n\033[92mInstalling sdrplay...\033[0m'
cd /tmp
wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O sdrplay.run
bash sdrplay.run --tar xf
mv mirsdrapi-rsp.h /usr/include
mv x86_64/* /usr/lib64
ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so

echo -e '\n\033[92mCompiling wheels...\033[0m'
for PYBIN in /opt/python/*/bin; do
     echo -e "\033[36mCompiling wheel for $PYBIN\033[0m"
    "${PYBIN}/pip" install -r /io/data/requirements.txt
    cd /io
    echo -e "\033[36mBuilding extentions for $PYBIN\033[0m"
    "${PYBIN}/python3" setup.py build_ext -j$(nproc)
    "${PYBIN}/pip" wheel --no-deps /io/ -w /wheelhouse/
done

# Bundle external libs into wheels
for whl in /wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done
