from PyQt5.QtWidgets import QWidget
from urh.ui.ui_send_recv_device_settings import Ui_FormDeviceSettings
from urh.util.ProjectManager import ProjectManager


class DeviceSettingsWidgetController(QWidget):
    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.ui = Ui_FormDeviceSettings()
        self.ui.setupUi(self)


