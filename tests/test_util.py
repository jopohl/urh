import os
import sys

import copy
import tempfile
import platform

from PyQt5.QtGui import QIcon

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.dev.PCAP import PCAP
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.util import util


class TestUtil(QtTestCase):
    def test_set_icon_theme(self):
        constants.SETTINGS.setValue("icon_theme_index", 0)
        util.set_icon_theme()

        self.assertEqual(QIcon.themeName(), "oxy")

        constants.SETTINGS.setValue("icon_theme_index", 1)
        util.set_icon_theme()

        if sys.platform == "linux":
            self.assertNotEqual(QIcon.themeName(), "oxy")
        else:
            self.assertEqual(QIcon.themeName(), "oxy")

    def test_set_windows_lib_path(self):
        before = os.environ["PATH"]
        util.set_windows_lib_path()

        if sys.platform == "win32":
            self.assertNotEqual(before, os.environ["PATH"])
        else:
            self.assertEqual(before, os.environ["PATH"])

    def test_create_textbox_dialog(self):
        dialog = util.create_textbox_dialog("Test content", "Test title", parent=self.form)
        self.assertEqual(dialog.windowTitle(), "Test title")
        self.assertEqual(dialog.layout().itemAt(0).widget().toPlainText(), "Test content")
        dialog.close()

    def test_write_pcap(self):
        signal = Signal(get_path_for_data_file("ask.complex"), "ASK-Test")
        signal.modulation_type = 0
        signal.bit_len = 295
        signal.qad_center = -0.1667
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.decoded_hex_str[0], "b25b6db6c80")

        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))

        pcap = PCAP()
        pcap.write_packets(proto_analyzer.messages, os.path.join(tempfile.gettempdir(), "test.pcap"), 1e6)

    def test_windows_native_backends_installed(self):
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
