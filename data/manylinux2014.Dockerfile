FROM quay.io/pypa/manylinux2014_x86_64

RUN export AIRSPY_VERSION="1.0.9" \
 && export BLADERF_VERSION="2018.08" \
 && export LIMESUITE_VERSION="20.01.0" \
 && export SDRPLAY_VERSION="2.13" \
 && export RTLSDR_VERSION="0.6.0" \
 && yum -y install wget cmake3 hackrf-devel uhd-devel https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm \
 && wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz -O /tmp/airspy.tar.gz \
 && tar xf /tmp/airspy.tar.gz -C /tmp \
 && cmake3 -Wno-dev -S /tmp/airspyone_host-$AIRSPY_VERSION -B /tmp/build_airspy \
 && make -j$(nproc) -C /tmp/build_airspy  \
 && make -C /tmp/build_airspy install \
 && wget https://github.com/Nuand/bladeRF/archive/$BLADERF_VERSION.tar.gz -O /tmp/bladeRF.tar.gz \
 && tar xf /tmp/bladeRF.tar.gz -C /tmp \
 && cmake3 -Wno-dev -S /tmp/bladeRF-$BLADERF_VERSION/host -B /tmp/build_blade \
 && make -j$(nproc) -C /tmp/build_blade \
 && make -C /tmp/build_blade install \
 && wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz -O /tmp/lime.tar.gz \
 && tar xf /tmp/lime.tar.gz -C /tmp \
 && cmake3 -S /tmp/LimeSuite-$LIMESUITE_VERSION -B /tmp/build_lime \
 && make -j$(nproc) -C /tmp/build_lime \
 && make -C /tmp/build_lime install \
 && wget https://github.com/osmocom/rtl-sdr/archive/$RTLSDR_VERSION.tar.gz -O /tmp/rtlsdr.tar.gz \
 && tar xf /tmp/rtlsdr.tar.gz -C /tmp \
 && cmake3 -DDETACH_KERNEL_DRIVER=ON -S /tmp/rtl-sdr-$RTLSDR_VERSION -B /tmp/build_rtlsdr \
 && make -j$(nproc) -C /tmp/build_rtlsdr \
 && make -C /tmp/build_rtlsdr install \
 && wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O /tmp/sdrplay.run \
 && bash /tmp/sdrplay.run --tar xf -C /tmp \
 && mv /tmp/mirsdrapi-rsp.h /usr/include \
 && mv /tmp/x86_64/* /usr/lib64 \
 && ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so \
 && rm -rf /tmp/* \
 && yum clean all
