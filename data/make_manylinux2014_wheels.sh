#!/bin/bash

AIRSPY_VERSION="1.0.9"
BLADERF_VERSION="2018.08"
LIMESUITE_VERSION="20.01.0"
SDRPLAY_VERSION="2.13"

echo -e '\n\033[92mInstalling dependencies...\033[0m'
yum -y install wget cmake3 rtl-sdr-devel hackrf-devel uhd-devel
yum -y install https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm

build_airspy() {
  echo -e '\n\033[92Compiling Airspy...\033[0m'
  wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz -O /tmp/airspy.tar.gz
  tar xf /tmp/airspy.tar.gz -C /tmp
  cmake3 -S /tmp/airspyone_host-$AIRSPY_VERSION -B /tmp/build_airspy
  make -C /tmp/build_airspy
  make -C /tmp/build_airspy install
}

build_bladerf() {
  echo -e '\n\033[92mCompiling BladeRF...\033[0m'
  wget https://github.com/Nuand/bladeRF/archive/$BLADERF_VERSION.tar.gz -O /tmp/bladeRF.tar.gz
  tar xf /tmp/bladeRF.tar.gz -C /tmp
  cd /tmp/bladeRF-$BLADERF_VERSION || return
  cmake3 -S /tmp/bladeRF-$BLADERF_VERSION -B /tmp/build_blade
  make -C /tmp/build_blade -j2
  make -C /tmp/build_blade install
}

build_limesdr() {
  echo -e '\n\033[92mCompiling LimeSuite...\033[0m'
  wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz -O /tmp/lime.tar.gz
  tar xf /tmp/lime.tar.gz -C /tmp
  cmake3 -S /tmp/LimeSuite-$LIMESUITE_VERSION -B /tmp/build_lime
  make -C /tmp/build_lime -j2
  make -C /tmp/build_lime install
}

build_sdrplay() {
  echo -e '\n\033[92mInstalling sdrplay...\033[0m'
  wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O /tmp/sdrplay.run
  bash /tmp/sdrplay.run --tar xf -C /tmp
  mv /tmp/mirsdrapi-rsp.h /usr/include
  mv /tmp/x86_64/* /usr/lib64
  ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so
}

build_airspy &
build_bladerf &
build_limesdr &
build_sdrplay &
wait

echo -e '\n\033[92mCompiling wheels...\033[0m'
for PYBIN in /opt/python/*/bin; do
     echo -e "\033[36mCompiling wheel for $PYBIN\033[0m"
    "${PYBIN}/pip" install -r /io/data/requirements.txt
    cd /io || return
    echo -e "\033[36mBuilding extentions for $PYBIN\033[0m"
    "${PYBIN}/python3" setup.py build_ext "-j$(nproc)"
    "${PYBIN}/pip" wheel --no-deps /io/ -w /wheelhouse/
done

# Bundle external libs into wheels
for whl in /wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done
