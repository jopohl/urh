#!/bin/bash

AIRSPY_VERSION="1.0.9"
BLADERF_VERSION="2019.07"
LIMESUITE_VERSION="20.01.0"
SDRPLAY_VERSION="2.13"

yum -y install wget cmake cmake3 rtl-sdr-devel hackrf-devel uhd-devel
yum -y install https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm

cd /tmp
wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz
tar xf v$AIRSPY_VERSION.tar.gz && rm v$AIRSPY_VERSION.tar.gz
cd /tmp/airspyone_host-$AIRSPY_VERSION
mkdir build_airspy && cd build_airspy
cmake .. && make -j$(nproc) && make install

cd /tmp
git clone https://github.com/Nuand/bladeRF
cd bladeRF
git checkout $BLADERF_VERSION
mkdir build && cd build
cmake .. && make -j$(nproc) && make install

cd /tmp
wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz
tar xf v$LIMESUITE_VERSION.tar.gz && rm v$LIMESUITE_VERSION.tar.gz
cd /tmp/LimeSuite-$LIMESUITE_VERSION
mkdir build_lime && cd build_lime
cmake3 .. && make -j$(nproc) && make install

cd /tmp
wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O sdrplay.run
bash sdrplay.run --tar xf
mv mirsdrapi-rsp.h /usr/include
mv x86_64/* /usr/lib64
