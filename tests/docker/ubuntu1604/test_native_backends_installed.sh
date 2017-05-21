#!/usr/bin/env bash
git clone https://github.com/jopohl/urh
cd urh/src
python3 urh/cythonext/build.py

python3 -c "import urh.dev.native.lib.airspy; print('AirSpy found!')" && \
python3 -c "import urh.dev.native.lib.hackrf; print('HackRF found!')" && \
python3 -c "import urh.dev.native.lib.rtlsdr; print('RTL-SDR found!')" && \
python3 -c "import urh.dev.native.lib.limesdr; print('LimeSDR found!')" && \
python3 -c "import urh.dev.native.lib.usrp; print('USRP found!')"
