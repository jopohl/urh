from PyQt5.QtWidgets import QItemDelegate, QStyle, QStyleOptionViewItem, QComboBox, QWidget
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, pyqtSlot

from urh.controller.SendRecvSettingsDialogController import SendRecvSettingsDialogController
from urh.dev.BackendHandler import BackendHandler

from urh import SimulatorSettings

class SimulatorSettingsComboBoxDelegate(QItemDelegate):
    def __init__(self, controller, is_rx=True, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.generator_tab_controller = controller.generator_tab_controller
        self.project_manager = controller.project_manager
        self.compare_frame_controller = controller.compare_frame_controller
        self.editor = None
        self.is_rx = is_rx
        self.backend_handler = BackendHandler()

    @property
    def is_tx(self):
        return not self.is_rx

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        self.editor = QComboBox(parent)
        self.load_combobox()

        self.editor.activated.connect(self.combobox_activated)
        return self.editor

    def load_combobox(self):
        self.editor.blockSignals(True)
        self.editor.clear()

        for profile in SimulatorSettings.profiles:
            if self.is_rx and profile['supports_rx']:
                self.editor.addItem(profile['name'], profile)

            if self.is_tx and profile['supports_tx']:
                self.editor.addItem(profile['name'], profile)

        self.editor.addItem("...")
        self.editor.blockSignals(False)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        self.editor.blockSignals(True)
        item = index.model().data(index, Qt.EditRole)
        self.editor.setCurrentIndex(self.find_index(item))
        self.editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.itemData(editor.currentIndex()), Qt.EditRole)

    def dialog_finished(self):
        self.load_combobox()
        selected_profile = SimulatorSettings.profiles[self.sender().ui.comboBoxProfiles.currentIndex()]
        self.editor.setCurrentIndex(self.find_index(selected_profile))
        self.commitData.emit(self.editor)

    def find_index(self, profile):
        indx = self.editor.findData(profile)
        return self.editor.count() - 1 if indx == -1 else indx

    @pyqtSlot(int)
    def combobox_activated(self, index: int):
        if index == -1:
            return

        pm = self.project_manager

        if index == self.editor.count() - 1:
            signal = None
            for proto in self.compare_frame_controller.protocol_list:
                signal = proto.signal
                if signal:
                    break

            if signal:
                bit_len = signal.bit_len
                mod_type = signal.modulation_type
                tolerance = signal.tolerance
                noise = signal.noise_threshold
                center = signal.qad_center
            else:
                bit_len = 100
                mod_type = 1
                tolerance = 5
                noise = 0.001
                center = 0.02

            dialog = SendRecvSettingsDialogController(pm, noise, center, bit_len, tolerance, mod_type,
                                                      self.generator_tab_controller, parent=self.editor)

            dialog.finished.connect(self.dialog_finished)
            dialog.show()