import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class InsertBitsAndPauses(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, index: int, pa: ProtocolAnalyzer):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.proto_analyzer = pa
        self.index = index
        if self.index == -1 or self.index > len(self.proto_analyzer_container.messages):
            self.index = len(self.proto_analyzer_container.messages)

        self.setText("Insert data at index {0:d}".format(self.index))
        self.num_messages = 0

    def redo(self):
        self.proto_analyzer_container.insert_protocol_analyzer(self.index, self.proto_analyzer)
        self.num_messages += len(self.proto_analyzer.messages)

    def undo(self):
        for i in reversed(range(self.index, self.index+self.num_messages)):
            del self.proto_analyzer_container.messages[i]
        self.num_messages = 0
