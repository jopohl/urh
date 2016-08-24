import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class DeleteBitsAndPauses(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, start_message: int, end_message:int,
                 start: int, end: int, view: int, decoded: bool, subprotos=None):
        super().__init__()

        self.subprotos = [] if subprotos is None else subprotos
        """:type: list of ProtocolAnalyzer """
        self.view = view
        self.end = end
        self.start = start
        self.end_message = end_message
        self.start_message = start_message
        self.proto_analyzer = proto_analyzer
        self.decoded = decoded
        self.orig_messages = copy.deepcopy(self.proto_analyzer.messages)
        self.subproto_hist = {}  # for CFC
        for subproto in self.subprotos:
            self.subproto_hist[subproto] = copy.deepcopy(subproto.messages)


        self.setText("Delete Bits")

    def redo(self):
        self.proto_analyzer.delete_messages(self.start_message, self.end_message, self.start, self.end, self.view, self.decoded)

    def undo(self):
        self.proto_analyzer.messages = self.orig_messages
        for subproto in self.subproto_hist.keys():
            subproto.messages = self.subproto_hist[subproto]
