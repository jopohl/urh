#!/bin/bash
cd /tmp
git clone https://github.com/jopohl/urh
cd urh
python3 setup.py install
urh autoclose
#/tmp/urh/bin/urh