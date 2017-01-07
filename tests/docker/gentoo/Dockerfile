FROM gentoo/stage3-amd64

RUN emerge --sync\
 && emerge dev-vcs/git app-portage/cfg-update\
 && PYTHON_TARGETS="python3_4" emerge psutil numpy

# PYTHON_TARGETS="python3_4"
RUN USE="gui widgets" emerge --autounmask-write PyQt5 || /bin/true
RUN etc-update --automode -5
RUN USE="gui widgets" emerge PyQt5 # PYTHON_TARGETS="python3_4"

ADD run_from_source.sh /bin/run_from_source.sh

RUN chmod +x /bin/run_from_source.sh
CMD /bin/run_from_source.sh