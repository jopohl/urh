FROM ubuntu:16.04

RUN apt-get update && apt-get -y dist-upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install git g++ libpython3-dev python3-pip python3-pyqt5 python3-numpy

RUN echo "#!/bin/bash" > /bin/run.sh
RUN echo "pip3 install urh" >> /bin/run.sh
RUN echo "urh autoclose" >> /bin/run.sh

RUN chmod +x /bin/run.sh
CMD /bin/run.sh
