import sys
import platform

from tests.QtTestCase import QtTestCase


class TestWinNativeBackend(QtTestCase):
    def test_native_backends_installed(self):
        if sys.platform == "win32":
            if platform.architecture()[0] == "64bit":
                import os
                cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(
                    os.readlink(__file__))
                dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
                os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']

                # noinspection PyUnresolvedReferences
                from urh.dev.native.lib import hackrf

                # noinspection PyUnresolvedReferences
                from urh.dev.native.RTLSDR import RTLSDR
            else:
                print("Native Windows device extensions are currently only supported on 64 Bit.")

        self.assertTrue(True)
