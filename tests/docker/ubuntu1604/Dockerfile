FROM ubuntu:16.04

RUN apt-get update\
 && apt-get -y dist-upgrade\
 && apt-get -y install nano vim\
 && apt-get -y install git g++ libpython3-dev python3-pip python3-pyqt5 python3-numpy

ADD install_with_pip.sh /bin/install_with_pip.sh
RUN chmod +x /bin/install_with_pip.sh
CMD /bin/install_with_pip.sh
