![URH image](https://raw.githubusercontent.com/jopohl/urh/master/data/icons/banner.png)

[![Build Status](https://dev.azure.com/jopohl/urh/_apis/build/status/jopohl.urh?branchName=master)](https://dev.azure.com/jopohl/urh/_build/latest?definitionId=2&branchName=master)
[![PyPI version](https://badge.fury.io/py/urh.svg)](https://badge.fury.io/py/urh)
[![Packaging status](https://repology.org/badge/tiny-repos/urh.svg)](https://repology.org/project/urh/versions)
 [![Blackhat Arsenal 2017](https://rawgit.com/toolswatch/badges/master/arsenal/usa/2017.svg)](http://www.toolswatch.org/2017/06/the-black-hat-arsenal-usa-2017-phenomenal-line-up-announced/)
 [![Blackhat Arsenal 2018](https://rawgit.com/toolswatch/badges/master/arsenal/europe/2018.svg)](http://www.toolswatch.org/2018/09/black-hat-arsenal-europe-2018-lineup-announced/)


The Universal Radio Hacker (URH) is a complete suite for wireless protocol investigation with native support for [many](https://github.com/jopohl/urh/wiki/Supported-devices) common __Software Defined Radios__.
URH allows __easy demodulation__ of signals combined with an [automatic](https://dl.acm.org/doi/10.1145/3375894.3375896) detection of modulation parameters making it a breeze to identify the bits and bytes that fly over the air. 
As data often gets _encoded_ before transmission, URH offers __customizable decodings__ to crack even sophisticated encodings like CC1101 data whitening.
When it comes to __protocol reverse-engineering__, URH is helpful in two ways. You can either manually assign protocol fields and message types or let URH __automatically infer protocol fields__ with a [rule-based intelligence](https://www.usenix.org/conference/woot19/presentation/pohl).
Finally, URH entails a __fuzzing component__ aimed at stateless protocols and a __simulation environment__ for stateful attacks.

### Getting started
In order to get started
 - view the [installation instructions](#Installation) on this page,
 - download the [official userguide (PDF)](https://github.com/jopohl/urh/releases/download/v2.0.0/userguide.pdf), 
 - watch the [demonstration videos (YouTube)](https://www.youtube.com/watch?v=kuubkTDAxwA&index=1&list=PLlKjreY6G-1EKKBs9sucMdk8PwzcFuIPB),
 - check out the [wiki](https://github.com/jopohl/urh/wiki) for more information such as supported devices or
 - read some [articles about URH](#Articles) for inspiration.

If you like URH, please :star: this repository and [join our Slack channel](https://join.slack.com/t/stralsundsecurity/shared_invite/enQtMjEwOTIxNzMzODc3LTk3NmE4MGVjYjEyYTMzYTdmN2RlNzUzYzg0NTNjNTQ2ODBkMzI3MDZlOWY3MjE4YjBkNTM4ZjJlNTJlZmJhNDg). We appreciate your support!

### Citing URH
We encourage researchers working with URH to cite [this](https://www.usenix.org/conference/woot18/presentation/pohl) WOOT'18 paper or directly use the following BibTeX entry.
 
 <details>
 <summary> <b>URH BibTeX entry for your research paper</b> </summary>
 
  ```bibtex
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

## Installation
URH runs on Windows, Linux and macOS. Click on your operating system below to view installation instructions.

<details>
 <summary><b>Windows</b></summary><br/>

 On Windows, URH can be installed with its [Installer](https://github.com/jopohl/urh/releases). No further dependencies are required.
 
If you get an error about missing ```api-ms-win-crt-runtime-l1-1-0.dll```, run Windows Update or directly install [KB2999226](https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows).

</details>

<details>
<summary><b>Linux</b></summary>


<details open>
<summary><i>Generic Installation with pip (recommended)</i></summary><br/>

URH is available on [PyPi](https://pypi.org/project/urh/) so you can install it with 
```bash 
# IMPORTANT: Make sure your pip is up to date
sudo python3 -m pip install --upgrade pip  # Update your pip installation
sudo python3 -m pip install urh            # Install URH
``` 
This is the recommended way to install URH on Linux because it comes with __all native extensions__ precompiled.

In order to access your SDR as non-root user, install the according __udev rules__. You can find them [in the wiki](https://github.com/jopohl/urh/wiki/SDR-udev-rules).

</details>

<details>
<summary><i>Install via Package Manager</i></summary><br/>

URH is included in the repositories of many linux distributions such as __Arch Linux__, __Gentoo__, __Fedora__, __openSUSE__ or __NixOS__. There is also a package for __FreeBSD__.  If available, simply use your package manager to install URH.

__Note__: For native support, you must install the according ```-dev``` package(s) of your SDR(s) such as ```hackrf-dev``` __before__ installing URH.
</details>

<details>
<summary><i>Snap</i></summary><br/>

URH is available as a snap: https://snapcraft.io/urh

</details>

<details>
<summary><i>Docker Image</i></summary><br/>

The official URH docker image is available [here](https://hub.docker.com/r/jopohl/urh/). It has all native backends included and ready to operate. 
</details>

</details>


<details>
<summary><b>macOS</b></summary>

<details open>
<summary><i>Using DMG</i></summary><br/>

It is recommended to use __at least macOS 10.14__ when using the DMG available [here](https://github.com/jopohl/urh/releases).

</details>

<details>
<summary><i>With pip</i></summary><br/>

1. Install [Python 3 for Mac OS X](https://www.python.org/downloads/mac-osx/). 
   _If you experience issues with preinstalled Python, make sure you update to a recent version using the given link._
2. (Optional) Install desired native libs e.g. ```brew install librtlsdr``` for 
corresponding native device support.
3. In a terminal, type: ```pip3 install urh```.
4. Type ```urh``` in a terminal to get it started.

</details>

</details>

<details>
<summary><b>Update your installation</b></summary><br/>

If you installed URH via pip you can keep it up to date with ``` python3 -m pip install --upgrade urh ```.

</details>

<details>
<summary><b>Running from source</b></summary>

<details>
<summary><i>Without installation</i></summary><br/>

To execute the Universal Radio Hacker without installation, just run:
```bash
git clone https://github.com/jopohl/urh/
cd urh/src/urh
./main.py
```

Note, before first usage the C++ extensions will be built.


</details>

<details>
<summary><i>Installing from source</i></summary><br/>

To install URH from source you need to have ```python-setuptools``` installed. You can get them with ```python3 -m pip install setuptools```. 
Once the setuptools are installed execute: 
```bash
git clone https://github.com/jopohl/urh/
cd urh
python setup.py install
```

And start the application by typing ```urh``` in a terminal.

</details>

</details>

## Articles
### Hacking stuff with URH
* [Hacking Burger Pagers](https://www.rtl-sdr.com/using-a-hackrf-to-reverse-engineer-and-control-restaurant-pagers/)
* [Reverse-engineer and Clone a Remote Control](https://www.rtl-sdr.com/video-tutorial-using-universal-radio-hacker-an-rtl-sdr-and-a-microcontroller-to-clone-433-mhz-remotes/)
* [Reverse-engineering Weather Station RF Signals](https://www.rtl-sdr.com/tag/universal-radio-hacker/)
* [Reverse-engineering Wireless Blinds](https://www.rtl-sdr.com/reverse-engineering-wireless-blinds-with-an-rtl-sdr-and-controlling-them-with-amazon-alexa/)
* [Attacking Logitech Wireless Presenters (German Article)](https://www.heise.de/security/meldung/Wireless-Presenter-von-Logitech-und-Inateck-anfaellig-fuer-Angriffe-ueber-Funk-4439795.html)
* [Attacking Wireless Keyboards](https://threatpost.com/fujitsu-wireless-keyboard-unpatched-flaws/149477/)
* [Reverse-engineering a 433MHz Remote-controlled Power Socket for use with Arduino](http://www.ignorantofthings.com/2018/11/reverse-engineering-433mhz-remote.html)

### General presentations and tutorials on URH
* [Hackaday Article](https://hackaday.com/2017/02/23/universal-radio-hacker/)
* [RTL-SDR.com Article](https://www.rtl-sdr.com/reverse-engineering-signals-universal-radio-hacker-software/)
* [Short Tutorial on URH with LimeSDR Mini](https://www.crowdsupply.com/lime-micro/limesdr-mini/updates/investigating-wireless-protocols-with-universal-radio-hacker)
* [Brute-forcing a RF Device: a Step-by-step Guide](https://pandwarf.com/news/brute-forcing-a-new-device-a-step-by-step-guide/)
* [Hacking wireless sockets like a NOOB](https://olof-astrand.medium.com/hacking-wireless-sockets-like-a-noob-b57d4b4812d5)

## External decodings
See [wiki](https://github.com/jopohl/urh/wiki/External-decodings) for a list of external decodings provided by our community! Thanks for that!

## Screenshots
### Get the data out of raw signals
![Interpretation phase](http://i.imgur.com/Wy17Zv3.png)

### Keep an overview even on complex protocols
 ![Analysis phase](http://i.imgur.com/ubAL3pE.png)

### Record and send signals
 ![Record](http://i.imgur.com/BfQpg23.png)
