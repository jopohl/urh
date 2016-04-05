# Requirements
- Python 3.4+
- numpy
- PyQt5
- C++ Compiler

# Installation

```python
sudo python setup.py install
```

# Running from source
To run urh without installation, you need to rebuild the C++ Extensions:
```bash
cd src/urh/cythonext
python3 build.py
```

Then you can run the application:
```bash
cd bin
./urh
```
