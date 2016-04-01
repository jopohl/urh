import unittest
from PyQt5.QtTest import QTest

from urh import constants
from urh.controller.MainController import MainController
from urh.plugins.BlockBreak.BlockBreakPlugin import BlockBreakPlugin
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

    def test_block_break_plugin(self):
        bp = BlockBreakPlugin()
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
