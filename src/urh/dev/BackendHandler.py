import os
import sys
from enum import Enum
from subprocess import call, DEVNULL

from urh import settings
from urh.util.Logger import logger


class Backends(Enum):
    none = "no available backend"
    native = "native backend"
    grc = "GNU Radio backend"
    network = "Network Backend"  # provided by network sdr plugin


class BackendContainer(object):
    def __init__(self, name, avail_backends: set, supports_rx: bool, supports_tx: bool):
        self.name = name
        self.avail_backends = avail_backends
        self.selected_backend = Backends[
            settings.read(name + "_selected_backend", "none")
        ]
        if self.selected_backend not in self.avail_backends:
            self.selected_backend = Backends.none

        if self.selected_backend == Backends.none:
            if Backends.native in self.avail_backends:
                self.selected_backend = Backends.native
            elif Backends.grc in self.avail_backends:
                self.selected_backend = Backends.grc

        self.is_enabled = settings.read(name + "_is_enabled", True, bool)
        self.__supports_rx = supports_rx
        self.__supports_tx = supports_tx
        if len(self.avail_backends) == 0:
            self.is_enabled = False

    def __repr__(self):
        return (
            "avail backends: "
            + str(self.avail_backends)
            + "| selected backend:"
            + str(self.selected_backend)
        )

    @property
    def supports_rx(self) -> bool:
        return self.__supports_rx

    @property
    def supports_tx(self) -> bool:
        return self.__supports_tx

    @property
    def has_gnuradio_backend(self):
        return Backends.grc in self.avail_backends

    @property
    def has_native_backend(self):
        return Backends.native in self.avail_backends

    def set_enabled(self, enabled: bool):
        self.is_enabled = enabled
        self.write_settings()

    def set_selected_backend(self, sel_backend: Backends):
        self.selected_backend = sel_backend
        self.write_settings()

    def write_settings(self):
        settings.write(self.name + "_is_enabled", self.is_enabled)

        if self.selected_backend == Backends.grc and len(self.avail_backends) == 1:
            # if GNU Radio is the only backend available we do not save it to ini,
            # in order to auto enable native backend if a native extension is built afterwards
            # see: https://github.com/jopohl/urh/issues/270
            pass
        else:
            settings.write(self.name + "_selected_backend", self.selected_backend.name)


