import numpy as np


class LiveAutoInterpreter(object):
    BUFFER_SIZE_MB = 50

    def __init__(self, bit_len=100, center=0.0, noise=0.0, modulation_type="FSK"):
        self.modulation_type = modulation_type
        self.bit_length = bit_len

        self.noise = noise
        self.center = center

        self.__buffer = np.zeros(int(self.BUFFER_SIZE_MB * 1000 * 1000 / 8), dtype=np.complex64)

    def update(self, data: np.ndarray, update_noise=True, update_center=True):
        if not update_noise and not update_center:
            return

        # TODO
        self.noise = self.noise
        self.center = self.center