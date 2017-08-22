from PyQt5.QtWidgets import QDialog, QLabel

from urh.signalprocessing.Filter import Filter
from urh.ui.ui_filter_bandwidth_dialog import Ui_DialogFilterBandwidth

class FilterBandwidthDialogController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_DialogFilterBandwidth()
        self.ui.setupUi(self)

        for item in dir(self.ui):
            label = getattr(self.ui, item)
            if isinstance(label, QLabel):
                name = label.objectName().replace("label", "")
                key = next((key for key in Filter.BANDWIDTHS.keys() if name.startswith(key.replace(" ", ""))), None)
                if key is not None and name.endswith("Bandwidth"):
                    label.setText("{0:n}".format(Filter.BANDWIDTHS[key]))
                elif key is not None and name.endswith("KernelLength"):
                    label.setText(str(Filter.filter_length_from_bandwidth(Filter.BANDWIDTHS[key])))

        self.create_connects()

    def create_connects(self):
        pass
