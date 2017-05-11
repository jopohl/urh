import psutil

from urh import constants
from urh.util.Formatter import Formatter
from urh.util.Logger import logger


class SettingsProxy(object):
    """
    Centralize common settings operations
    """
    @staticmethod
    def get_receive_buffer_size(resume_on_full_receive_buffer: bool, spectrum_mode: bool) -> int:
        if resume_on_full_receive_buffer:
            if spectrum_mode:
                num_samples = constants.SPECTRUM_BUFFER_SIZE
            else:
                num_samples = constants.SNIFF_BUFFER_SIZE
        else:
            # Take 60% of avail memory
            threshold = constants.SETTINGS.value('ram_threshold', 0.6, float)
            num_samples = threshold * (psutil.virtual_memory().available / 8)
        logger.info("Initializing receive buffer with size {0}B".format(Formatter.big_value_with_suffix(num_samples*8)))
        return int(num_samples)
