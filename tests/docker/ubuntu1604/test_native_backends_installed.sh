#!/usr/bin/env bash
git clone https://github.com/jopohl/urh
cd urh/src
python3 urh/cythonext/build.py

python3 -c "import urh.dev.native.lib.airspy" && \
python3 -c "import urh.dev.native.lib.hackrf" && \
python3 -c "import urh.dev.native.lib.rtlsdr" && \
python3 -c "import urh.dev.native.lib.limesdr"
