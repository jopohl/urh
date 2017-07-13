import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class InsertColumn(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, index: int, rows: list, view: int):
        super().__init__()
        self.proto_analyzer = proto_analyzer
        self.index = proto_analyzer.convert_index(index, from_view=view, to_view=0, decoded=False)[0]
        self.nbits = 1 if view == 0 else 4 if view == 1 else 8
        self.rows = rows

        self.saved_messages = {}

        self.setText("Insert column at {0:d}".format(index))

    def redo(self):
        for i in self.rows:
            msg = self.proto_analyzer.messages[i]
            self.saved_messages[i] = copy.deepcopy(msg)
            for j in range(self.nbits):
                msg.insert(self.index + j, False)

    def undo(self):
        for i in self.rows:
            self.proto_analyzer.messages[i] = self.saved_messages[i]
        self.saved_messages.clear()
