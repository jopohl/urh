from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.AdvancedModulationOptionsDialog import AdvancedModulationOptionsDialog


class TestAdvancedModulationSettings(QtTestCase):
    def test_pause_threshold(self):
        self.add_signal_to_form("enocean.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        self.assertGreater(signal_frame.proto_analyzer.num_messages, 1)
        self.__make_setting(signal_frame, pause_threshold=0)
        self.assertEqual(signal_frame.proto_analyzer.num_messages, 1)

    def test_message_length_divisor(self):
        self.add_signal_to_form("pwm.coco")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        protocol = signal_frame.proto_analyzer

        bits = "1000100010001110100011101000111010001000100011101000111010001110100011101000111010001110111011101"
        pauses = [77118, 77117, 58218]
        for i in range(3):
            self.assertEqual(protocol.plain_bits_str[i], bits, msg=str(i))
            self.assertEqual(protocol.messages[i].pause, pauses[i], msg=str(i))

        self.__make_setting(signal_frame, message_divisor_length=4)
        self.assertEqual(signal_frame.signal.message_length_divisor, 4)
        for i in range(3):
            self.assertEqual(protocol.plain_bits_str[i], bits + "000", msg=str(i))
            self.assertEqual(protocol.messages[i].pause, pauses[i] - 3 * signal_frame.signal.bit_len, msg=str(i))

    def __make_setting(self, signal_frame, pause_threshold=None, message_divisor_length=None):
        def accept_dialog():
            for widget in QApplication.instance().topLevelWidgets():
                if isinstance(widget, AdvancedModulationOptionsDialog):
                    if pause_threshold is not None:
                        widget.ui.spinBoxPauseThreshold.setValue(pause_threshold)
                    if message_divisor_length is not None:
                        widget.ui.spinBoxMessageLengthDivisor.setValue(message_divisor_length)
                    widget.ui.buttonBox.accepted.emit()
                    return

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(accept_dialog)
        timer.setInterval(10)
        timer.start()

        signal_frame.ui.btnAdvancedModulationSettings.click()
