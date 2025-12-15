#!/usr/bin/env python
"""
Simple example external decoding
Simply removes every second bit
"""

import sys

bits = sys.argv[1]
print("".join(b for b in bits[::2]))
