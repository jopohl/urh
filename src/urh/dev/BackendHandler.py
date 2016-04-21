from urh import constants
import os
import sys

class BackendHandler(object):
    """
    This class controls the devices backend.
    1) List available backends for devices
    2) List avaibale devices (atleast one backend)
    3) Manage the selection of devices backend
    4) provide wrapper methods for devices for calling with the right backend

    """
    DEVICES = ("HackRF", "USRP")

    def __init__(self):
        self.gnuradio_exe = constants.SETTINGS.value('gnuradio_exe')
        self.python2_exe = constants.SETTINGS.value('python2_exe')
        if not hasattr(sys, 'frozen'):
            self.path = os.path.dirname(os.path.realpath(__file__))
        else:
            self.path = os.path.join(os.path.dirname(sys.executable), "dev")

    @property
    def gnuradio_installed(self) -> bool:
        return os.path.isfile(self.gnuradio_exe) and os.path.isfile(self.python2_exe)
    #
    # @property
    # def hackrf_native_enabled(self) -> bool:
    #     try:
