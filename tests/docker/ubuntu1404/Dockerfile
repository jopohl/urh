FROM ubuntu:14.04

RUN apt-get update\
 && apt-get -y dist-upgrade\
 && apt-get -y install nano vim\
 && apt-get -y install git g++ libpython3-dev python3-pip python3-pyqt5 python3-numpy python3-setuptools\
 && apt-get -y install build-essential cmake libusb-1.0-0-dev liblog4cpp5-dev libboost-dev libboost-system-dev libboost-thread-dev libboost-program-options-dev swig pkg-config # Install HackRF

WORKDIR /tmp

RUN git clone https://github.com/mossmann/hackrf.git
WORKDIR /tmp/hackrf/host

RUN mkdir build
WORKDIR /tmp/hackrf/host/build
RUN cmake ../ -DINSTALL_UDEV_RULES=ON\
 && make -j4\
 && make install\
 && ldconfig

# Install Gnuradio - Doesnt work fails with package uhd-host
# RUN apt-get -y install gnuradio gnuradio-dev gr-iqbal

ADD install_with_pip.sh /bin/install_with_pip.sh
RUN chmod +x /bin/install_with_pip.sh
CMD /bin/install_with_pip.sh
