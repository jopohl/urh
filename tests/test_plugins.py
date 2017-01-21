import unittest

import math
from PyQt5.QtTest import QTest

from urh import constants
from urh.controller.MainController import MainController
from urh.plugins.MessageBreak.MessageBreakPlugin import MessageBreakPlugin
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.ZeroHide.ZeroHidePlugin import ZeroHidePlugin

__author__ = 'joe'

import tests.startApp

app = tests.startApp.app


class TestPlugins(unittest.TestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0) # Disable Symbols for this Test
        QTest.qWait(100)

        self.form = MainController()
        self.form.add_signalfile("./data/esaver.complex")
        QTest.qWait(100)
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

    def tearDown(self):
        constants.SETTINGS.setValue('rel_symbol_length', self.old_sym_len) # Restore Symbol Length

    def test_message_break_plugin(self):
        bp = MessageBreakPlugin()
        action = bp.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack,
                               (1, 1, 4, 4), self.cframe.proto_analyzer, 0)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)
        action.trigger()
        QTest.qWait(100)
        self.assertEqual(self.cframe.protocol_model.row_count, 4)

        self.cframe.protocol_undo_stack.undo()
        QTest.qWait(100)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

    def test_zero_hide_plugin_gui(self):
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377)
        zh = ZeroHidePlugin()
        zh.following_zeros = 188
        action = zh.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack, (),
                               self.cframe.proto_analyzer, 0)
        action.trigger()
        QTest.qWait(100)
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377 - 188)

        self.cframe.protocol_undo_stack.undo()
        QTest.qWait(100)
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377)

    def test_zero_hide_plugin_function(self):
        zh = ZeroHidePlugin()
        zh.following_zeros = 3
        self.form.add_signalfile("./data/ask.complex")
        self.form.ui.tabWidget.setCurrentIndex(1)
        QTest.qWait(100)
        test_bits = "10110010010110110110110110110110110001000000"
        self.assertEqual(self.cframe.proto_analyzer.decoded_proto_bits_str[3], test_bits)

        action = zh.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack, (),
                               self.cframe.proto_analyzer, 0)
        action.trigger()
        QTest.qWait(100)
        self.assertEqual(self.cframe.proto_analyzer.decoded_proto_bits_str[3], "10110010010110110110110110110110111")

    def test_sdr_interface_plugin(self):
        si = NetworkSDRInterfacePlugin()
        test_bits = [
            "10101011111",
            "1010100011000111110001011001010101010101",
            "1101010101011000011",
            "11010101010110000110",
            "11100010101001110000",
            "111100000011011101010101010000101010101010100001010011010101010011"
        ]

        for bits in test_bits:
            byte_vals = si.bit_str_to_bytearray(bits)
            self.assertEqual(len(byte_vals), int(math.ceil(len(bits) / 8)), msg=bits)

            recalculated = si.bytearray_to_bit_str(byte_vals)

            if bits.endswith("1"):
                self.assertEqual(bits, recalculated.rstrip("0"))
            else:
                self.assertTrue(recalculated.startswith(bits))