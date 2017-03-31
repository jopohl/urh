# Universal Radio Hacker
[![Build Status](https://travis-ci.org/jopohl/urh.svg?branch=master)](https://travis-ci.org/jopohl/urh) [![Code Climate](https://codeclimate.com/github/jopohl/urh/badges/gpa.svg)](https://codeclimate.com/github/jopohl/urh) [![PyPI version](https://badge.fury.io/py/urh.svg)](https://pypi.python.org/pypi/urh) [![Dependency Status](https://gemnasium.com/badges/github.com/jopohl/urh.svg)](https://gemnasium.com/github.com/jopohl/urh)

The Universal Radio Hacker is a software for investigating unknown wireless protocols. Features include

* __hardware interfaces__ for common Software Defined Radios
* __easy demodulation__ of signals
* __assigning participants__ to keep overview of your data
* __customizable decodings__ to crack even sophisticated encodings like CC1101 data whitening
* __assign labels__ to reveal the logic of the protocol
* __fuzzing component__ to find security leaks
* __modulation support__ to inject the data back into the system

Check out the [wiki](https://github.com/jopohl/urh/wiki) for more information and supported devices.

Like to see things in action? Watch URH on YouTube!

[![Youtube Image](http://i.imgur.com/5HGzP2T.png)](https://www.youtube.com/watch?v=kuubkTDAxwA)

## Installation
### Dependencies
#### Required
- Python 3.4+
- numpy / psutil / zmq
- PyQt5
- C++ Compiler

#### Optional
- librtlsdr (for native RTL-SDR device backend)
- libhackrf (for native HackRF device backend)
- gnuradio / gnuradio-osmosdr (for GNU Radio device backends) 

### Arch Linux
```bash
yaourt -S urh
```

### Ubuntu/Debian
If you want to use native backends for _RTL-SDR_ or _HackRF_ and installed these drivers using your packet manager, 
you need to create the appropriate symlink:
```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/librtlsdr.so.0 /usr/lib/x86_64-linux-gnu/librtlsdr.so
sudo ln -s /usr/lib/x86_64-linux-gnu/libhackrf.so.0 /usr/lib/x86_64-linux-gnu/libhackrf.so
```

__before__ installing URH, using:

```bash
sudo apt-get update
sudo apt-get install python3-numpy python3-psutil python3-zmq python3-pyqt5 g++ libpython3-dev python3-pip
sudo pip3 install urh
```



### Windows
1. Install [Visual C++ Build Tools](http://landinghub.visualstudio.com/visual-cpp-build-tools).
2. Install [Python 3 for Windows](https://www.python.org/downloads/windows/). Choose a __64 Bit__ version!
3. (Optional) Open a terminal (__cmd__) and type: ``` pip install numpy ``` - _This speeds the installation up a bit._
4. In a terminal, type: ``` pip install urh ```.
5. Type ``` urh ``` in a terminal or search for ``` urh ``` in search bar.

### Mac OS X
1. Install [Python 3 for Mac OS X](https://www.python.org/downloads/mac-osx/).
2. (Optional) Install desired native libs e.g. ``` brew install librtlsdr ``` for 
corresponding native device support.
3. In a terminal, type: ``` pip3 install urh ```.
4. Type ``` urh ``` in a terminal to get it started.

### Updating
If you installed URH via pip you can keep it up to date with
```bash
pip3 install --upgrade urh
```

### Running from source
If you like to live on bleeding edge, you can run URH from source.

#### Without Installation
To execute the Universal Radio Hacker without installation, just run:
```bash
git clone https://github.com/jopohl/urh/
cd urh/src/urh
./main.py
```

Note, before first usage the C++ extensions will be built.

#### Installing from source
To install from source you need to have ``` python-setuptools ``` installed. You can get it e.g. with ``` pip install setuptools ```. 
Once the setuptools are installed use: 
```bash
git clone https://github.com/jopohl/urh/
cd urh
python setup.py install
```

And start the application by typing ``` urh ``` in a terminal.



## Screenshots
### Get the data out of raw signals
![Interpretation phase](http://i.imgur.com/Wy17Zv3.png)


### Keep an overview even on complex protocols
 ![Analysis phase](http://i.imgur.com/ubAL3pE.png)

### Record and send signals
 ![Record](http://i.imgur.com/BfQpg23.png)
