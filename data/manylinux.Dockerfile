FROM quay.io/pypa/manylinux_2_28_x86_64

# Define SDR library versions
ARG AIRSPY_VERSION="1.0.9"
ARG BLADERF_VERSION="2022.11"
ARG LIMESUITE_VERSION="20.01.0"
ARG HACKRF_VERSION="v2023.01.1"
ARG SDRPLAY_VERSION="3.15"
ARG RTLSDR_VERSION="0.6.0"
ARG UHD_VERSION="4.5.0.0"
ARG LIBIIO_VERSION="0.19"

# Install system dependencies and libiio
RUN yum -y install \
    wget \
    blas \
    libusb-devel \
    fftw-devel \
    cmake3 \
    boost-devel \
    python3-pip \
    https://github.com/analogdevicesinc/libiio/releases/download/v${LIBIIO_VERSION}/libiio-${LIBIIO_VERSION}.g5f5af2e-centos-7-x86_64.rpm \
    && yum clean all

# Build and install HackRF
RUN git clone --branch ${HACKRF_VERSION} --depth 1 \
        https://github.com/greatscottgadgets/hackrf /tmp/hackrf \
    && cmake3 -Wno-dev -S /tmp/hackrf/host -B /tmp/build_hackrf \
    && make -j$(nproc) -C /tmp/build_hackrf \
    && make -C /tmp/build_hackrf install \
    && rm -rf /tmp/hackrf /tmp/build_hackrf

# Build and install UHD
RUN wget -nv https://github.com/EttusResearch/uhd/archive/v${UHD_VERSION}.tar.gz -O /tmp/uhd.tar.gz \
    && tar xf /tmp/uhd.tar.gz -C /tmp \
    && python3.12 -m pip install --no-cache-dir mako==1.1.3 \
    && cmake3 \
        -DBOOST_INCLUDEDIR=/usr/include/boost/ \
        -DBOOST_LIBRARYDIR=/usr/lib64/boost/ \
        -DENABLE_EXAMPLES=OFF \
        -DENABLE_UTILS=OFF \
        -DENABLE_C_API=ON \
        -DENABLE_TESTS=OFF \
        -DENABLE_MAN_PAGES=OFF \
        -S /tmp/uhd-${UHD_VERSION}/host \
        -B /tmp/build_uhd \
    && make -j$(nproc) -C /tmp/build_uhd \
    && make -C /tmp/build_uhd install \
    && rm -rf /tmp/uhd* /tmp/build_uhd

# Build and install AirSpy
RUN wget -nv https://github.com/airspy/airspyone_host/archive/v${AIRSPY_VERSION}.tar.gz -O /tmp/airspy.tar.gz \
    && tar xf /tmp/airspy.tar.gz -C /tmp \
    && cmake3 -Wno-dev -S /tmp/airspyone_host-${AIRSPY_VERSION} -B /tmp/build_airspy \
    && make -j$(nproc) -C /tmp/build_airspy \
    && make -C /tmp/build_airspy install \
    && rm -rf /tmp/airspy* /tmp/build_airspy

# Build and install BladeRF
RUN git clone --branch ${BLADERF_VERSION} --recursive \
        https://github.com/Nuand/bladeRF /tmp/bladeRF \
    && cmake3 -S /tmp/bladeRF/host -B /tmp/build_blade -DCMAKE_C_FLAGS="-Wno-error=calloc-transposed-args" \
    && make -j$(nproc) -C /tmp/build_blade \
    && make -C /tmp/build_blade install \
    && rm -rf /tmp/bladeRF /tmp/build_blade

# Build and install LimeSuite
RUN wget -nv https://github.com/myriadrf/LimeSuite/archive/v${LIMESUITE_VERSION}.tar.gz -O /tmp/lime.tar.gz \
    && tar xf /tmp/lime.tar.gz -C /tmp \
    && cmake3 -S /tmp/LimeSuite-${LIMESUITE_VERSION} -B /tmp/build_lime \
    && make -j$(nproc) -C /tmp/build_lime \
    && make -C /tmp/build_lime install \
    && rm -rf /tmp/lime* /tmp/build_lime

# Build and install RTL-SDR
RUN wget -nv https://github.com/osmocom/rtl-sdr/archive/${RTLSDR_VERSION}.tar.gz -O /tmp/rtlsdr.tar.gz \
    && tar xf /tmp/rtlsdr.tar.gz -C /tmp \
    && cmake3 -DDETACH_KERNEL_DRIVER=ON -S /tmp/rtl-sdr-${RTLSDR_VERSION} -B /tmp/build_rtlsdr \
    && make -j$(nproc) -C /tmp/build_rtlsdr \
    && make -C /tmp/build_rtlsdr install \
    && rm -rf /tmp/rtlsdr* /tmp/build_rtlsdr

# Install SDRplay API
RUN wget -nv https://www.sdrplay.com/software/SDRplay_RSP_API-Linux-${SDRPLAY_VERSION}.2.run -O /tmp/sdrplay.run \
    && bash /tmp/sdrplay.run --tar xf -C /tmp \
    && mv /tmp/inc/sdrplay_*.h /usr/include \
    && mv /tmp/amd64/* /usr/lib64 \
    && ln -s /usr/lib64/libsdrplay_api.so.${SDRPLAY_VERSION} /usr/lib64/libsdrplay_api.so \
    && rm -rf /tmp/*
