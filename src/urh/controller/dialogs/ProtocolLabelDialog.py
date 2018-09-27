from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QDialog, QHeaderView, QAbstractItemView

from urh import constants
from urh.controller.widgets.ChecksumWidget import ChecksumWidget
from urh.models.PLabelTableModel import PLabelTableModel
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.ui.delegates.CheckBoxDelegate import CheckBoxDelegate
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate
from urh.ui.ui_properties_dialog import Ui_DialogLabels
from urh.util import util
from urh.util.Logger import logger


class ProtocolLabelDialog(QDialog):
    apply_decoding_changed = pyqtSignal(ProtocolLabel, MessageType)

    SPECIAL_CONFIG_TYPES = [FieldType.Function.CHECKSUM]

    def __init__(self, message: Message, viewtype: int, selected_index=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogLabels()
        self.ui.setupUi(self)
        util.set_splitter_stylesheet(self.ui.splitter)

        field_types = FieldType.load_from_xml()
        self.model = PLabelTableModel(message, field_types)

        self.ui.tblViewProtoLabels.setItemDelegateForColumn(0, ComboBoxDelegate([ft.caption for ft in field_types],
                                                                                is_editable=True,
                                                                                return_index=False, parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(1, SpinBoxDelegate(1, len(message), self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(2, SpinBoxDelegate(1, len(message), self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(3,
                                                            ComboBoxDelegate([""] * len(constants.LABEL_COLORS),
                                                                             colors=constants.LABEL_COLORS,
                                                                             parent=self))
        self.ui.tblViewProtoLabels.setItemDelegateForColumn(4, CheckBoxDelegate(self))
        self.ui.tblViewProtoLabels.setModel(self.model)
        self.ui.tblViewProtoLabels.setEditTriggers(QAbstractItemView.AllEditTriggers)

        self.ui.tblViewProtoLabels.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.tblViewProtoLabels.resizeColumnsToContents()
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle(self.tr("Edit Protocol Labels from message type %s") % message.message_type.name)

        self.configure_special_config_tabs()
        self.ui.splitter.setSizes([self.height() / 2, self.height() / 2])

        self.create_connects()

        if selected_index is not None:
            self.ui.tblViewProtoLabels.setCurrentIndex(self.model.index(selected_index, 0))

        self.ui.cbProtoView.setCurrentIndex(viewtype)
        self.setAttribute(Qt.WA_DeleteOnClose)

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

        for i in range(self.model.rowCount()):
            self.open_editors(i)

    def configure_special_config_tabs(self):
        self.ui.tabWidgetAdvancedSettings.clear()
        for lbl in self.model.message_type:  # type: ProtocolLabel
            if isinstance(lbl, SimulatorProtocolLabel):
                lbl = lbl.label

            if lbl.field_type is not None and lbl.field_type.function in self.SPECIAL_CONFIG_TYPES:
                if isinstance(lbl, ChecksumLabel):
                    w = ChecksumWidget(lbl, self.model.message, self.model.proto_view)
                    self.ui.tabWidgetAdvancedSettings.addTab(w, lbl.name)
                else:
                    logger.error("No Special Config Dialog for field type " + lbl.field_type.caption)

        if self.ui.tabWidgetAdvancedSettings.count() > 0:
            self.ui.tabWidgetAdvancedSettings.setCurrentIndex(0)
            self.ui.tabWidgetAdvancedSettings.setFocus()

        self.ui.groupBoxAdvancedSettings.setVisible(self.ui.tabWidgetAdvancedSettings.count() > 0)

    def create_connects(self):
        self.ui.btnConfirm.clicked.connect(self.confirm)
        self.ui.cbProtoView.currentIndexChanged.connect(self.set_view_index)
        self.model.apply_decoding_changed.connect(self.on_apply_decoding_changed)
        self.model.special_status_label_changed.connect(self.on_label_special_status_changed)

    def open_editors(self, row):
        self.ui.tblViewProtoLabels.openPersistentEditor(self.model.index(row, 4))

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Enter:
            event.ignore()
        else:
            event.accept()

    def closeEvent(self, event: QCloseEvent):
        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    @pyqtSlot()
    def confirm(self):
        self.close()

    @pyqtSlot(int)
    def set_view_index(self, ind):
        self.model.proto_view = ind
        self.model.update()

        for i in range(self.ui.tabWidgetAdvancedSettings.count()):
            self.ui.tabWidgetAdvancedSettings.widget(i).proto_view = ind

    @pyqtSlot(ProtocolLabel)
    def on_apply_decoding_changed(self, lbl: ProtocolLabel):
        self.apply_decoding_changed.emit(lbl, self.model.message_type)

    @pyqtSlot(ProtocolLabel)
    def on_label_special_status_changed(self, lbl: ProtocolLabel):
        self.configure_special_config_tabs()
