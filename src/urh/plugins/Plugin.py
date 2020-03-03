import logging
import os

from PyQt5 import uic
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QSettings
from PyQt5.QtWidgets import QUndoCommand, QUndoStack

from urh.util.Logger import logger


class Plugin(QObject):
    enabled_changed = pyqtSignal()

    def __init__(self, name: str):
        super().__init__()
        self.__enabled = Qt.Unchecked
        self.name = name
        self.plugin_path = ""
        self.description = ""
        self.__settings_frame = None
        self.qsettings = QSettings(QSettings.IniFormat, QSettings.UserScope, "urh", self.name + "-plugin")

    @property
    def settings_frame(self):
        if self.__settings_frame is None:
            logging.getLogger().setLevel(logging.WARNING)
            self.__settings_frame = uic.loadUi(os.path.join(self.plugin_path, "settings.ui"))
            logging.getLogger().setLevel(logger.level)

            self.create_connects()
        return self.__settings_frame

    @property
    def enabled(self) -> bool:
        return self.__enabled

    @enabled.setter
    def enabled(self, value: bool):
        if value != self.__enabled:
            self.__enabled = Qt.Checked if value else Qt.Unchecked
            self.enabled_changed.emit()

    def load_description(self):
        descr_file = os.path.join(self.plugin_path, "descr.txt")
        try:
            with open(descr_file, "r") as f:
                self.description = f.read()
        except Exception as e:
            print(e)

    def destroy_settings_frame(self):
        self.__settings_frame = None

    def create_connects(self):
        pass


class ProtocolPlugin(Plugin):
    def __init__(self, name: str):
        Plugin.__init__(self, name)

    def get_action(self, parent, undo_stack: QUndoStack, sel_range, groups,
                   view: int) -> QUndoCommand:
        """
        :type parent: QTableView
        :type undo_stack: QUndoStack
        :type groups: list of ProtocolGroups
        """
        raise NotImplementedError("Abstract Method.")


class SDRPlugin(Plugin):
    def __init__(self, name: str):
        Plugin.__init__(self, name)


class SignalEditorPlugin(Plugin):
    def __init__(self, name: str):
        Plugin.__init__(self, name)
