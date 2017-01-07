FROM kalilinux/kali-linux-docker

RUN apt-get -y update\
 && apt-get -y dist-upgrade\
 && apt-get clean\
 && apt-get -y install git g++ libpython3-dev libhackrf-dev python3-pip python3-pyqt5 python3-numpy

ADD install_with_pip.sh /bin/install_with_pip.sh
RUN chmod +x /bin/install_with_pip.sh
CMD /bin/install_with_pip.sh