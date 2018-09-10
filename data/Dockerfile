FROM ubuntu:18.04

LABEL maintainer="Johannes.Pohl90@gmail.com"

ENV TZ=Europe/Berlin

# Debug QT plugins by exporting QT_DEBUG_PLUGINS=1 before running URH
# To allow docker to connect to X run xhost +local:docker

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && apt-get -qq update \
 && apt-get -qq install wget gcc g++ git \
                       python-pip python-zmq \
                       python3 python3-pip python3-pyaudio python3-pyqt5 python3-numpy python3-zmq python3-psutil \
                       fonts-dejavu-core libgles2-mesa libusb-1.0-0 \
                       gr-osmosdr libgnuradio-zeromq* > /dev/null \
 && python2 -m pip install pyusb \
 && python3 -m pip install setuptools cython \
 \
 && cd /tmp && git clone --depth=1 https://github.com/jopohl/urh \
 && wget https://www.dropbox.com/s/lp5cks82rp4pqhr/linux-64.tar.bz2 -O /tmp/linux-64.tar.bz2 \
 && cd /tmp/urh \
 && mkdir src/urh/dev/native/lib/shared \
 && tar xf /tmp/linux-64.tar.bz2 -C src/urh/dev/native/lib/shared \
 && cp -a src/urh/dev/native/lib/shared/*.so* /usr/lib/x86_64-linux-gnu/ \
 && rm -rf /tmp/linux-64.tar.bz2 \
 && python3 -m pip install . \
 && rm -rf /tmp/urh \
 \
 && cd /tmp && git clone --depth=1 https://github.com/atlas0fd00m/rfcat \
 && cd rfcat \
 && python setup.py install \
 && rm -rf ../rfcat \
 \
 && apt-get -qq remove wget gcc g++ git ttf-bitstream-vera \
 && apt-get -qq autoremove \
 && dbus-uuidgen > /var/lib/dbus/machine-id \
 && apt-get -qq clean all \
 && mkdir /tmp/runtime-root \
 && chmod 0700 /tmp/runtime-root

CMD XDG_RUNTIME_DIR=/tmp/runtime-root urh
