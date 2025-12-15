FROM ubuntu:18.04

LABEL maintainer="Johannes.Pohl90@gmail.com"

ENV TZ=Europe/Berlin

# Debug QT plugins by exporting QT_DEBUG_PLUGINS=1 before running URH
# To allow docker to connect to X run xhost +local:docker

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && apt-get -qq update \
 && apt-get -qq install software-properties-common \
 && add-apt-repository -y ppa:myriadrf/drivers && apt-get -qq update \
 && apt-get -qq install wget gcc g++ git \
                       python3 python3-pip python3-pyaudio python3-pyqt5 python3-numpy python3-psutil \
                       fonts-dejavu-core libgles2-mesa libusb-1.0-0 \
                       gr-osmosdr \
                       libhackrf-dev liblimesuite-dev libbladerf-dev librtlsdr-dev libairspy-dev libuhd-dev libiio-dev \
 && python3 -m pip install setuptools cython \
 && mkdir /tmp/sdrplay \
 && wget http://www.sdrplay.com/software/SDRplay_RSP_API-Linux-2.13.1.run -O /tmp/sdrplay/sdrplay.run \
 && cd /tmp/sdrplay && bash sdrplay.run --tar xf \
 && cp mirsdrapi-rsp.h /usr/local/include \
 && cp x86_64/libmirsdrapi-rsp.so.2.13 /usr/lib/x86_64-linux-gnu/ \
 && ln -s /usr/lib/x86_64-linux-gnu/libmirsdrapi-rsp.so.2.13 /usr/lib/x86_64-linux-gnu/libmirsdrapi-rsp.so \
 && rm -rf /tmp/sdrplay \
 \
 && cd /tmp && git clone --depth=1 https://github.com/jopohl/urh \
 && cd /tmp/urh \
 && python3 setup.py install \
 && rm -rf /tmp/urh \
 \
 && apt-get -qq remove wget gcc g++ git ttf-bitstream-vera \
 && apt-get -qq autoremove \
 && dbus-uuidgen > /var/lib/dbus/machine-id \
 && apt-get -qq clean all \
 && mkdir /tmp/runtime-root \
 && chmod 0700 /tmp/runtime-root

CMD XDG_RUNTIME_DIR=/tmp/runtime-root urh
