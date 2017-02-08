[![Build Status](https://travis-ci.org/jopohl/urh.svg?branch=master)](https://travis-ci.org/jopohl/urh)

## What's this?
Universal Radio Hacker is a suite for investigating unknown wireless protocols. Features include

* __hardware interfaces__ for common Software Defined Radios
* __easy demodulation__ of signals
* __assigning participants__ to keep overview of your data
* __customizable decodings__ to crack even sophisticated encodings like CC1101 data whitening
* __assign labels__ to reveal the logic of the protocol
* __fuzzing component__ to find security leaks
* __modulation support__ to inject the data back into the system

Check out the [wiki](https://github.com/jopohl/urh/wiki) for more information.

Like to see things in action? Watch URH on YouTube!

[![Youtube Image](/doc/screenshots/youtube.png?raw=true)](https://www.youtube.com/watch?v=kuubkTDAxwA)

## Installation
### Requirements
- Python 3.4+
- numpy / psutil
- PyQt5
- C++ Compiler

### Arch Linux
```bash
yaourt -S urh
```

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3-numpy python3-psutil python3-pyqt5 g++ libpython3-dev python3-pip
sudo pip3 install urh
```

### Windows
1. Install [Visual C++ Build Tools](http://landinghub.visualstudio.com/visual-cpp-build-tools).
2. Install [Python 3 for Windows](https://www.python.org/downloads/windows/).
3. (Optional) Open a terminal (__cmd__) and type: ``` pip install numpy ``` - _This speeds the installation up a bit._
4. In a terminal, type: ``` pip install urh ```.
5. Type ``` urh ``` in a terminal or search for ``` urh ``` in search bar.

### Mac OS X
1. Install [Python 3 for Mac OS X](https://www.python.org/downloads/mac-osx/).
2. In a terminal, type: ``` pip3 install urh ```.
3. Type ``` urh ``` in a terminal to get it started.

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
 ![Interpreation phase](/doc/screenshots/interpretation_full.png?raw=true)

### Keep an overview even on complex protocols
 ![Analysis phase](/doc/screenshots/analysis_full.png?raw=true)

### Record and send signals
 ![Record](/doc/screenshots/record_signal.png?raw=true)
