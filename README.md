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
1. Install [Visual C++ Build Tools](http://landinghub.visualstudio.com/visual-cpp-build-tools)
2. Install [Python 3.5 for Windows](https://www.python.org/downloads/windows/)
3. ( Open a terminal (__cmd__) and type: ``` pip install numpy ``` ) _This speeds the installation up a bit_
4. In a terminal, type: ``` pip install urh ```
5. Navigate to ```C:\Users\<Your-Username>\AppData\Local\Programs\Python\Python35\Scripts```
6. In a terminal (__cmd__) type ```python urh```

### Running from source
To execute the Universal Radio Hacker without installation, just run:
```bash
git clone https://github.com/jopohl/urh/
cd urh/bin
./urh
```

Note, before first usage the C++ extensions will be built.

## Screenshots
### Get the data out of raw signals
 ![Interpreation phase](/doc/screenshots/interpretation_full.png?raw=true)

### Keep an overview even on complex protocols
 ![Analysis phase](/doc/screenshots/analysis_full.png?raw=true)

### Record and send signals
 ![Record](/doc/screenshots/record_signal.png?raw=true)
