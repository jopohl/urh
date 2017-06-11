import sys
import platform

from tests.QtTestCase import QtTestCase


class TestWinNativeBackend(QtTestCase):
    def test_native_backends_installed(self):
        if sys.platform == "win32":
            if platform.architecture()[0] == "64bit":
                from urh.util import util

                util.set_windows_lib_path()

                # noinspection PyUnresolvedReferences
                from urh.dev.native.lib import hackrf

                # noinspection PyUnresolvedReferences
                from urh.dev.native.lib import rtlsdr

                # noinspection PyUnresolvedReferences
                from urh.dev.native.lib import airspy

                # noinspection PyUnresolvedReferences
                from urh.dev.native.lib import limesdr

            else:
                print("Native Windows device extensions are currently only supported on 64 Bit.")

        self.assertTrue(True)
