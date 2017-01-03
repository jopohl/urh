FROM kalilinux/kali-linux-docker

RUN apt-get -y update && apt-get -y dist-upgrade && apt-get clean
RUN apt-get -y install git g++ libpython3-dev libhackrf-dev python3-pip python3-pyqt5 python3-numpy

RUN echo "#!/bin/bash" > /bin/run.sh
RUN echo "pip3 install urh" >> /bin/run.sh
RUN echo "urh autoclose" >> /bin/run.sh

RUN chmod +x /bin/run.sh
CMD /bin/run.sh