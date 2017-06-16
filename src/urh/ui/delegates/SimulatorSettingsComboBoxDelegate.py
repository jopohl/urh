from PyQt5.QtWidgets import QItemDelegate, QStyle, QStyleOptionViewItem, QComboBox, QWidget
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel, pyqtSlot

from urh.controller.SendRecvSettingsDialogController import SendRecvSettingsDialogController

from urh.dev import config

class SimulatorSettingsComboBoxDelegate(QItemDelegate):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.project_manager = controller.project_manager
        self.compare_frame_controller = controller.compare_frame_controller
        self.editor = None
        
    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        self.editor = QComboBox(parent)
        self.load_combobox()

        self.editor.activated.connect(self.combobox_activated)
        return self.editor

    def load_combobox(self):
        self.editor.blockSignals(True)
        self.editor.clear()

        for profile in config.profiles:
            self.editor.addItem(profile["name"])

        self.editor.addItem("...")
        self.editor.blockSignals(False)

    def setEditorData(self, editor: QWidget, index: QModelIndex):
        self.editor.blockSignals(True)
        indx = index.model().data(index, Qt.EditRole)
        self.editor.setCurrentIndex(indx)
        self.editor.blockSignals(False)

    def setModelData(self, editor: QWidget, model: QAbstractItemModel, index: QModelIndex):
        model.setData(index, editor.currentIndex(), Qt.EditRole)

    def dialog_finished(self):
        self.load_combobox()
        self.editor.setCurrentIndex(self.sender().ui.comboBoxProfiles.currentIndex())
        self.commitData.emit(self.editor)

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
                            parent=self.editor)

            dialog.finished.connect(self.dialog_finished)
            dialog.show()