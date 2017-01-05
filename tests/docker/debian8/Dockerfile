FROM debian:8

RUN apt-get update\
 && apt-get -y dist-upgrade\
 && apt-get -y install nano vim\
 && apt-get -y install python3-numpy python3-psutil python3-pyqt5 git g++ libpython3-dev python3-setuptools

ADD install_from_source.sh /bin/install_from_source.sh
RUN chmod +x /bin/install_from_source.sh
CMD /bin/install_from_source.sh