class BackendHandler(object):
    """
    This class controls the devices backend.
    1) List available backends for devices
    2) List available devices (at least one backend)
    3) Manage the selection of devices backend

    """

    DEVICE_NAMES = (
        "AirSpy R2",
        "AirSpy Mini",
        "BladeRF",
        "FUNcube",
        "HackRF",
        "Rad1o",
        "LimeSDR",
        "PlutoSDR",
        "RTL-SDR",
        "RTL-TCP",
        "SDRPlay",
        "SoundCard",
        "USRP",
    )

    def __init__(self):
        self.__gr_python_interpreter = settings.read("gr_python_interpreter", "")
        if not self.__gr_python_interpreter:
            self.__gr_python_interpreter = settings.read("python2_exe", "")  # legacy

        self.set_gnuradio_installed_status()

        if not hasattr(sys, "frozen"):
            self.path = os.path.dirname(os.path.realpath(__file__))
        else:
            self.path = os.path.dirname(sys.executable)

        self.device_backends = {}
        """:type: dict[str, BackendContainer] """

        self.get_backends()

    @property
    def gr_python_interpreter(self):
        return self.__gr_python_interpreter

    @gr_python_interpreter.setter
    def gr_python_interpreter(self, value):
        if value != self.__gr_python_interpreter:
            self.__gr_python_interpreter = value
            self.set_gnuradio_installed_status(force=True)
            settings.write("gr_python_interpreter", value)

    @property
    def num_native_backends(self):
        return len(
            [
                dev
                for dev, backend_container in self.device_backends.items()
                if Backends.native in backend_container.avail_backends
                and dev.lower() != "rtl-tcp"
            ]
        )

    @property
    def __plutosdr_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import plutosdr

            return True
        except ImportError:
            return False

    @property
    def __bladerf_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import bladerf

            return True
        except ImportError:
            return False

    @property
    def __hackrf_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import hackrf

            return True
        except ImportError:
            return False

    @property
    def __usrp_native_enabled(self) -> bool:
        old_stdout = devnull = None
        try:
            try:
                # Redirect stderr to /dev/null to hide USRP messages
                devnull = open(os.devnull, "w")
                old_stdout = os.dup(sys.stdout.fileno())
                os.dup2(devnull.fileno(), sys.stdout.fileno())
            except:
                pass

            from urh.dev.native.lib import usrp

            return True
        except ImportError:
            return False
        finally:
            if old_stdout is not None:
                os.dup2(old_stdout, sys.stdout.fileno())
            if devnull is not None:
                devnull.close()

    @property
    def __soundcard_enabled(self) -> bool:
        try:
            import pyaudio

            return True
        except ImportError:
            return False

    @property
    def __airspy_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import airspy

            return True
        except ImportError:
            return False

    @property
    def __lime_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import limesdr

            return True
        except ImportError:
            return False

    @property
    def __rtlsdr_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import rtlsdr

            return True
        except ImportError:
            return False

    @property
    def __sdrplay_native_enabled(self) -> bool:
        try:
            from urh.dev.native.lib import sdrplay

            return True
        except ImportError:
            return False

    def __check_gr_python_interpreter(self, interpreter):
        # Use shell=True to prevent console window popping up on windows
        return (
            call(
                '"{0}" -c "import gnuradio"'.format(interpreter),
                shell=True,
                stderr=DEVNULL,
            )
            == 0
        )

    def set_gnuradio_installed_status(self, force=False):
        current_setting = settings.read("gnuradio_is_installed", -1, int)
        if not force and current_setting != -1:
            self.gnuradio_is_installed = bool(current_setting)
            return

        if os.path.isfile(self.gr_python_interpreter) and os.access(
            self.gr_python_interpreter, os.X_OK
        ):
            try:
                self.gnuradio_is_installed = self.__check_gr_python_interpreter(
                    self.gr_python_interpreter
                )
            except OSError:
                self.gnuradio_is_installed = False
        else:
            self.gnuradio_is_installed = False

        settings.write("gnuradio_is_installed", int(self.gnuradio_is_installed))

    def __device_has_gr_scripts(self, devname: str):
        if not hasattr(sys, "frozen"):
            script_path = os.path.join(self.path, "gr", "scripts")
        else:
            script_path = self.path
        devname = devname.lower().split(" ")[0]
        has_send_file = False
        has_recv_file = False
        for f in os.listdir(script_path):
            if f == "{0}_send.py".format(devname):
                has_send_file = True
            elif f == "{0}_recv.py".format(devname):
                has_recv_file = True

        return has_recv_file, has_send_file

    def __avail_backends_for_device(self, devname: str):
        backends = set()
        supports_rx, supports_tx = self.__device_has_gr_scripts(devname)
        if self.gnuradio_is_installed and (supports_rx or supports_tx):
            backends.add(Backends.grc)

        if devname.lower() == "plutosdr" and self.__plutosdr_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower() == "bladerf" and self.__bladerf_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower() == "hackrf" and self.__hackrf_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower() == "rad1o" and self.__hackrf_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower() == "usrp" and self.__usrp_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower() == "limesdr" and self.__lime_native_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        if devname.lower().startswith("airspy") and self.__airspy_native_enabled:
            supports_rx, supports_tx = True, False
            backends.add(Backends.native)

        if (
            devname.lower().replace("-", "") == "rtlsdr"
            and self.__rtlsdr_native_enabled
        ):
            supports_rx, supports_tx = True, False
            backends.add(Backends.native)

        if devname.lower().replace("-", "") == "rtltcp":
            supports_rx, supports_tx = True, False
            backends.add(Backends.native)

        if devname.lower() == "sdrplay" and self.__sdrplay_native_enabled:
            supports_rx, supports_tx = True, False
            backends.add(Backends.native)

        if devname.lower() == "soundcard" and self.__soundcard_enabled:
            supports_rx, supports_tx = True, True
            backends.add(Backends.native)

        return backends, supports_rx, supports_tx

    def get_backends(self):
        self.device_backends.clear()
        for device_name in self.DEVICE_NAMES:
            ab, rx_suprt, tx_suprt = self.__avail_backends_for_device(device_name)
            container = BackendContainer(device_name.lower(), ab, rx_suprt, tx_suprt)
            self.device_backends[device_name.lower()] = container

    def get_key_from_device_display_text(self, displayed_device_name):
        displayed_device_name = displayed_device_name.lower()
        for key in self.DEVICE_NAMES:
            key = key.lower()
            if displayed_device_name.startswith(key):
                return key
        return None

    @staticmethod
    def perform_soundcard_health_check():
        result = "SoundCard -- "
        try:
            import pyaudio

            return result + "OK"
        except Exception as e:
            return result + str(e)
