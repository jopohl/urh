from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.MainController import MainController
from urh.controller.dialogs.AdvancedModulationOptionsDialog import AdvancedModulationOptionsDialog
from urh.controller.widgets.SignalFrame import SignalFrame


class TestAdvancedModulationSettings(QtTestCase):
    def test_pause_threshold(self):
        self.add_signal_to_form("enocean.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        self.assertGreater(signal_frame.proto_analyzer.num_messages, 1)
        self.__make_setting(signal_frame, pause_threshold=0)
        self.assertEqual(signal_frame.proto_analyzer.num_messages, 1)

    def test_message_length_divisor(self):
        assert isinstance(self.form, MainController)
        self.form.ui.actionAuto_detect_new_signals.setChecked(False)
        self.add_signal_to_form("pwm.coco")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]  # type: SignalFrame
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0.0525)
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        signal_frame.ui.spinBoxCenterOffset.setValue(0.01807)
        signal_frame.ui.spinBoxCenterOffset.editingFinished.emit()
        signal_frame.ui.spinBoxInfoLen.setValue(2900)
        signal_frame.ui.spinBoxInfoLen.editingFinished.emit()
        signal_frame.ui.spinBoxTolerance.setValue(2)
        signal_frame.ui.spinBoxTolerance.editingFinished.emit()


        protocol = signal_frame.proto_analyzer

        bits = "1000100010001110100011101000111010001000100011101000111010001110100011101000111010001110111011101"
        pauses = [77114, 77112, 58221]
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

        timer = QTimer(self.form)
        timer.setSingleShot(True)
        timer.timeout.connect(accept_dialog)
        timer.setInterval(10)
        timer.start()

        signal_frame.ui.btnAdvancedModulationSettings.click()
