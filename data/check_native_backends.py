#!/usr/bin/env python3

import importlib
import sys
rc = 0

for sdr in ("AirSpy", "BladeRF", "HackRF", "RTLSDR", "LimeSDR", "PlutoSDR", "SDRPlay", "USRP"):
    try:
        importlib.import_module('.{}'.format(sdr.lower()), 'urh.dev.native.lib')
        print("{:<10} SUCCESS".format(sdr+":"))
    except ImportError as e:
        print("{:<10} FAILURE ({})".format(sdr+":", e))
        rc = 1

sys.exit(rc)
