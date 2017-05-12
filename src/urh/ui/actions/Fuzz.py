import copy

import time
from PyQt5.QtWidgets import QUndoCommand

from urh import constants
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class Fuzz(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, fuz_mode: str):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.fuz_mode = fuz_mode

        self.setText("{0} Fuzzing".format(self.fuz_mode))
        self.added_message_indices = []

    def redo(self):
        if constants.SETTINGS.value('use_default_fuzzing_pause', True, bool):
            default_pause = constants.SETTINGS.value("default_fuzzing_pause", 10**6, int)
        else:
            default_pause = None

        if self.fuz_mode == "Successive":
            added_indices = self.proto_analyzer_container.fuzz_successive(default_pause=default_pause)
        elif self.fuz_mode == "Concurrent":
            added_indices = self.proto_analyzer_container.fuzz_concurrent(default_pause=default_pause)
        elif self.fuz_mode == "Exhaustive":
            added_indices = self.proto_analyzer_container.fuzz_exhaustive(default_pause=default_pause)
        else:
            added_indices = []

        self.added_message_indices.extend(added_indices)

    def undo(self):
        for index in reversed(self.added_message_indices):
            del self.proto_analyzer_container.messages[index]
        self.added_message_indices.clear()
