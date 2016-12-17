from PyQt5.QtWidgets import QTableView

from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate


class LabelValueTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(1, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))
        self.setEditTriggers(QTableView.AllEditTriggers)

    def model(self) -> LabelValueTableModel:
        return super().model()
