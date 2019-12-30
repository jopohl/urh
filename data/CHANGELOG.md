# Changelog
__This changelog file will not be updated anymore__. 

Instead, the recent changes can be found at the releases page: https://github.com/jopohl/urh/releases


## v2.5.3 (19/12/2018)
### Bugfixes
- fix crash when using spectrum analyzer with GNU Radio backend [#588](https://github.com/jopohl/urh/pull/588)

## v2.5.2 (10/12/2018)
### Bugfixes
- certain windows (e.g. decoding) can't be closed on OSX
- prevent crash in substitution encoding
- consider alignment offset when showing selected labels

### Adjustments
- remove ```Save and Close``` of fuzzing dialog, as closing means saving here anyway

### New features
- make application __font size__ configurable in ``` Options ``` -> ``` View ```

## v2.5.1 (25/11/2018)
### Bugfixes
- improve stability when capturing with SoundCard
- fix bug making the docker container crash at startup
- stop simulation instantly after finishing

## v2.5.0 (19/11/2018)
### New features
- Add native support for PlutoSDR [#574](https://github.com/jopohl/urh/pull/574)

### Bugfixes
- do not add URH to autostart on windows [#569](https://github.com/jopohl/urh/pull/569)
- save button was not shown when change on saved signal was undone [#571](https://github.com/jopohl/urh/pull/571)
- y scale got falsely reset on save [#573](https://github.com/jopohl/urh/pull/573)

## v2.4.2 (11/11/2018)
### New features
- enhance settings for RTL-SDR [#561](https://github.com/jopohl/urh/pull/561) + [#566](https://github.com/jopohl/urh/pull/566)
- ergonomic improvements [#564](https://github.com/jopohl/urh/pull/564)

### Bugfixes
- fix problem with set reference message shortcut [#559](https://github.com/jopohl/urh/pull/559)
- fix loading decodings and centralized place for decodings [#563](https://github.com/jopohl/urh/pull/563)

## v2.4.1 (23/10/2018)
### New features
- Add an option to disable automatic detection of interpretation parameters for newly loaded signals to the ``` Edit ``` menu [#555](https://github.com/jopohl/urh/pull/555) 

### Bugfixes
- fix off by one error when creating a new label in analysis
- fix crash when opening a project with saved dc correction setting

## v2.4.0 (19/10/2018)
### New features
- added __font size zoom__ to table views (analysis/generator/simulator); more details in [#546](https://github.com/jopohl/urh/pull/546)
- greatly enhance __accuracy of automatic interpretation__ [#550](https://github.com/jopohl/urh/pull/550)
- added __DC correction__ option to recording dialogs and as a new filter type in Interpretation [#552](https://github.com/jopohl/urh/pull/552) 

### Improvements
- ignore case when searching for hex values in analysis [#544](https://github.com/jopohl/urh/pull/544)
- RSSI is now given in dBm [#549](https://github.com/jopohl/urh/pull/549)

### Bugfixes
- Fix display of RSSI indicator in Interpretation [#547](https://github.com/jopohl/urh/pull/547)

## v2.3.0 (28/09/2018)
### New features
- added native support for BladeRF [#524](https://github.com/jopohl/urh/pull/524)
- added backward compatibility for SDRPlay < 2.13 [#528](https://github.com/jopohl/urh/pull/528)
- improved UI for message type and label configuration in analysis [#532](https://github.com/jopohl/urh/pull/532)
- rename __close all__ action to __close all files__ for more clarity [#532](https://github.com/jopohl/urh/pull/532)
- added a __close project__ action [#532](https://github.com/jopohl/urh/pull/532)


## v2.2.4 (30/08/2018)
### Bugfixes
- fix scaling of modulated preview in modulation dialog [#523](https://github.com/jopohl/urh/pull/523)
- improve default parameters for PSK modulation in modulation dialog [#523](https://github.com/jopohl/urh/pull/523)

## v2.2.3 (28/07/2018)
### New features
- allow save and load of binary protocols (``` .bin ``` files) [#488](https://github.com/jopohl/urh/pull/488)
- improve bootstrap of simulator messages [#500](https://github.com/jopohl/urh/pull/500)
  - auto assign destination when dropping messages to simulator
  - show participant address in participant legend if present
  - auto assign participant address when clicking analyze button in analysis based on SRC address label
- consider API changes of SDRPlay 2.13 [#508](https://github.com/jopohl/urh/pull/508) thanks [@mehdideveloper](https://github.com/mehdideveloper) 
- also consider participant address (next to RSSI) when auto assigning participants in analysis [#512](https://github.com/jopohl/urh/pull/512)
- Clear button stays enabled during operation so e.g. recordings can be cleared live [#514](https://github.com/jopohl/urh/pull/514)

### Bugfixes
- antenna selection is not saved when reopening dialog [#494](https://github.com/jopohl/urh/pull/494)
- hiding multiple rows at once in analysis not working properly [#499](https://github.com/jopohl/urh/pull/499)


## v2.2.2 (01/07/2018)
This release removes the ``` config.pxi ``` requirement which caused problems on Arch Linux and Gentoo during installation. More details in PR [#484](https://github.com/jopohl/urh/pull/484).

## v2.2.1 (30/06/2018)
This is a hotfix release which targets issue [#481](https://github.com/jopohl/urh/issues/481), so if you had problems with a missing ``` config.pxi ``` make sure to use this version.

## v2.2.0 (29/06/2018)
__Import announcement if you build URH manually__: Cython is now a __required__ dependency to build URH. If you install URH from PyPi (with ``` pip ```) or use the ``` .msi ``` installer you will not notice any difference. However, if you run URH from source you need to install cython which is as easy as ``` python3 -m pip install cython ```.

- [#478](https://github.com/jopohl/urh/pull/478) - make message pause configurable in simulator
- [#476](https://github.com/jopohl/urh/pull/476) - add padding when sending very short messages with soundcard
- [#473](https://github.com/jopohl/urh/pull/473) - move ``` .desktop ``` file to ``` data ``` folder. __Important if you build a package of URH__
- [#471](https://github.com/jopohl/urh/pull/471) - make relative external programs paths relative to project path
- [#470](https://github.com/jopohl/urh/pull/470) - improve conditional compiling of native device extensions
- [#469](https://github.com/jopohl/urh/pull/469) - improve device selection in options, use a table instead of a list view
- [#468](https://github.com/jopohl/urh/pull/468) - improve python2 interpreter settings for GNU Radio backend with empty ``` urh.ini ```
- [#458](https://github.com/jopohl/urh/pull/458) - add alignment action to analysis
![alignment image](https://i.imgur.com/xQt7H7Y.png)



## v2.1.1 (17/06/2018)
This release updates the bundled SDR drivers on Windows.
__Furthermore, this release adds native device support for 32 bit windows__.

Bugfix:
- a bug was fixed where sample rate of a signal was not written correctly to wav file when exporting as wav


## v2.1.0 (01/06/2018)
The highlight of this release is a __Command Line Interface__ (CLI) for the Universal Radio Hacker.
Learn more about this new feature [in the wiki](https://github.com/jopohl/urh/wiki/Command-Line-Interface).

Moreover, these two features were added:
- Add export features #437
- make refin and refout configurable for CRC #439

These bugs were fixed:
- fix #441 (Reference signal is not kept when disabling and re-enabling "Mark diffs in protocol")
- fix #442 (consider hidden zeros for show selection in interpretation)
- fix #444 (Message Break error box popping up too early)
- fix #448 (Include pyaudio in windows package for soundcard support)



## v2.0.4 (06/05/2018)

This version fixes a bug when importing 24 bit wav files on windows.



## v2.0.3 (06/05/2018)
- Improve external program behaviour in Simulator #417
- fix #421
- Improve simulator useability #422
- Improve transcript for external programs #425
- make endianness selectable in order column #428
- UI improvements #430
- add support for soundcards as new SDR device #433
- Multi device support #432
- add support for 24bit wav #434


## v2.0.2 (22/04/2018)
- Improve external program behaviour in Simulator #417
- fix #421
- Improve simulator useability #422
- Improve transcript for external programs #425
- make endianness selectable in order column #428
- UI improvements #430


## v2.0.1 (23/03/2018)
Changes:
- improve appearance of splitters
- add adaptive noise feature for protocol sniffer and simulator (#401)
- improve native device rebuild button in options + added a new button to view the build log there (only visible after hitting the rebuild button)  (#402)
- improve performance of CRC calculation (#412)
- save number of sending repeats when changed in send dialog (#415)


## v2.0.0 (28/02/2018)
URH 2.0 is here! This release adds a new tab to the main interface. This __Simulator__ tab enables you to simulate certain devices and crack even sophisticated security mechanisms like challenge response procedures. Learn more about this new feature [on this wiki page](https://github.com/jopohl/urh/wiki/Simulator).

Moreover, the overall performance and stability of URH increases with 2.0. The most notable changes are:
- improve accuracy when sending messages with short pauses
- improve accuracy of protocol sniffer
- allow setting lower frequencies for HackRF (#396)
- consider latest changes of LimeSuite API (#397)
- add timestamp to protocol sniffer output (#392)
- improve performance of modulations
- improve performance of filtering in analysis
- improve performance when starting sending
- improve send accuracy of HackRF
- improve performance when filtering messages in Analysis


## v1.9.2 (19/01/2018)
- Add BCD (Binary Coded Decimal) as new display format #386
- Make bit order configurable in analysis view table #390
- Improved loading of protocol files


## v1.9.1 (17/12/2017)

This is a hotfix release that fixes an error with HackRF receiving (#379).



## v1.9.0 (15/12/2017)
- added native support for SDRplay (#378)
- improved performance for continuous send mode
- added collapsable comboboxes to device dialog



## v1.8.17 (04/12/2017)
Changes:
- show warning at bottom if no project loaded (#374)
- if no project is opened an new project is created, add currently opnened files to new project (#374)
- add --version flag to command line script #375 (thanks to @Funcan for the initial work)
- Enable specifying a custom python 2 interpreter on Windows (#372)


## v1.8.16 (30/11/2017)

This release fixes an issue on Windows where processes ended with an error (#370).

Furthermore, the NetworkSDR can now be used in continuous send mode (#369).



## v1.8.15 (27/11/2017)

This release fixes a problem with GNU Radio backend on Windows mentioned in #366 and #368.



## v1.8.14 (26/11/2017)
This release fixes an overflow error (#364) when modulating very long messages in Generator.

The highlight of this release is an enhanced spectrum analyzer (#365) with __increased performance__ and a __waterfall plot__ to have a different, time based perspective on the spectrum.
![spectrum](https://user-images.githubusercontent.com/18219846/33239754-03bb62f6-d2a9-11e7-80aa-059df7b0b133.png)




## v1.8.13 (18/11/2017)

This release enhances the stability for sending and receiving with all SDRs. Especially, it fixes nasty bug #360 which affected HackRF users under Windows.

Furthermore, the WAV file support was greatly enhanced. Now, you can use WAV files from SDR# (fix #359).



## v1.8.12 (16/11/2017)

This release fixes the following issues:

- fix #355 - added a CSV import wizard for generic support of USB oscilloscopes
- fix #358 - MSI version of URH did not start on Windows

__So if you had trouble to install the previous version on Windows make sure you use this one.__



## v1.8.11 (13/11/2017)

The following issues were fixed in this release:

- fix #343 - crash when entering bits on empty position in Analysis / Generation
- fix #344 - bandpass filter can now also work with negative frequencies
- fix #346 - bandpass filter operations now run in a separate process and can be canceled with the ESC button
- fix #349 - added a csv import to work with USB oscilloscopes
- fix #352 - added a advanced modulation menu in Interpretation where a minimum message length for ASK can be configured



## v1.8.10 (21/10/2017)

This release fixes a crash when pressing the replay button in interpretation tab.



##  (21/10/2017)



## v1.8.8 (16/10/2017)

These issues were fixed in this release: 

- fix #339 - keep tree in analysis collapsed if check box toggled
- fix #338 - make pause threshold configurable in interpretation
- fix #333 - keep search string if search fails in analysis



## v1.8.7 (18/09/2017)
This release fixes the following issues:
 
 - [#330](https://github.com/jopohl/urh/pull/330) - Improve modulation for large protocols
 - [#329](https://github.com/jopohl/urh/pull/329) - Improve handling of protocol files
 - [#324](https://github.com/jopohl/urh/issues/324) - LimeSDR: Failed to receive stream
 - [#297](https://github.com/jopohl/urh/issues/297) - LimeSDR RX antenna always LNA_L


## v1.8.6 (06/09/2017)

This release fixes two crashes as described in #327.



## v1.8.5 (30/08/2017)

This release fixes #323 .



## v1.8.4 (28/08/2017)

This is a hotfix release that fixes native device extensions on Windows when conflicting SDR software is installed.
Furthermore, a health check button for native device extensions was added to options.

Details can be found in this PR: #321



## Version 1.8.0 (24/08/2017)

This release adds two highly demanded features to URH: __Spectrogram View__ and __Channel Separation__. Learn more about them in the [wiki](https://github.com/jopohl/urh/wiki/Spectrogram) and keep hacking like a boss!



## Version 1.7.1 (19/07/2017)

This release adds installers for Windows. If you use the new installer and should get an error about missing ``` api-ms-win-crt-runtime-l1-1-0.dll ```, run Windows Update or directly install [KB2999226](https://support.microsoft.com/en-us/help/2999226/update-for-universal-c-runtime-in-windows).
__It is recommended to use the 64 bit version (amd64) of URH on Windows__, because 32 bit version has no native device support.

This release also fixes some bugs:

- Fix exhaustive fuzzing mode
- Fix a rare crash in Generator tab when performing undo
- fix checksum assignment to fuzzed messages when sending/generating data
- refresh estimated time in generator if pause was edited


## Version 1.7.0 (14/07/2017)
The highlight of this release is support for __generic checksums__. You can define custom CRC polynomials or use predefined ones.
Learn more about this feature [in the wiki](https://github.com/jopohl/urh/wiki/Checksums).

Other fixes/features include:
- "Edit all" action in pause menu of generator tab
- Open Project now additionally possible by opening the project file
- bootstrapping of modulation when dropping first protocol to generator table
- new icons and improved UI
- improved auto detection of carrier frequency for modulation
- improved ASK demodulation algorithm
- fix a bug with relative paths on OS X
- fix selection behavior when extending selection with shift
- fix #306
- fix #308
- fix #310
- fix #311



## Hotfix for Windows wheels (11/06/2017)

This is a hotfix release that fixes dependencies in the precompiled wheels for Windows which were introduced in the previous release.



## Version 1.6.5 (11/06/2017)
This release brings the following changes:

- fix #278: added a __repeat button__ to fuzzing dialog, next to the table with fuzzing values
- fix #284: fixed behaviour: "Your selection is empty!" sometimes pops up when creating a new signal from signal
- fix #285: fixed a rare crash when undoing a crop action
- fix #281: Optimized performance of protocol synchronization in Interpretation
- fix #286: improved context menu in Analysis
- fix #288: UI improvements: remove unneeded borders and increase visibility of splitter handle
- fix #290: fixed a crash occurring when pressing Analysis button in certain circumstances
- fix #291: created precompiled wheels for windows on PyPI, so no C++ compiler needed anymore.
- improved visual appearance of comboboxes in protocol label list view


## Add filter to Interpretation (28/05/2017)
This release brings a filter button to the Interpretation phase:
![bildschirmfoto_2017-05-28_12-29-58](https://cloud.githubusercontent.com/assets/18219846/26528462/a20c36ce-43ac-11e7-815e-0d929aa20cb8.png)

This way, you can smooth your signals right inside URH or unlock the full power of DSP fir filters by defining custom filters through the menu!
