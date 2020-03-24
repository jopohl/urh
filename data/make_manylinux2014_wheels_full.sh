#!/bin/bash

# for plain quay.io/pypa/manylinux2014_x86_64

AIRSPY_VERSION="1.0.9"
BLADERF_VERSION="2018.08"
LIMESUITE_VERSION="20.01.0"
SDRPLAY_VERSION="2.13"
RTLSDR_VERSION="0.6.0"

echo -e '\033[92mInstalling dependencies...\033[0m'
yum -y -q install wget cmake3 hackrf-devel uhd-devel\
       https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm

build_airspy() {
   &> /dev/null
  tar xf /tmp/airspy.tar.gz -C /tmp
  cmake3 -Wno-dev -S /tmp/airspyone_host-$AIRSPY_VERSION -B /tmp/build_airspy > /dev/null
  make --silent -C /tmp/build_airspy > /dev/null
  make --silent -C /tmp/build_airspy install > /dev/null
}

build_bladerf() {
  wget https://github.com/Nuand/bladeRF/archive/$BLADERF_VERSION.tar.gz -O /tmp/bladeRF.tar.gz &> /dev/null
  tar xf /tmp/bladeRF.tar.gz -C /tmp
  cmake3 -Wno-dev -S /tmp/bladeRF-$BLADERF_VERSION/host -B /tmp/build_blade > /dev/null
  make --silent -C /tmp/build_blade > /dev/null
  make --silent -C /tmp/build_blade install > /dev/null
}

build_limesdr() {
  wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz -O /tmp/lime.tar.gz &> /dev/null
  tar xf /tmp/lime.tar.gz -C /tmp
  cmake3 -Wno-dev -S /tmp/LimeSuite-$LIMESUITE_VERSION -B /tmp/build_lime > /dev/null
  make --silent -C /tmp/build_lime > /dev/null
  make --silent -C /tmp/build_lime install > /dev/null
}

build_rtlsdr() {
  wget https://github.com/osmocom/rtl-sdr/archive/$RTLSDR_VERSION.tar.gz -O /tmp/rtlsdr.tar.gz &> /dev/null
  tar xf /tmp/rtlsdr.tar.gz -C /tmp
  cmake3 -Wno-dev -DDETACH_KERNEL_DRIVER=ON -S /tmp/rtl-sdr-$RTLSDR_VERSION -B /tmp/build_rtlsdr > /dev/null
  make --silent -C /tmp/build_rtlsdr > /dev/null
  make --silent -C /tmp/build_rtlsdr install > /dev/null
}

build_sdrplay() {
  wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O /tmp/sdrplay.run &> /dev/null
  bash /tmp/sdrplay.run --tar xf -C /tmp
  mv /tmp/mirsdrapi-rsp.h /usr/include
  mv /tmp/x86_64/* /usr/lib64
  ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so
}

echo -e '\033[92mCompiling SDR libs...\033[0m'
build_airspy &
build_bladerf &
build_limesdr &
build_rtlsdr &
build_sdrplay &
wait

touch /tmp/urh_releasing
for PYBIN in /opt/python/*/bin; do
    echo -e "\033[1mInstalling requirements for $PYBIN\033[0m"
    "${PYBIN}/pip" install -r /io/data/requirements.txt > /dev/null

    cd /io || return
    echo -e "\033[1mBuilding extentions for $PYBIN\033[0m"
    "${PYBIN}/python3" setup.py build_ext "-j$(nproc)" | grep --color=always "Skipping"

    echo -e "\033[1mBuilding wheel for $PYBIN\033[0m"
    "${PYBIN}/pip" wheel --no-deps /io/ -w /wheelhouse/ > /dev/null
done

# Bundle external libs into wheels
echo -e '\033[92mRepairing wheels...\033[0m'
for whl in /wheelhouse/*.whl; do
    auditwheel repair "$whl" -w /io/dist/
done
