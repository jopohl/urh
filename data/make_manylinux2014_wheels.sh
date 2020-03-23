#!/bin/bash

AIRSPY_VERSION="1.0.9"
BLADERF_VERSION="2018.08"
LIMESUITE_VERSION="20.01.0"
SDRPLAY_VERSION="2.13"

echo -e '\033[92mInstalling dependencies...\033[0m'
start=$SECONDS
yum -y -q install wget cmake3 rtl-sdr-devel hackrf-devel uhd-devel\
       https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm
echo -e "\033[93mInstalling dependencies took $(( $SECONDS - start )) seconds\033[0m"

build_airspy() {
  wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz -O /tmp/airspy.tar.gz &> /dev/null
  tar xf /tmp/airspy.tar.gz -C /tmp
  cmake3 -S /tmp/airspyone_host-$AIRSPY_VERSION -B /tmp/build_airspy > /dev/null
  make --silent -C /tmp/build_airspy > /dev/null
  make --silent -C /tmp/build_airspy install > /dev/null
}

build_bladerf() {
  wget https://github.com/Nuand/bladeRF/archive/$BLADERF_VERSION.tar.gz -O /tmp/bladeRF.tar.gz &> /dev/null
  tar xf /tmp/bladeRF.tar.gz -C /tmp
  cmake3 -S /tmp/bladeRF-$BLADERF_VERSION -B /tmp/build_blade > /dev/null
  make --silent -C /tmp/build_blade > /dev/null
  make --silent -C /tmp/build_blade install > /dev/null
}

build_limesdr() {
  wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz -O /tmp/lime.tar.gz &> /dev/null
  tar xf /tmp/lime.tar.gz -C /tmp
  cmake3 -S /tmp/LimeSuite-$LIMESUITE_VERSION -B /tmp/build_lime > /dev/null
  make --silent -C /tmp/build_lime > /dev/null
  make --silent -C /tmp/build_lime install > /dev/null
}

build_sdrplay() {
  wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O /tmp/sdrplay.run &> /dev/null
  bash /tmp/sdrplay.run --tar xf -C /tmp
  mv /tmp/mirsdrapi-rsp.h /usr/include
  mv /tmp/x86_64/* /usr/lib64
  ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so
}

start=$SECONDS
build_airspy &
build_bladerf &
build_limesdr &
build_sdrplay &
wait
echo -e "\033[93mCompiling SDR libraries took $(( $SECONDS - start )) seconds\033[0m"

start=$SECONDS
for PYBIN in /opt/python/*/bin; do
    start1=$SECONDS
    echo -e "\033[36mInstalling requirements for $PYBIN\033[0m"
    "${PYBIN}/pip" install -r /io/data/requirements.txt > /dev/null
    echo -e "\033[96mFinished after $(( $SECONDS - start1 )) seconds\033[0m"

    start1=$SECONDS
    cd /io || return
    echo -e "\033[36mBuilding extentions for $PYBIN\033[0m"
    "${PYBIN}/python3" setup.py build_ext "-j$(nproc)" > /dev/null
    echo -e "\033[96mFinished after $(( $SECONDS - start1 )) seconds\033[0m"

    start1=$SECONDS
    echo -e "\033[36mBuilding wheel for $PYBIN\033[0m"
    "${PYBIN}/pip" wheel --no-deps /io/ -w /wheelhouse/ > /dev/null
    echo -e "\033[96mFinished after $(( $SECONDS - start1 )) seconds\033[0m"
done

echo -e "\033[93mBuilding wheels took $(( $SECONDS - start )) seconds\033[0m"
wait

# Bundle external libs into wheels
start=$SECONDS
for whl in /wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/dist/ &
done
wait
echo -e "\033[93mRepairing wheels took $(( $SECONDS - start )) seconds\033[0m"
