from collections import OrderedDict, namedtuple

import copy

from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin

DEVICE_CONFIG = OrderedDict()

dev_range = namedtuple("dev_range", ["start", "stop", "step"])

M = 10**6
G = 10 ** 9
# https://github.com/mossmann/hackrf/wiki/HackRF-One#features
DEVICE_CONFIG["HackRF"] = {
    "center_freq": dev_range(start=1*M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2*M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "rf_gain": dev_range(start=0, stop=14, step=14),
    "if_gain": dev_range(start=0, stop=40, step=8),
    "baseband_gain": dev_range(start=0, stop=47, step=1)  # only available in RX
}

# https://kb.ettus.com/About_USRP_Bandwidths_and_Sampling_Rates
DEVICE_CONFIG["USRP"] = {
    "center_freq": dev_range(start=0, stop=6 * G, step=1),
    "sample_rate": dev_range(start=1, stop=200 * M, step=1),
    "bandwidth": dev_range(start=1, stop=120 * M, step=1),
    "device_args": "",
    "ip": "",
    "rf_gain": dev_range(start=0, stop=100, step=1),
    "antenna": dev_range(start=0, stop=1, step=1)
}

# http://osmocom.org/projects/sdr/wiki/rtl-sdr
DEVICE_CONFIG["RTL-SDR"] = {
    "center_freq": dev_range(start=22 * M, stop=2200 * M, step=1),
    "sample_rate": dev_range(start=1, stop=int(3.2 * M), step=1),
    "bandwidth": dev_range(start=1, stop=int(3.2 * M), step=1),
    "rf_gain": dev_range(start=0, stop=50, step=1),  # CAUTION: API is *10 so e.g. 1 needs to be given as 10 to API
    "direct_sampling": dev_range(start=0, stop=2, step=1),  # 0 disabled, 1 I-ADC input enabled, 2 Q-ADC input enabled
    "freq_correction": dev_range(start=-1 * 10 ** 3, stop=1 * 10 ** 3, step=1)
}

DEVICE_CONFIG["RTL-TCP"] = copy.deepcopy(DEVICE_CONFIG["RTL-SDR"])
DEVICE_CONFIG["RTL-TCP"]["ip"] = ""
DEVICE_CONFIG["RTL-TCP"]["port"] = ""

DEVICE_CONFIG[NetworkSDRInterfacePlugin.NETWORK_SDR_NAME] = {}

DEVICE_CONFIG["Fallback"] = {
    "center_freq": dev_range(start=1*M, stop=6 * G, step=1),
    "sample_rate": dev_range(start=2 * M, stop=20 * M, step=1),
    "bandwidth": dev_range(start=2 * M, stop=20 * M, step=1),
    "rf_gain": dev_range(start=0, stop=50, step=1),
}
