FROM gentoo/stage3-amd64

RUN emerge --sync
RUN emerge dev-vcs/git app-portage/cfg-update
RUN PYTHON_TARGETS="python3_4" emerge psutil numpy
RUN PYTHON_TARGETS="python3_4" emerge --autounmask-write PyQt5 || /bin/true
RUN etc-update --automode -5
RUN PYTHON_TARGETS="python3_4" emerge PyQt5

RUN echo "#!/bin/bash" > /bin/run.sh
RUN echo "git clone https://github.com/jopohl/urh" >> /bin/run.sh
RUN echo "cd urh/src/urh" >> /bin/run.sh
RUN echo "./main.py autoclose" >> /bin/run.sh

RUN chmod +x /bin/run.sh
CMD /bin/run.sh