import array
import copy
import os
import sys
import tempfile

from PyQt5.QtGui import QIcon
from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import settings
from urh.dev.PCAP import PCAP
import urh.dev.PCAPNG as PCAPNG
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.util import util
from urh.util.Logger import logger
from urh.cythonext import util as c_util


class TestUtil(QtTestCase):
    def test_set_icon_theme(self):
        settings.write("icon_theme_index", 0)
        util.set_icon_theme()

        self.assertEqual(QIcon.themeName(), "oxy")

        settings.write("icon_theme_index", 1)
        util.set_icon_theme()

        if sys.platform == "linux":
            self.assertNotEqual(QIcon.themeName(), "oxy")
        else:
            self.assertEqual(QIcon.themeName(), "oxy")

    def test_set_shared_lib_path(self):
        before = os.environ["PATH"]
        util.set_shared_library_path()

    def test_create_textbox_dialog(self):
        dialog = util.create_textbox_dialog("Test content", "Test title", parent=self.form)
        self.assertEqual(dialog.windowTitle(), "Test title")
        self.assertEqual(dialog.layout().itemAt(0).widget().toPlainText(), "Test content")
        dialog.close()

    def test_get_receive_buffer_size(self):
        settings.OVERWRITE_RECEIVE_BUFFER_SIZE = None
        ns = settings.get_receive_buffer_size(resume_on_full_receive_buffer=True, spectrum_mode=True)
        self.assertEqual(ns, settings.SPECTRUM_BUFFER_SIZE)

        ns = settings.get_receive_buffer_size(resume_on_full_receive_buffer=True, spectrum_mode=False)
        self.assertEqual(ns, settings.SNIFF_BUFFER_SIZE)

        ns1 = settings.get_receive_buffer_size(resume_on_full_receive_buffer=False, spectrum_mode=True)
        ns2 = settings.get_receive_buffer_size(resume_on_full_receive_buffer=False, spectrum_mode=False)
        self.assertEqual(len(str(ns1)), len(str(ns2)))

    def test_write_pcap(self):
        signal = Signal(get_path_for_data_file("ask.complex"), "ASK-Test")
        signal.modulation_type = "ASK"
        signal.samples_per_symbol = 295
        signal.center = -0.1667
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.decoded_hex_str[0], "b25b6db6c80")

        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))

        pcap = PCAP()
        pcap.write_packets(proto_analyzer.messages, os.path.join(tempfile.gettempdir(), "test.pcap"), 1e6)

    def test_write_pcapng(self):
        signal = Signal(get_path_for_data_file("ask.complex"), "ASK-Test")
        signal.modulation_type = "ASK"
        signal.samples_per_symbol = 295
        signal.center = -0.1667
        self.assertEqual(signal.num_samples, 13710)

        proto_analyzer = ProtocolAnalyzer(signal)
        proto_analyzer.get_protocol_from_signal()
        self.assertEqual(proto_analyzer.decoded_hex_str[0], "b25b6db6c80")

        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))
        proto_analyzer.messages.append(copy.deepcopy(proto_analyzer.messages[0]))

        filepath = os.path.join(tempfile.gettempdir(), "test.pcapng")
        PCAPNG.create_pcapng_file(filepath, "Universal Radio Hacker Test", "TestHW", 147)
        PCAPNG.append_packets_to_pcapng(
            filename=filepath,
            packets=(msg.decoded_ascii_buffer for msg in proto_analyzer.messages),
            timestamps=(msg.timestamp for msg in proto_analyzer.messages))

        # As we don't have PCAPNG importers, we'll verify output just by checking file size, PCAPNG SHB type number
        # and that all msg bytes were written somewhere inside output file
        filechecks = False
        if os.path.isfile(filepath):                                     # ok, file exist
            with open(filepath, "rb") as f:
                filecontents = f.read()
            # min file len= SHB + IDB + 4 EPB msgs
            minfilelen = 28 + 20 + (4 * (32 + len(proto_analyzer.messages[0].decoded_ascii_buffer)))
            if len(filecontents) >= minfilelen:                          # ok, min file length passed
                if filecontents.find(b'\x0A\x0D\x0D\x0A') >= 0:          # ok, seems that SHB was written
                    if filecontents.find(proto_analyzer.messages[0].decoded_ascii_buffer) >= 0: # ok, msg bytes written
                        filechecks = True
                
        self.assertTrue(filechecks)

    def test_de_bruijn_fuzzing(self):
        self.assertEqual(c_util.de_bruijn(3), array.array("B", [0, 0, 0, 1, 0, 1, 1, 1]))
        self.assertEqual(c_util.de_bruijn(4), array.array("B", [0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1]))

    def test_native_backends_installed(self):
        from urh.util import util

        if not util.get_shared_library_path():
            logger.info("Shared library dir not found, skipping check of native device extensions")
            return

        util.set_shared_library_path()

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import airspy

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import bladerf

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import hackrf

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import rtlsdr

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import limesdr

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import plutosdr

        # noinspection PyUnresolvedReferences
        from urh.dev.native.lib import usrp

        if sys.platform != "darwin":
            # noinspection PyUnresolvedReferences
            from urh.dev.native.lib import sdrplay
        self.assertTrue(True)
