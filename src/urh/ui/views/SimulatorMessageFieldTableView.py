from PyQt5.QtWidgets import QTableView

from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.SimulatorScene import MessageDataItem
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate

class SimulatorMessageFieldTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(1, ComboBoxDelegate(MessageDataItem.LOG_LEVELS, parent=self))
        self.setItemDelegateForColumn(2, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))
        self.setEditTriggers(QTableView.AllEditTriggers)

    def model(self) -> SimulatorMessageFieldModel:
        return super().model()