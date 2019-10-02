# Universal Radio Hacker [![Blackhat Arsenal 2017](https://rawgit.com/toolswatch/badges/master/arsenal/usa/2017.svg)](http://www.toolswatch.org/2017/06/the-black-hat-arsenal-usa-2017-phenomenal-line-up-announced/) [![Blackhat Arsenal 2018](https://raw.githubusercontent.com/jopohl/badges/master/arsenal/europe/2018.svg?sanitize=true)](http://www.toolswatch.org/2018/09/black-hat-arsenal-europe-2018-lineup-announced/)

[![Tests status](https://img.shields.io/azure-devops/tests/jopohl/urh/2/master.svg)](https://dev.azure.com/jopohl/urh/_build?definitionId=2)
[![Coverage](https://img.shields.io/azure-devops/coverage/jopohl/urh/2/master.svg)](https://dev.azure.com/jopohl/urh/_build?definitionId=2)
[![PyPI version](https://badge.fury.io/py/urh.svg)](https://badge.fury.io/py/urh)
[![Packaging status](https://repology.org/badge/tiny-repos/urh.svg)](https://repology.org/project/urh/versions)
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

Want to stay in touch? [![Slack](https://img.shields.io/badge/chat-on%20slack-blue.svg?logo=slack)](https://join.slack.com/t/stralsundsecurity/shared_invite/enQtMjEwOTIxNzMzODc3LTk3NmE4MGVjYjEyYTMzYTdmN2RlNzUzYzg0NTNjNTQ2ODBkMzI3MDZlOWY3MjE4YjBkNTM4ZjJlNTJlZmJhNDg)

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
- [MacOS](#macos)
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

## MacOS
### Using DMG
It is recommended to use __at least macOS 10.14__ when using the DMG available [here](https://github.com/jopohl/urh/releases).

### With pip
1. Install [Python 3 for Mac OS X](https://www.python.org/downloads/mac-osx/). 
   _If you experience issues with preinstalled Python, make sure you update to a recent version using the given link._
2. (Optional) Install desired native libs e.g. ``` brew install librtlsdr ``` for 
corresponding native device support.
3. In a terminal, type: ``` pip3 install urh ```.
4. Type ``` urh ``` in a terminal to get it started.


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

## Articles
### Hacking stuff with URH
* [Hacking burger pagers](https://www.rtl-sdr.com/using-a-hackrf-to-reverse-engineer-and-control-restaurant-pagers/)
* [Reverse engineer and clone a remote control](https://www.rtl-sdr.com/video-tutorial-using-universal-radio-hacker-an-rtl-sdr-and-a-microcontroller-to-clone-433-mhz-remotes/)
* [Reverse engineering weather station RF signals](https://www.rtl-sdr.com/tag/universal-radio-hacker/)
* [Reverse engineering wireless blinds](https://www.rtl-sdr.com/reverse-engineering-wireless-blinds-with-an-rtl-sdr-and-controlling-them-with-amazon-alexa/)
* [Attacking Logitech wireless presenters (german article)](https://www.heise.de/security/meldung/Wireless-Presenter-von-Logitech-und-Inateck-anfaellig-fuer-Angriffe-ueber-Funk-4439795.html)
* [Reverse engineering a 433MHz remote-controlled power socket for use with Arduino](http://www.ignorantofthings.com/2018/11/reverse-engineering-433mhz-remote.html)

### General presentations and tutorials on URH
* [Hackaday article](https://hackaday.com/2017/02/23/universal-radio-hacker/)
* [RTL-SDR.com article](https://www.rtl-sdr.com/reverse-engineering-signals-universal-radio-hacker-software/)
* [Short tutorial on URH with LimeSDR mini](https://www.crowdsupply.com/lime-micro/limesdr-mini/updates/investigating-wireless-protocols-with-universal-radio-hacker)
* [Brute forcing a RF Device: a step-by-step guide](https://pandwarf.com/news/brute-forcing-a-new-device-a-step-by-step-guide/)

## External decodings
See [wiki](https://github.com/jopohl/urh/wiki/External-decodings) for a list of external decodings provided by our community! Thanks for that!

## Screenshots
### Get the data out of raw signals
![Interpretation phase](http://i.imgur.com/Wy17Zv3.png)

### Keep an overview even on complex protocols
 ![Analysis phase](http://i.imgur.com/ubAL3pE.png)

### Record and send signals
 ![Record](http://i.imgur.com/BfQpg23.png)
