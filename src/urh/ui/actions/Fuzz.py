import copy

from PyQt5.QtWidgets import QUndoCommand

from urh import constants
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class Fuzz(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, fuz_mode: str):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.fuz_mode = fuz_mode

        self.setText("{0} Fuzzing".format(self.fuz_mode))
        self.orig_messages = copy.deepcopy(self.proto_analyzer_container.messages)

    def redo(self):
        if constants.SETTINGS.value('use_default_fuzzing_pause', True, bool):
            default_pause = constants.SETTINGS.value("default_fuzzing_pause", 10**6, int)
        else:
            default_pause = None
        if self.fuz_mode == "Successive":
            self.proto_analyzer_container.fuzz_successive(default_pause=default_pause)
        elif self.fuz_mode == "Concurrent":
            self.proto_analyzer_container.fuzz_concurrent(default_pause=default_pause)
        elif self.fuz_mode == "Exhaustive":
            self.proto_analyzer_container.fuzz_exhaustive(default_pause=default_pause)

    def undo(self):
        self.proto_analyzer_container.messages = self.orig_messages
