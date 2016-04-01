from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class InsertColumn(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer, index: int):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.index = index

        self.setText("Insert Column at {0:d}".format(self.index))

    def redo(self):
        for block in self.proto_analyzer_container.blocks:
            block.insert(self.index, False)

    def undo(self):
        for block in self.proto_analyzer_container.blocks:
            if self.index < len(block):
                del block[self.index]
            else:
                del block[-1]
