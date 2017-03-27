import sys

from tests.QtTestCase import QtTestCase


class TestWhitening(QtTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_native_backends_installed(self):
        if sys.platform == "win32":
            import os
            cur_dir = os.path.dirname(__file__) if not os.path.islink(__file__) else os.path.dirname(
                os.readlink(__file__))
            dll_dir = os.path.realpath(os.path.join(cur_dir, "..", "src", "urh", "dev", "native", "lib", "win"))
            os.environ['PATH'] = dll_dir + ';' + os.environ['PATH']

            # noinspection PyUnresolvedReferences
            from urh.dev.native.lib import hackrf

            # noinspection PyUnresolvedReferences
            from urh.dev.native.RTLSDR import RTLSDR

        self.assertTrue(True)
