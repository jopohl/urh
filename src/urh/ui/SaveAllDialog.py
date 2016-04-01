from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox


class SaveAllDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Saving All Signals")

        l = QVBoxLayout(self)
        l.addWidget(QLabel("All changed signal files will be overwritten. OK?", self))

        self.dontShowCBox = QCheckBox("Don't ask me again.")
        l.addWidget(self.dontShowCBox)

        l.addWidget(QDialogButtonBox(
            QDialogButtonBox.Yes | QDialogButtonBox.No,
            parent=self,
            accepted=self.accept,
            rejected=self.reject))

    @staticmethod
    def dialog(parent):
        d = SaveAllDialog(parent)
        return bool(d.exec_()), d.dontShowCBox.isChecked()
