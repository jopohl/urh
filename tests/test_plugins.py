import math
import unittest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh.controller.MainController import MainController
from urh.plugins.MessageBreak.MessageBreakPlugin import MessageBreakPlugin
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.ZeroHide.ZeroHidePlugin import ZeroHidePlugin
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
from urh.util.Formatter import Formatter
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestPlugins(unittest.TestCase):
    def setUp(self):
        logger.debug("Init form")
        self.form = MainController()
        logger.debug("Initalized form")
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

        self.signal = self.sframe.signal

    def tearDown(self):
        self.signal = None
        self.form.close_all()
        tests.utils_testing.short_wait()

    def test_message_break_plugin(self):
        bp = MessageBreakPlugin()
        action = bp.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack,
                               (1, 1, 4, 4), self.cframe.proto_analyzer, 0)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)
        action.trigger()
        self.assertEqual(self.cframe.protocol_model.row_count, 4)

        self.cframe.protocol_undo_stack.undo()
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

    def test_zero_hide_plugin_gui(self):
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377)
        zh = ZeroHidePlugin()
        zh.following_zeros = 188
        action = zh.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack, (),
                               self.cframe.proto_analyzer, 0)
        action.trigger()
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377 - 188)

        self.cframe.protocol_undo_stack.undo()
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 377)

    def test_zero_hide_plugin_function(self):
        zh = ZeroHidePlugin()
        zh.following_zeros = 3
        self.form.add_signalfile(get_path_for_data_file("ask.complex"))
        self.form.ui.tabWidget.setCurrentIndex(1)
        test_bits = "10110010010110110110110110110110110001000000"
        self.assertEqual(self.cframe.proto_analyzer.decoded_proto_bits_str[3], test_bits)

        action = zh.get_action(self.cframe.ui.tblViewProtocol, self.cframe.protocol_undo_stack, (),
                               self.cframe.proto_analyzer, 0)
        action.trigger()
        self.assertEqual(self.cframe.proto_analyzer.decoded_proto_bits_str[3], "10110010010110110110110110110110111")

    def test_sdr_interface_plugin(self):
        si = NetworkSDRInterfacePlugin()
        test_bits = [
            "10101011111",
            "1010100011000111110001011001010101010101",
            "1010100011000111110001011001010100100",
            "1101010101011000011",
            "11010101010110000110",
            "11100010101001110000",
            "111100000011011101010101010000101010101010100001010011010101010011"
        ]

        for bits in test_bits:
            byte_vals = si.bit_str_to_bytearray(bits)
            self.assertEqual(len(byte_vals), int(math.ceil(len(bits) / 8)), msg=bits)

            recalculated = si.bytearray_to_bit_str(byte_vals)

            if len(bits) % 8 == 0:
                self.assertEqual(bits, recalculated)
            elif bits.endswith("1"):
                self.assertEqual(bits, recalculated.rstrip("0"))
            else:
                self.assertTrue(recalculated.startswith(bits))

    def test_insert_sine_plugin(self):
        insert_sine_plugin = self.sframe.ui.gvSignal.insert_sine_plugin
        num_samples = 10000
        dialog = insert_sine_plugin.get_insert_sine_dialog(original_data=self.signal.data,
                                                           position=2000,
                                                           sample_rate=self.signal.sample_rate,
                                                           num_samples=num_samples)

        graphics_view = dialog.graphicsViewSineWave  # type: ZoomableGraphicView

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        self.assertEqual(int(graphics_view.sceneRect().width()), self.signal.num_samples + num_samples)
        self.assertEqual(insert_sine_plugin.insert_indicator.rect().width(), num_samples)
        self.assertEqual(insert_sine_plugin.insert_indicator.rect().x(), 2000)

        dialog.doubleSpinBoxAmplitude.setValue(0.1)
        dialog.doubleSpinBoxAmplitude.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.amplitude, 0.1)

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        dialog.doubleSpinBoxFrequency.setValue(1e6)
        dialog.doubleSpinBoxFrequency.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.frequency, 1e6)

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        dialog.doubleSpinBoxPhase.setValue(100)
        dialog.doubleSpinBoxPhase.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.phase, 100)

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        dialog.doubleSpinBoxSampleRate.setValue(2e6)
        dialog.doubleSpinBoxSampleRate.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.sample_rate, 2e6)

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        dialog.doubleSpinBoxNSamples.setValue(0.5e6)
        dialog.doubleSpinBoxNSamples.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.num_samples, 0.5e6)

        while not dialog.doubleSpinBoxAmplitude.isEnabled():
            tests.utils_testing.short_wait(10)

        sep = Formatter.local_decimal_seperator()
        self.assertEqual(dialog.lineEditTime.text(), "250" + sep + "000m")
