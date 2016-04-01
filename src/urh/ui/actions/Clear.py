from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzerContainer import ProtocolAnalyzerContainer


class Clear(QUndoCommand):
    def __init__(self, proto_analyzer_container: ProtocolAnalyzerContainer):
        super().__init__()
        self.proto_analyzer_container = proto_analyzer_container
        self.orig_blocks, self.orig_labels = self.proto_analyzer_container.copy_data()

        self.setText("Clear Generator Table")

    def redo(self):
        self.proto_analyzer_container.clear()

    def undo(self):
        self.proto_analyzer_container.revert_to(self.orig_blocks, self.orig_labels)
