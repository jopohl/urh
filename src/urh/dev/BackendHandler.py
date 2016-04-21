from urh import constants
import os
import sys
from enum import Enum

class Backends(Enum):
    native = 1
    grc = 2


class BackendContainer(object):
    def __init__(self, avail_backends: set, selected_backend: Backends):
        self.avail_backends = avail_backends
        self.selected_backend = selected_backend

    def __repr__(self):
        return "avail backends: " +str(self.avail_backends) + "| selected backend:" + str(self.selected_backend)

class BackendHandler(object):
    """
    This class controls the devices backend.
    1) List available backends for devices
    2) List available devices (atleast one backend)
    3) Manage the selection of devices backend
    4) provide wrapper methods for devices for calling with the right backend

    """



    DEVICE_NAMES = ("HackRF", "USRP")

    def __init__(self):
        self.gnuradio_exe = constants.SETTINGS.value('gnuradio_exe')
        self.python2_exe = constants.SETTINGS.value('python2_exe')
        if not hasattr(sys, 'frozen'):
            self.path = os.path.dirname(os.path.realpath(__file__))
        else:
            self.path = os.path.join(os.path.dirname(sys.executable), "dev")

        self.device_backends = {}
        self.get_backends()

    @property
    def avail_devices(self):
        return set(devname for devname in self.DEVICE_NAMES if len(self.device_backends[devname.lower()].avail_backends) > 0)

    @property
    def gnuradio_installed(self) -> bool:
        return os.path.isfile(self.gnuradio_exe) and os.path.isfile(self.python2_exe)

    @property
    def hackrf_native_enabled(self) -> bool:
         try:
             from urh.dev.native.lib import hackrf
             return True
         except ImportError:
             return False

    @property
    def usrp_native_enabled(self) -> bool:
         try:
             from urh.dev.native.lib import uhd
             return True
         except ImportError:
             return False

    def device_has_gr_scripts(self, devname: str):
        script_path = os.path.join(self.path, "gr", "scripts")
        devname = devname.lower()
        has_send_file = False
        has_recv_file = False

        for f in os.listdir(script_path):
            if f == "{0}_send.py".format(devname):
                has_send_file = True
            elif f == "{0}_recv.py".format(devname):
                has_recv_file = True

        return has_send_file and has_recv_file

    def avail_backends_for_device(self, devname: str):
        backends = set()
        if self.gnuradio_installed and self.device_has_gr_scripts(devname):
            backends.add(Backends.grc)

        if devname.lower() == "hackrf" and self.hackrf_native_enabled:
            backends.add(Backends.native)

        if devname.lower() == "usrp" and self.usrp_native_enabled:
            backends.add(Backends.native)

        return backends

    def get_backends(self):
        self.device_backends.clear()
        for device_name in self.DEVICE_NAMES:
            ab = self.avail_backends_for_device(device_name)
            sb = None # TODO read from settings
            self.device_backends[device_name.lower()] = BackendContainer(ab, sb)

if __name__ == "__main__":
    bh = BackendHandler()
    print(bh.device_backends)