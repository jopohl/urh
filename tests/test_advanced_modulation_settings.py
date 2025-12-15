from tests.QtTestCase import QtTestCase
from urh.controller.MainController import MainController
from urh.controller.widgets.SignalFrame import SignalFrame


class TestAdvancedModulationSettings(QtTestCase):
    def test_pause_threshold(self):
        self.add_signal_to_form("enocean.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        self.assertGreater(signal_frame.proto_analyzer.num_messages, 1)

        dialog = signal_frame.get_advanced_modulation_settings_dialog()
        dialog.ui.spinBoxPauseThreshold.setValue(0)
        dialog.on_accept_clicked()

        self.assertEqual(signal_frame.proto_analyzer.num_messages, 1)

    def test_message_length_divisor(self):
        assert isinstance(self.form, MainController)
        self.form.ui.actionAuto_detect_new_signals.setChecked(False)
        self.add_signal_to_form("pwm.complex16s")
        signal_frame = self.form.signal_tab_controller.signal_frames[
            0
        ]  # type: SignalFrame
        signal_frame.ui.spinBoxNoiseTreshold.setValue(0.0525)
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        signal_frame.ui.spinBoxCenterOffset.setValue(0.01807)
        signal_frame.ui.spinBoxCenterOffset.editingFinished.emit()
        signal_frame.ui.spinBoxSamplesPerSymbol.setValue(2900)
        signal_frame.ui.spinBoxSamplesPerSymbol.editingFinished.emit()
        signal_frame.ui.spinBoxTolerance.setValue(2)
        signal_frame.ui.spinBoxTolerance.editingFinished.emit()

        protocol = signal_frame.proto_analyzer

        bits = "1000100010001110100011101000111010001000100011101000111010001110100011101000111010001110111011101"
        pauses = [77114, 77112, 58220]
        for i in range(3):
            self.assertEqual(protocol.plain_bits_str[i], bits, msg=str(i))
            self.assertEqual(protocol.messages[i].pause, pauses[i], msg=str(i))

        dialog = signal_frame.get_advanced_modulation_settings_dialog()
        dialog.ui.spinBoxMessageLengthDivisor.setValue(4)
        dialog.on_accept_clicked()
        self.assertEqual(signal_frame.signal.message_length_divisor, 4)
        for i in range(3):
            self.assertEqual(protocol.plain_bits_str[i], bits + "000", msg=str(i))
            self.assertEqual(
                protocol.messages[i].pause,
                pauses[i] - 3 * signal_frame.signal.samples_per_symbol,
                msg=str(i),
            )
