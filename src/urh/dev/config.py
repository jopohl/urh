from collections import OrderedDict

DEVICE_CONFIG = OrderedDict()

# List = supported values
# Tuple = start/end for range

# https://github.com/mossmann/hackrf/wiki/HackRF-One#features
DEVICE_CONFIG["HackRF"] = {
    "center_freq": (10**6, 6*10**9),
    "sample_rate": (2*10**6, 20*10**6),
    "bandwidth": (2*10**6, 20*10**6),
    "rf_gain": [0, 14],
    "if_gain": list(range(0, 41, 8)),
    "baseband_gain": list(range(0, 48))  # only available in RX
}

# https://kb.ettus.com/About_USRP_Bandwidths_and_Sampling_Rates
DEVICE_CONFIG["USRP"] = {
    "center_freq": (0, 6*10**9),
    "sample_rate": (1, 200*10**6),
    "bandwidth": (1, 120*10**6),
    "device_args": "",
    "rf_gain": (0, 100),
    "antenna": [0, 1],
}
