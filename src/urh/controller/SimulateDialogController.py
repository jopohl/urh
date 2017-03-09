from PyQt5.QtWidgets import QDialog

from urh.ui.ui_simulate_dialog import Ui_SimulateDialog


class SimulateDialogController(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SimulateDialog()
        self.ui.setupUi(self)

    def create_connects(self):
        pass