from collections import OrderedDict

DEVICE_CONFIG = OrderedDict()

# List = supported values
# Tuple = start/end for range

# https://github.com/mossmann/hackrf/wiki/HackRF-One#features
DEVICE_CONFIG["HackRF"] = {
    "frequency": (10**6, 6*10**9),
    "sample_rate": (2*10**6, 20*10**6),
    "bandwidth": (2*10**6, 20*10**6),
    "rf_gain": [0, 14],
    "if_gain": list(range(0, 41, 8)),
    "baseband_gain": list(range(0, 48))  # only available in RX
}
