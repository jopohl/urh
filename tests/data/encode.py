#!/usr/bin/env python
"""
Simple example external encoding
Simply doubles each bit of the input
"""

import sys

bits = sys.argv[1]
print("".join(b + b for b in bits))
