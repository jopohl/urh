from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWidget, QCompleter, QDirModel

from urh import constants
from urh.dev.BackendHandler import BackendHandler
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.ui.ui_send_recv_sniff_settings import Ui_SniffSettings


class SniffSettingsWidget(QWidget):
    sniff_setting_edited = pyqtSignal()
    sniff_file_edited = pyqtSignal()

    def __init__(self, encodings, device_name: str, signal=None, encoding_index=0, backend_handler=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_SniffSettings()
        self.ui.setupUi(self)

        bit_length = signal.bit_len if signal else 100
        modulation_type_index = signal.modulation_type if signal else 1
        tolerance = signal.tolerance if signal else 5
        noise = signal.noise_threshold if signal else 0.001
        center = signal.qad_center if signal else 0.02

        self.sniffer = ProtocolSniffer(bit_len=bit_length,
                                       center=center,
                                       noise=noise,
                                       tolerance=tolerance,
                                       modulation_type=modulation_type_index,
                                       device=device_name,
                                       backend_handler=BackendHandler() if backend_handler is None else backend_handler)

        self.ui.spinbox_sniff_Noise.setValue(noise)
        self.ui.spinbox_sniff_Center.setValue(center)
        self.ui.spinbox_sniff_BitLen.setValue(bit_length)
        self.ui.spinbox_sniff_ErrorTolerance.setValue(tolerance)
        self.ui.combox_sniff_Modulation.setCurrentIndex(modulation_type_index)

        self.encodings = encodings
        for encoding in self.encodings:
            self.ui.comboBox_sniff_encoding.addItem(encoding.name)

        self.create_connects()

        if encoding_index > -1:
            self.ui.comboBox_sniff_encoding.setCurrentIndex(encoding_index)

        self.ui.comboBox_sniff_viewtype.setCurrentIndex(constants.SETTINGS.value('default_view', 0, int))

        # Auto Complete like a Boss
        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEdit_sniff_OutputFile.setCompleter(completer)

    def create_connects(self):
        self.ui.spinbox_sniff_Noise.editingFinished.connect(self.on_noise_edited)
        self.ui.spinbox_sniff_Center.editingFinished.connect(self.on_center_edited)
        self.ui.spinbox_sniff_BitLen.editingFinished.connect(self.on_bit_len_edited)
        self.ui.spinbox_sniff_ErrorTolerance.editingFinished.connect(self.on_tolerance_edited)
        self.ui.combox_sniff_Modulation.currentIndexChanged.connect(self.on_modulation_changed)
        self.ui.comboBox_sniff_viewtype.currentIndexChanged.connect(self.on_view_type_changed)
        self.ui.lineEdit_sniff_OutputFile.editingFinished.connect(self.on_line_edit_output_file_editing_finished)
        self.ui.comboBox_sniff_encoding.currentIndexChanged.connect(self.on_combobox_sniff_encoding_index_changed)

    def emit_editing_finished_signals(self):
        self.ui.spinbox_sniff_Noise.editingFinished.emit()
        self.ui.spinbox_sniff_Center.editingFinished.emit()
        self.ui.spinbox_sniff_BitLen.editingFinished.emit()
        self.ui.spinbox_sniff_ErrorTolerance.editingFinished.emit()
        self.ui.lineEdit_sniff_OutputFile.editingFinished.emit()

    @pyqtSlot()
    def on_noise_edited(self):
        self.sniffer.signal._noise_threshold = self.ui.spinbox_sniff_Noise.value()
        self.sniff_setting_edited.emit()

    @pyqtSlot()
    def on_center_edited(self):
        self.sniffer.signal.qad_center = self.ui.spinbox_sniff_Center.value()
        self.sniff_setting_edited.emit()

    @pyqtSlot()
    def on_bit_len_edited(self):
        self.sniffer.signal.bit_len = self.ui.spinbox_sniff_BitLen.value()
        self.sniff_setting_edited.emit()

    @pyqtSlot()
    def on_tolerance_edited(self):
        self.sniffer.signal.tolerance = self.ui.spinbox_sniff_ErrorTolerance.value()
        self.sniff_setting_edited.emit()

    @pyqtSlot(int)
    def on_modulation_changed(self, new_index: int):
        self.sniffer.signal.silent_set_modulation_type(new_index)
        self.sniff_setting_edited.emit()

    @pyqtSlot(int)
    def on_view_type_changed(self, new_index: int):
        self.sniff_setting_edited.emit()

    @pyqtSlot(int)
    def on_combobox_sniff_encoding_index_changed(self, index: int):
        if self.sniffer.decoder != self.encodings[index]:
            self.sniffer.set_decoder_for_messages(self.encodings[index])
            self.sniffer.decoder = self.encodings[index]
            self.sniff_setting_edited.emit()

    @pyqtSlot()
    def on_line_edit_output_file_editing_finished(self):
        text = self.ui.lineEdit_sniff_OutputFile.text()
        if text and not text.endswith(".txt"):
            text += ".txt"
            self.ui.lineEdit_sniff_OutputFile.setText(text)

        self.sniffer.sniff_file = text
        self.sniff_file_edited.emit()
