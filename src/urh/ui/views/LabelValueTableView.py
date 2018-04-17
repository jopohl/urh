from collections import OrderedDict

from PyQt5.QtWidgets import QTableView

from urh.models.LabelValueTableModel import LabelValueTableModel
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.delegates.SectionComboBoxDelegate import SectionComboBoxDelegate


class LabelValueTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemDelegateForColumn(1, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))

        orders = OrderedDict([("Big Endian (BE)", [bo + " (BE)" for bo in ProtocolLabel.DISPLAY_BIT_ORDERS]),
                              ("Little Endian (LE)", [bo + " (LE)" for bo in ProtocolLabel.DISPLAY_BIT_ORDERS])])

        self.setItemDelegateForColumn(2, SectionComboBoxDelegate(orders, parent=self))
        self.setEditTriggers(QTableView.AllEditTriggers)

    def model(self) -> LabelValueTableModel:
        return super().model()
