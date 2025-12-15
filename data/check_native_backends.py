#!/usr/bin/env python3

import importlib
import os
import sys

rc = 0

if sys.platform == "win32":
    shared_lib_dir = os.path.realpath(
        os.path.join(os.path.dirname(__file__), "..", "src/urh/dev/native/lib/shared")
    )
    print("Attempting to read", shared_lib_dir)
    if os.path.isdir(shared_lib_dir):
        os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + shared_lib_dir
        print("PATH updated")

for sdr in (
    "AirSpy",
    "BladeRF",
    "HackRF",
    "RTLSDR",
    "LimeSDR",
    "PlutoSDR",
    "SDRPlay",
    "USRP",
):
    try:
        importlib.import_module(".{}".format(sdr.lower()), "urh.dev.native.lib")
        print("{:<10} \033[92mSUCCESS\033[0m".format(sdr + ":"))
    except ImportError as e:
        print("{:<10} \033[91mFAILURE\033[0m ({})".format(sdr + ":", e))
        rc = 1

sys.exit(rc)
