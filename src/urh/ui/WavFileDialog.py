from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QCheckBox, QDialogButtonBox


class WavFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wav-File selected")

        l = QVBoxLayout(self)
        msg = self.tr("You selected a .wav file as signal.\n"
                      "Universal Radio Hacker (URH) will interpret it as real part of the signal.\n"
                      "Protocol results may be bad due to missing imaginary part.\n\n"
                      "Load a complex file if you experience problems.\n"
                      "You have been warned.")

        l.addWidget(QLabel(msg, self))

        self.alrdyDemod = QCheckBox("Signal in File is already quadrature demodulated")
        l.addWidget(self.alrdyDemod)

        l.addWidget(QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Abort, parent=self,
                                     accepted=self.accept, rejected=self.reject))

    @staticmethod
    def dialog(parent):
        d = WavFileDialog(parent)
        return d.exec_(), d.alrdyDemod.isChecked()
