from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class InsertBitsAndPauses(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, index: int, pa: ProtocolAnalyzer):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.proto_analyzer = pa
        self.index = index
        if self.index == -1 or self.index > len(self.proto_analyzer_container.blocks):
            self.index = len(self.proto_analyzer_container.blocks)

        self.setText("Insert Bits at index {0:d}".format(self.index))
        self.orig_blocks, self.orig_labels = self.proto_analyzer_container.copy_data()

    def redo(self):
        self.proto_analyzer_container.insert_protocol_analyzer(self.index, self.proto_analyzer)

    def undo(self):
        self.proto_analyzer_container.revert_to(self.orig_blocks, self.orig_labels)
