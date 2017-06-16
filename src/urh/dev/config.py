from collections import OrderedDict, namedtuple

import copy

from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin


DEFAULT_FREQUENCY = 433.92e6
DEFAULT_SAMPLE_RATE = 1e6
DEFAULT_BANDWIDTH = 1e6
DEFAULT_GAIN = 20
DEFAULT_IF_GAIN = 20
DEFAULT_BB_GAIN = 20
DEFAULT_FREQ_CORRECTION = 1
DEFAULT_DIRECT_SAMPLING_MODE = 0

DEVICE_CONFIG = OrderedDict()

dev_range = namedtuple("dev_range", ["start", "stop", "step"])

K = 10 ** 3
M = 10 ** 6
G = 10 ** 9
# https://github.com/mossmann/hackrf/wiki/HackRF-One#features
DEVICE_CONFIG["HackRF"] = {
    "center_freq": dev_range(start=1*M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2*M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "tx_rf_gain": [0, 14],
    "rx_rf_gain": [0, 14],
    "rx_if_gain": [0, 8, 16, 24, 32, 40],
    "tx_if_gain": list(range(0, 48)),
    "rx_baseband_gain": list(range(0, 63, 2))  # only available in RX
}

# https://kb.ettus.com/About_USRP_Bandwidths_and_Sampling_Rates
DEVICE_CONFIG["USRP"] = {
    "center_freq": dev_range(start=0, stop=6 * G, step=1),
    "sample_rate": dev_range(start=1, stop=200 * M, step=1),
    "bandwidth": dev_range(start=1, stop=120 * M, step=1),
    "device_args": "",
    "rx_rf_gain": list(range(0, 101)),
    "tx_rf_gain": list(range(0, 101)),
    "antenna": [0, 1]
}

# https://myriadrf.org/projects/limesdr/
DEVICE_CONFIG["LimeSDR"] = {
    "center_freq": dev_range(start=100 * K, stop=int(3.8 * G), step=1),
    "sample_rate": dev_range(start=2*M, stop=30 * M, step=1),
    "bandwidth": dev_range(start=2*M, stop=130 * M, step=1),
    "rx_rf_gain": list(range(0, 101)),  # Normalized Gain 0-100%
    "tx_rf_gain": list(range(0, 101)),  # Normalized Gain 0-100%
    "rx_channel": ["RX1", "RX2"],
    "tx_channel": ["TX1", "TX2"],
    "rx_antenna": ["None", "High (RX_H)", "Low (RX_L)", "Wide (RX_W)"],
    "rx_antenna_default_index": 2,
    "tx_antenna": ["None", "Band 1 (TX_1)", "Band 2 (TX_2)"],
    "tx_antenna_default_index": 1
}

# http://osmocom.org/projects/sdr/wiki/rtl-sdr
DEVICE_CONFIG["RTL-SDR"] = {
    # 0.1 MHz lower limit because: https://github.com/jopohl/urh/issues/211
    "center_freq": dev_range(start=0.1 * M, stop=2200 * M, step=1),
    "sample_rate": dev_range(start=1, stop=int(3.2 * M), step=1),
    "bandwidth": dev_range(start=1, stop=int(3.2 * M), step=1),
    "rx_rf_gain": list(range(0, 51)),  # CAUTION: API is *10 so e.g. 1 needs to be given as 10 to API
    "direct_sampling": ["disabled", "I-ADC input enabled", "Q-ADC input enabled"],
    "freq_correction": dev_range(start=-1 * 10 ** 3, stop=1 * 10 ** 3, step=1)
}

DEVICE_CONFIG["RTL-TCP"] = copy.deepcopy(DEVICE_CONFIG["RTL-SDR"])
DEVICE_CONFIG["RTL-TCP"]["ip"] = ""
DEVICE_CONFIG["RTL-TCP"]["port"] = ""

DEVICE_CONFIG[NetworkSDRInterfacePlugin.NETWORK_SDR_NAME] = {}

# http://www.rtl-sdr.com/review-airspy-vs-sdrplay-rsp-vs-hackrf/
DEVICE_CONFIG["AirSpy R2"] = {
    "center_freq": dev_range(start=24, stop=1800 * M, step=1),
    "sample_rate": [2.5*M, 10*M],
    "bandwidth": [2.5*M, 10*M],
    "rx_rf_gain":  list(range(0, 16)),
    "rx_if_gain":  list(range(0, 16)),
    "rx_baseband_gain":  list(range(0, 16)),
}

DEVICE_CONFIG["AirSpy Mini"] = {
    "center_freq": dev_range(start=24, stop=1800 * M, step=1),
    "sample_rate": [3*M, 6*M],
    "bandwidth": [3*M, 6*M],
    "rx_rf_gain":  list(range(0, 16)),
    "rx_if_gain":  list(range(0, 16)),
    "rx_baseband_gain":  list(range(0, 16)),
}

DEVICE_CONFIG["Fallback"] = {
    "center_freq": dev_range(start=1*M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2 * M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "rx_rf_gain":  list(range(0, 51)),
    "tx_rf_gain":  list(range(0, 51)),
}

#default_profile = {
#    "name": "Default",
#    "device": "HackRF",
#    "device_arguments": "",
#    "channel": 0,
#    "antenna": 0,
#    "ip_address": "127.0.0.1",
#    "port_number": 1234,
#    "frequency": DEFAULT_FREQUENCY,
#    "sample_rate": DEFAULT_SAMPLE_RATE,
#    "band_width": DEFAULT_BANDWIDTH,
#    "gain": self.ui.spinBoxGain.value(),
#    "if_gain": self.ui.spinBoxIFGain.value(),
#    "baseband_gain": self.ui.spinBoxBasebandGain.value(),
#    "frequency_correction": self.ui.spinBoxFreqCorrection.value(),
#    "direct_sampling": 0 if direct_sampling_index == -1 else direct_sampling_index,

#    "noise": self.ui.spinbox_sniff_Noise.value(),
#    "center": self.ui.spinbox_sniff_Center.value(),
#    "bit_length": self.ui.spinbox_sniff_BitLen.value(),
#    "error_tolerance": self.ui.spinbox_sniff_ErrorTolerance.value(),
#    "modulation": self.ui.combox_sniff_Modulation.currentIndex(),

#    "bw_sr_locked": self.ui.btnLockBWSR.isChecked()
#}

profiles = []