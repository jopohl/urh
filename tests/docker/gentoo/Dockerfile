FROM gentoo/stage3-amd64

RUN PYTHON_TARGETS="python3_4" emerge psutil numpy dev-vcs/git app-portage/cfg-update
RUN PYTHON_TARGETS="python3_4" emerge --autounmask-write PyQt5
RUN etc-update --automode -3
RUN PYTHON_TARGETS="python3_4" emerge PyQt5

RUN echo "#!/bin/bash" > /bin/run.sh
RUN echo "git clone https://github.com/jopohl/urh" >> /bin/run.sh
RUN echo "cd urh/src/urh" >> /bin/run.sh
RUN echo "./main autoclose" >> /bin/run.sh

RUN chmod +x /bin/run.sh
CMD /bin/run.sh