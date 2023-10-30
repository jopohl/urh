import math

from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.CompareFrameController import CompareFrameController
from urh.plugins.MessageBreak.MessageBreakPlugin import MessageBreakPlugin
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import (
    NetworkSDRInterfacePlugin,
)
from urh.plugins.ZeroHide.ZeroHidePlugin import ZeroHidePlugin
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView
from urh.util.Formatter import Formatter


class TestPlugins(QtTestCase):
    def setUp(self):
        super().setUp()
        self.add_signal_to_form("esaver.complex16s")
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.setValue(0.3692)
        self.form.signal_tab_controller.signal_frames[
            0
        ].ui.spinBoxCenterOffset.editingFinished.emit()

        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.cframe = self.form.compare_frame_controller  # type: CompareFrameController
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

    def test_message_break_plugin(self):
        bp = MessageBreakPlugin()

        n = 1
        action = bp.get_action(
            self.cframe.ui.tblViewProtocol,
            self.cframe.protocol_undo_stack,
            (n, n, 4, 4),
            self.cframe.proto_analyzer,
            0,
        )
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

        original_msg = self.cframe.proto_analyzer.messages[n]
        original_msg.message_type = MessageType(
            "Test", [ProtocolLabel("Test Label", 2, 42, 0)]
        )
        msg_type = original_msg.message_type
        old_msg_len = len(original_msg)

        action.trigger()

        # Now we have two messages: One before and including selection and one behind selection
        msg_1 = self.cframe.proto_analyzer.messages[n]
        msg_2 = self.cframe.proto_analyzer.messages[n + 1]

        self.assertEqual(len(msg_1), 4)
        self.assertEqual(len(msg_2), old_msg_len - 4)
        self.assertEqual(msg_type, msg_1.message_type)
        self.assertEqual(msg_type, msg_2.message_type)

        self.assertEqual(self.cframe.protocol_model.row_count, 4)
        self.cframe.protocol_undo_stack.undo()
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

    def test_zero_hide_plugin_gui(self):
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 331)
        zh = ZeroHidePlugin()
        zh.following_zeros = 158
        action = zh.get_action(
            self.cframe.ui.tblViewProtocol,
            self.cframe.protocol_undo_stack,
            (),
            self.cframe.proto_analyzer,
            0,
        )
        action.trigger()

        self.assertEqual(
            len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 331 - 158
        )

        self.cframe.protocol_undo_stack.undo()
        self.assertEqual(len(self.cframe.proto_analyzer.decoded_proto_bits_str[0]), 331)

    def test_zero_hide_plugin_function(self):
        zh = ZeroHidePlugin()
        zh.following_zeros = 3
        self.add_signal_to_form("ask.complex")
        self.form.signal_tab_controller.signal_frames[
            1
        ].ui.cbModulationType.setCurrentText("ASK")

        self.form.signal_tab_controller.signal_frames[
            1
        ].ui.spinBoxCenterOffset.setValue(-0.3938)
        self.form.signal_tab_controller.signal_frames[
            1
        ].ui.spinBoxCenterOffset.editingFinished.emit()

        self.form.signal_tab_controller.signal_frames[
            1
        ].ui.spinBoxSamplesPerSymbol.setValue(300)
        self.form.signal_tab_controller.signal_frames[
            1
        ].ui.spinBoxSamplesPerSymbol.editingFinished.emit()

        self.form.ui.tabWidget.setCurrentIndex(1)
        test_bits = "1011001001011011011011011011011011001000000"
        self.assertEqual(
            self.cframe.proto_analyzer.decoded_proto_bits_str[3], test_bits
        )

        action = zh.get_action(
            self.cframe.ui.tblViewProtocol,
            self.cframe.protocol_undo_stack,
            (),
            self.cframe.proto_analyzer,
            0,
        )
        action.trigger()
        self.assertEqual(
            self.cframe.proto_analyzer.decoded_proto_bits_str[3],
            "1011001001011011011011011011011011001",
        )

    def test_sdr_interface_plugin(self):
        si = NetworkSDRInterfacePlugin(resume_on_full_receive_buffer=True)
        test_bits = [
            "10101011111",
            "1010100011000111110001011001010101010101",
            "1010100011000111110001011001010100100",
            "1101010101011000011",
            "11010101010110000110",
            "11100010101001110000",
            "111100000011011101010101010000101010101010100001010011010101010011",
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

    def __wait_for_spinbox_enabled(self, dialog):
        n = 0
        while not dialog.doubleSpinBoxAmplitude.isEnabled() and n < 50:
            QApplication.instance().processEvents()
            QTest.qWait(10)
            n += 1
        self.assertTrue(dialog.doubleSpinBoxAmplitude.isEnabled())

    def test_insert_sine_plugin(self):
        insert_sine_plugin = self.sframe.ui.gvSignal.insert_sine_plugin
        num_samples = 10000
        dialog = insert_sine_plugin.get_insert_sine_dialog(
            original_data=self.sframe.signal.iq_array.data,
            position=2000,
            sample_rate=self.sframe.signal.sample_rate,
            num_samples=num_samples,
        )

        graphics_view = dialog.graphicsViewSineWave  # type: ZoomableGraphicView

        self.__wait_for_spinbox_enabled(dialog)

        self.assertEqual(
            int(graphics_view.sceneRect().width()),
            self.sframe.signal.num_samples + num_samples,
        )
        self.assertEqual(
            insert_sine_plugin.insert_indicator.rect().width(), num_samples
        )
        self.assertEqual(insert_sine_plugin.insert_indicator.rect().x(), 2000)

        dialog.doubleSpinBoxAmplitude.setValue(0.1)
        dialog.doubleSpinBoxAmplitude.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.amplitude, 0.1)

        self.__wait_for_spinbox_enabled(dialog)

        dialog.doubleSpinBoxFrequency.setValue(1e6)
        dialog.doubleSpinBoxFrequency.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.frequency, 1e6)

        self.__wait_for_spinbox_enabled(dialog)

        dialog.doubleSpinBoxPhase.setValue(100)
        dialog.doubleSpinBoxPhase.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.phase, 100)

        self.__wait_for_spinbox_enabled(dialog)

        dialog.doubleSpinBoxSampleRate.setValue(2e6)
        dialog.doubleSpinBoxSampleRate.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.sample_rate, 2e6)

        self.__wait_for_spinbox_enabled(dialog)

        dialog.doubleSpinBoxNSamples.setValue(0.5e6)
        dialog.doubleSpinBoxNSamples.editingFinished.emit()
        self.assertEqual(insert_sine_plugin.num_samples, 0.5e6)

        self.__wait_for_spinbox_enabled(dialog)

        sep = Formatter.local_decimal_seperator()
        self.assertEqual(dialog.lineEditTime.text(), "250" + sep + "000m")

        dialog.close()
