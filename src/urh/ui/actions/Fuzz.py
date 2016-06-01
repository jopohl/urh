from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class Fuzz(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, fuz_mode: str):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.fuz_mode = fuz_mode

        self.setText("{0} Fuzzing".format(self.fuz_mode))
        self.orig_blocks, self.orig_labelsets = self.proto_analyzer_container.copy_data()

    def redo(self):
        if self.fuz_mode == "Successive":
            self.proto_analyzer_container.fuzz_successive()
        elif self.fuz_mode == "Concurrent":
            self.proto_analyzer_container.fuzz_concurrent()
        elif self.fuz_mode == "Exhaustive":
            self.proto_analyzer_container.fuzz_exhaustive()

    def undo(self):
        self.proto_analyzer_container.revert_to(self.orig_blocks, self.orig_labelsets)
