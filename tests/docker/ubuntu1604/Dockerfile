FROM ubuntu:16.04

RUN apt-get update\
 && apt-get -y dist-upgrade\
 && apt-get -y install nano vim\
 && apt-get -y install git g++ libpython3-dev python3-pip python3-pyqt5 python3-numpy cmake libsqlite3-dev libi2c-dev libusb-1.0-0-dev\
 && apt-get -y install hackrf rtl-sdr airspy\
 && ln -s /usr/lib/x86_64-linux-gnu/librtlsdr.so.0 /usr/lib/x86_64-linux-gnu/librtlsdr.so\
 && ln -s /usr/lib/x86_64-linux-gnu/libhackrf.so.0 /usr/lib/x86_64-linux-gnu/libhackrf.so\
 && ln -s /usr/lib/x86_64-linux-gnu/libairspy.so.0 /usr/lib/x86_64-linux-gnu/libairspy.so\
 && git clone https://github.com/myriadrf/LimeSuite && cd LimeSuite\
 && mkdir builddir && cd builddir && cmake ../ && make -j4 && make install\
 && cp /usr/local/lib/libLimeSuite.so* /usr/lib/x86_64-linux-gnu/

ADD test_native_backends_installed.sh /bin/test_native_backends_installed.sh
RUN chmod +x /bin/test_native_backends_installed.sh
CMD /bin/test_native_backends_installed.sh
