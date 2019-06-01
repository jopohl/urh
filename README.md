# Universal Radio Hacker [![Blackhat Arsenal 2017](https://rawgit.com/toolswatch/badges/master/arsenal/usa/2017.svg)](http://www.toolswatch.org/2017/06/the-black-hat-arsenal-usa-2017-phenomenal-line-up-announced/) [![Blackhat Arsenal 2018](https://raw.githubusercontent.com/jopohl/badges/master/arsenal/europe/2018.svg?sanitize=true)](http://www.toolswatch.org/2018/09/black-hat-arsenal-europe-2018-lineup-announced/)

[![Build Status](https://dev.azure.com/jopohl/urh/_apis/build/status/jopohl.urh?branchName=master)](https://dev.azure.com/jopohl/urh/_build/latest?definitionId=2?branchName=master)
[![Tests status](https://img.shields.io/azure-devops/tests/jopohl/urh/2/master.svg)](https://dev.azure.com/jopohl/urh/_build?definitionId=2)
[![Coverage](https://img.shields.io/azure-devops/coverage/jopohl/urh/2/master.svg)](https://dev.azure.com/jopohl/urh/_build?definitionId=2)
[![PyPI version](https://badge.fury.io/py/urh.svg)](https://badge.fury.io/py/urh)
[![Average time to resolve an issue](http://isitmaintained.com/badge/resolution/jopohl/urh.svg)](http://isitmaintained.com/project/jopohl/urh "Average time to resolve an issue")
[![Percentage of issues still open](http://isitmaintained.com/badge/open/jopohl/urh.svg)](http://isitmaintained.com/project/jopohl/urh "Percentage of issues still open")

The Universal Radio Hacker (URH) is a software for investigating unknown wireless protocols. Features include

* __hardware interfaces__ for common Software Defined Radios
* __easy demodulation__ of signals
* __assigning participants__ to keep overview of your data
* __customizable decodings__ to crack even sophisticated encodings like CC1101 data whitening
* __assign labels__ to reveal the logic of the protocol
* __automatic reverse engineering__ of protocol fields
* __fuzzing component__ to find security leaks
* __modulation support__ to inject the data back into the system
* __simulation environment__ to perform stateful attacks

To get started, download the [official userguide (PDF)](https://github.com/jopohl/urh/releases/download/v2.0.0/userguide.pdf), watch the [demonstration videos (YouTube)](https://www.youtube.com/watch?v=kuubkTDAxwA&index=1&list=PLlKjreY6G-1EKKBs9sucMdk8PwzcFuIPB)
or check out the [wiki](https://github.com/jopohl/urh/wiki) for more information and supported devices. Scroll down this page to learn how to install URH on your system.

Want to stay in touch? [![Slack](https://img.shields.io/badge/chat-on%20slack-blue.svg?logo=slack)](https://join.slack.com/t/stralsundsecurity/shared_invite/enQtMjEwOTIxNzMzODc3LWU4ZWIzMTQ3NDAyNjkzODBhZTJiZDNmN2U0MTA4ZTM1MjhhNTNiYTc4YzQ5MDk2NjU5YzMxOWJmMDQyZDczYjg)

If you find URH useful, please consider giving this repository a :star: or even [donate via PayPal](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=6WDFF59DL56Z2). We appreciate your support!

If you use URH in your research paper, please cite [this](https://www.usenix.org/conference/woot18/presentation/pohl) WOOT'18 paper, or directly use the following BibTeX entry.
<details>
  <summary>
    <b>BibTeX entry for citing URH</b>
  </summary>
  
  ```latex
@inproceedings {220562,
author = {Johannes Pohl and Andreas Noack},
title = {Universal Radio Hacker: A Suite for Analyzing and Attacking Stateful Wireless Protocols},
booktitle = {12th {USENIX} Workshop on Offensive Technologies ({WOOT} 18)},
year = {2018},
address = {Baltimore, MD},
url = {https://www.usenix.org/conference/woot18/presentation/pohl},
publisher = {{USENIX} Association},
}
```
</details>

# Installation
Universal Radio Hacker can be installed via __pip__ or using the __package manager__ of your distribution (if included).
Below you find more specific installation instructions for:
- [Windows](#windows)
- [Linux](#linux)
  - [Install via Package Manager](#install-via-package-manager)
  - [Generic Installation with pip (Ubuntu/Debian)](#generic-installation-with-pip-ubuntudebian)
  - [Docker Image](#docker-image)
- [Mac OS X](#mac-os-x)
- [Updating your installation](#update-your-installation)
  - [Updating with pip](#updating-with-pip)
  - [Updating with MSI](#updating-with-msi)
- [Running from source](#running-from-source)


## Windows
On Windows, URH can be installed with it's [MSI Installer](https://github.com/jopohl/urh/releases). No further dependencies are required.
 
If you get an error about missing ``` api-ms-win-crt-runtime-l1-1-0.dll ```, run Windows Update or directly install [KB2999226](https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows).

## Linux
### Install via Package Manager
URH is included in the repositories of many linux distributions such as __Arch Linux__, __Gentoo__, __Fedora__, __openSUSE__ or __NixOS__. There is also a package for __FreeBSD__. If available, simply use your package manager to install URH. 

### Generic Installation with pip (Ubuntu/Debian)
URH you can also be installed with using ```python3 -m pip install urh```. 
In case you are running __Ubuntu__ or __Debian__ read on for more specific instructions.

In order to use native device backends, make sure you install the __-dev__ package for your desired SDRs, that is ``` libairspy-dev ```, ``` libhackrf-dev ```, ``` librtlsdr-dev  ```, ``` libuhd-dev  ```.

If your device does not have a ``` -dev ``` package, e.g. LimeSDR, you need to manually create a symlink to the ``` .so ```, like this:
```bash
sudo ln -s /usr/lib/x86_64-linux-gnu/libLimeSuite.so.17.02.2 /usr/lib/x86_64-linux-gnu/libLimeSuite.so
```

__before__ installing URH, using:

```bash
sudo apt-get update
sudo apt-get install python3-numpy python3-psutil python3-zmq python3-pyqt5 g++ libpython3-dev python3-pip cython3
sudo pip3 install urh
```

### Docker Image
If you use docker you can also run the official URH docker image available [here](https://hub.docker.com/r/jopohl/urh/).

## Mac OS X
Use the DMG available [here](https://github.com/jopohl/urh/releases).

## Update your installation
### Updating with pip
If you installed URH via pip you can keep it up to date with ``` pip3 install --upgrade urh ```, or, if this should not work ``` python3 -m pip install --upgrade urh ```.

### Updating with MSI
If you experience issues after updating URH using the ``` .msi ``` installer on Windows, please perform a __full uninstallation__. That is, uninstall URH via Windows and after that remove the installation folder (something like ``` C:\Program Files\Universal Radio Hacker ```). Now, install the new version using the recent ```.msi ```.

## Running from source
If you like to live on bleeding edge, you can run URH from source.

### Without installation
To execute the Universal Radio Hacker without installation, just run:
```bash
git clone https://github.com/jopohl/urh/
cd urh/src/urh
./main.py
```

Note, before first usage the C++ extensions will be built.

### Installing from source
To install from source you need to have ``` python-setuptools ``` installed. You can get it e.g. with ``` pip install setuptools ```. 
Once the setuptools are installed use: 
```bash
git clone https://github.com/jopohl/urh/
cd urh
python setup.py install
```

And start the application by typing ``` urh ``` in a terminal.

## External decodings
See [wiki](https://github.com/jopohl/urh/wiki/External-decodings) for a list of external decodings provided by our community! Thanks for that!

## Screenshots
### Get the data out of raw signals
![Interpretation phase](http://i.imgur.com/Wy17Zv3.png)

### Keep an overview even on complex protocols
 ![Analysis phase](http://i.imgur.com/ubAL3pE.png)

### Record and send signals
 ![Record](http://i.imgur.com/BfQpg23.png)
