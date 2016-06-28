import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class DeleteBitsAndPauses(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, block_start: int, block_end:int,
                 start: int, end: int, view: int, decoded: bool, subprotos=None):
        super().__init__()

        self.subprotos = [] if subprotos is None else subprotos
        self.view = view
        self.end = end
        self.start = start
        self.block_end = block_end
        self.block_start = block_start
        self.proto_analyzer = proto_analyzer
        self.decoded = decoded
        self.orig_blocks = copy.deepcopy(self.proto_analyzer.blocks)
        self.subproto_hist = {}  # for CFC
        for subproto in self.subprotos:
            self.subproto_hist[subproto] = copy.deepcopy(subproto.blocks)


        self.setText("Delete Bits")

    def redo(self):
        self.proto_analyzer.delete_blocks(self.block_start, self.block_end, self.start, self.end, self.view, self.decoded)

    def undo(self):
        self.proto_analyzer.blocks = self.orig_blocks
        for subproto in self.subproto_hist.keys():
            subproto.blocks = self.subproto_hist[subproto]
