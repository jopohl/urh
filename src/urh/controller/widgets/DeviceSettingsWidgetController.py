from PyQt5.QtWidgets import QWidget
from urh.ui.ui_send_recv_device_settings import Ui_FormDeviceSettings


class DeviceSettingsWidgetController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_FormDeviceSettings()
        self.ui.setupUi(self)
