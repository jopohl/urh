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

## Windows
1. Install [Visual Studio 2015 Community](https://www.visualstudio.com/de-de/downloads/download-visual-studio-vs.aspx) - ensure you tick C++ language
2. Install [Python 3.5 for Windows](https://www.python.org/downloads/windows/)
3. Install [PyQt5 for Windows](https://www.riverbankcomputing.com/software/pyqt/download5)
4. Open a terminal (__cmd__) and type: ```pip install numpy```
5. After that, type ```pip install urh```
6. Navigate to ```C:\Users\<Your-Username>\AppData\Local\Programs\Python\Python35\Scripts```
7. In a terminal (__cmd__) type ```python urh```


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
