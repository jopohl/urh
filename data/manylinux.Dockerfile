FROM quay.io/pypa/manylinux_2_28_x86_64

RUN yum -y install wget blas libusb-devel fftw-devel cmake3 boost-devel https://github.com/analogdevicesinc/libiio/releases/download/v0.19/libiio-0.19.g5f5af2e-centos-7-x86_64.rpm
RUN export AIRSPY_VERSION="1.0.9" \
 && export BLADERF_VERSION="2022.11" \
 && export LIMESUITE_VERSION="20.01.0" \
 && export HACKRF_VERSION="v2023.01.1" \
 && export SDRPLAY_VERSION="2.13" \
 && export RTLSDR_VERSION="0.6.0" \
 && export UHD_VERSION="4.5.0.0" \
 # HackRF
 && git clone --branch $HACKRF_VERSION --depth 1 https://github.com/greatscottgadgets/hackrf /tmp/hackrf-$HACKRF_VERSION \
 && cmake3 -Wno-dev -S /tmp/hackrf-$HACKRF_VERSION/host -B /tmp/build_hackrf \
 && make -j$(nproc) -C /tmp/build_hackrf \
 &&  make -C /tmp/build_hackrf install \
 # UHD
 && wget https://github.com/EttusResearch/uhd/archive/v$UHD_VERSION.tar.gz -O /tmp/uhd.tar.gz \
 && tar xf /tmp/uhd.tar.gz -C /tmp \
 && python3.10 -m pip install mako \
 && cmake3 -DBOOST_INCLUDEDIR=/usr/include/boost/ -DBOOST_LIBRARYDIR=/usr/lib64/boost/ -DENABLE_EXAMPLES=OFF -DENABLE_UTILS=OFF -DENABLE_C_API=ON -DENABLE_TESTS=OFF -DENABLE_MAN_PAGES=OFF -S /tmp/uhd-$UHD_VERSION/host -B /tmp/build_uhd \
 && make -j$(nproc) -C /tmp/build_uhd \
 && make -C /tmp/build_uhd install \
 # AirSpy
 && wget https://github.com/airspy/airspyone_host/archive/v$AIRSPY_VERSION.tar.gz -O /tmp/airspy.tar.gz \
 && tar xf /tmp/airspy.tar.gz -C /tmp \
 && cmake3 -Wno-dev -S /tmp/airspyone_host-$AIRSPY_VERSION -B /tmp/build_airspy \
 && make -j$(nproc) -C /tmp/build_airspy  \
 && make -C /tmp/build_airspy install \
 # BladeRF
 && git clone --branch $BLADERF_VERSION --recursive https://github.com/Nuand/bladeRF /tmp/bladeRF-$BLADERF_VERSION \
 && cmake -S /tmp/bladeRF-$BLADERF_VERSION/host -B /tmp/build_blade \
 && make -j$(nproc) -C /tmp/build_blade \
 && make -C /tmp/build_blade install \
 # Lime
 && wget https://github.com/myriadrf/LimeSuite/archive/v$LIMESUITE_VERSION.tar.gz -O /tmp/lime.tar.gz \
 && tar xf /tmp/lime.tar.gz -C /tmp \
 && cmake -S /tmp/LimeSuite-$LIMESUITE_VERSION -B /tmp/build_lime \
 && make -j$(nproc) -C /tmp/build_lime \
 && make -C /tmp/build_lime install \
 # RTLSDR
 && wget https://github.com/osmocom/rtl-sdr/archive/$RTLSDR_VERSION.tar.gz -O /tmp/rtlsdr.tar.gz \
 && tar xf /tmp/rtlsdr.tar.gz -C /tmp \
 && cmake -DDETACH_KERNEL_DRIVER=ON -S /tmp/rtl-sdr-$RTLSDR_VERSION -B /tmp/build_rtlsdr \
 && make -j$(nproc) -C /tmp/build_rtlsdr \
 && make -C /tmp/build_rtlsdr install \
 # SDRPLAY
 && wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-$SDRPLAY_VERSION.1.run -O /tmp/sdrplay.run \
 && bash /tmp/sdrplay.run --tar xf -C /tmp \
 && mv /tmp/mirsdrapi-rsp.h /usr/include \
 && mv /tmp/x86_64/* /usr/lib64 \
 && ln -s /usr/lib64/libmirsdrapi-rsp.so.$SDRPLAY_VERSION /usr/lib64/libmirsdrapi-rsp.so \
 && rm -rf /tmp/* \
 && yum clean all
