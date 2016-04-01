from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QLineEdit, QCheckBox


class CustomDialog(QDialog):
    def __init__(self, parent=None, txt="", type="ok"):
        super().__init__(parent)
        self.setWindowTitle("Confirm Dialog")
        self.returnInfo = ""

        l = QVBoxLayout(self)

        if "ok" in type:
            l.addWidget(QLabel(txt, self))
            l.addWidget(QDialogButtonBox(QDialogButtonBox.Ok, parent=self, accepted=self.accept, rejected=self.reject))

        elif "yesno" in type:
            l.addWidget(QLabel(txt, self))
            l.addWidget(QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No, parent=self, accepted=self.accept, rejected=self.reject))

        elif "input" in type:
            l.addWidget(QLabel(txt[0], self))
            l.addWidget(QLineEdit(txt[1], parent=self, textChanged=self.input_changed))
            l.addWidget(QDialogButtonBox(QDialogButtonBox.Ok, parent=self, accepted=self.accept, rejected=self.reject))
            self.returnInfo = txt[1]

        elif "close" in type:
            l.addWidget(QLabel(txt, self))
            self.CB = QCheckBox("Don't ask me again.", stateChanged=self.checkbox_changed)
            l.addWidget(self.CB)
            l.addWidget(QDialogButtonBox(
                QDialogButtonBox.Yes | QDialogButtonBox.No,
                parent=self,
                accepted=self.accept,
                rejected=self.reject))


    def input_changed(self, text):
        self.returnInfo = text


    def checkbox_changed(self):
        self.returnInfo = self.CB.isChecked()


    @staticmethod
    def dialog(parent, txt, type):
        d = CustomDialog(parent, txt, type)
        return bool(d.exec_()), d.returnInfo
