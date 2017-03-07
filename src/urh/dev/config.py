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

# http://osmocom.org/projects/sdr/wiki/rtl-sdr
DEVICE_CONFIG["RTLSDR"] = {
    "center_freq": (22*10**6, 2200*10**6),
    "sample_rate": (1, int(3.2*10**6)),
    "bandwidth": (1, int(3.2*10**6)),
    "rf_gain": (0, 50),  # CAUTION: API is *10 so e.g. 1 needs to be given as 10 to API
    "direct_sampling": [0, 1, 2],  # 0 means disabled, 1 I-ADC input enabled, 2 Q-ADC input enabled
    "freq_correction": (-1*10**3, 1*10**3)
}

DEVICE_CONFIG["Fallback"] = {
    "center_freq": (10**6, 6*10**9),
    "sample_rate": (2*10**6, 20*10**6),
    "bandwidth": (2*10**6, 20*10**6),
    "rf_gain": (0, 50),
}
