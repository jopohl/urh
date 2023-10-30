#!/usr/bin/env python3
import os
import sys

from subprocess import call

cur_dir = os.path.dirname(os.path.realpath(__file__))

if sys.argv[1] == "e":
    call(
        sys.executable
        + ' "'
        + os.path.join(cur_dir, "encode.py")
        + '"'
        + " "
        + sys.argv[2],
        shell=True,
    )
elif sys.argv[1] == "d":
    call(
        sys.executable
        + ' "'
        + os.path.join(cur_dir, "decode.py")
        + '"'
        + " "
        + sys.argv[2],
        shell=True,
    )
else:
    print("Unknown")
