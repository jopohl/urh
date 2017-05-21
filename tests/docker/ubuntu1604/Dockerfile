FROM ubuntu:16.04

RUN apt-get update\
 && apt-get -y dist-upgrade\
 && apt-get -y install nano vim\
 && apt-get -y install git g++ libpython3-dev python3-pip python3-pyqt5 python3-numpy cmake libsqlite3-dev libi2c-dev libusb-1.0-0-dev\
 && apt-get -y install libairspy-dev libhackrf-dev librtlsdr-dev libuhd-dev software-properties-common\
 && add-apt-repository -y ppa:myriadrf/drivers\
 && apt-get update && apt-get install -y limesuite\
 && ln -s /usr/lib/x86_64-linux-gnu/libLimeSuite.so.17.02.2 /usr/lib/x86_64-linux-gnu/libLimeSuite.so

ADD test_native_backends_installed.sh /bin/test_native_backends_installed.sh
RUN chmod +x /bin/test_native_backends_installed.sh
CMD /bin/test_native_backends_installed.sh
