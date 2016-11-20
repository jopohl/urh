FROM debian:8

RUN apt-get update
RUN apt-get -y dist-upgrade
RUN apt-get -y install nano vim
RUN apt-get -y install python3-numpy python3-psutil python3-pyqt5 git g++ libpython3-dev python3-setuptools

RUN echo "#!/bin/bash" > /bin/run.sh
RUN echo "git clone https://github.com/jopohl/urh" >> /bin/run.sh
RUN echo "cd urh" >> /bin/run.sh
RUN echo "python3 setup.py install" >> /bin/run.sh
RUN echo "urh autoclose" >> /bin/run.sh

RUN chmod +x /bin/run.sh
CMD /bin/run.sh