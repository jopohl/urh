# Requirements
- Python 3.4+
- numpy
- PyQt5
- C++ Compiler

# Installation
## Arch Linux
```bash
yaourt -S urh
```

## Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install python3-numpy python3-pyqt5 g++ libpython3-dev python3-pip
sudo pip3 install urh
```

## From cloned repository
```bash
git clone https://github.com/jopohl/urh/
cd urh
sudo python setup.py install
```

# Running from source
To execute the Universal Radio Hacker without installation, just run:
```bash
git clone https://github.com/jopohl/urh/
cd urh/bin
./urh
```

Note, before first usage the C++ extensions will be built.
