from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from urh.controller.AdvancedModulationOptionsController import AdvancedModulationOptionsController


class TestAdvancedModulationSettings(QtTestCase):
    def test_pause_threshold(self):
        self.add_signal_to_form("enocean.complex")
        signal_frame = self.form.signal_tab_controller.signal_frames[0]
        signal_frame.ui.cbModulationType.setCurrentText("ASK")
        self.assertGreater(signal_frame.proto_analyzer.num_messages, 1)
        self.__make_setting(signal_frame, pause_threshold=0)
        self.assertEqual(signal_frame.proto_analyzer.num_messages, 1)

    def __make_setting(self, signal_frame, pause_threshold=None):
        def accept_dialog():
            for widget in QApplication.instance().topLevelWidgets():
                if isinstance(widget, AdvancedModulationOptionsController):
                    if pause_threshold is not None:
                        widget.ui.spinBoxPauseThreshold.setValue(pause_threshold)
                    widget.ui.buttonBox.accepted.emit()
                    return

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(accept_dialog)
        timer.setInterval(10)
        timer.start()

        signal_frame.ui.btnAdvancedModulationSettings.click()
