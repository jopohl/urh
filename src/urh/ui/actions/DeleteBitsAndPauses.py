from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class DeleteBitsAndPauses(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, block_start: int, block_end:int,
                 start: int, end: int, view: int, decoded: bool, blockranges_for_groups=None,
                 subprotos=None):
        super().__init__()

        self.subprotos = [] if subprotos is None else subprotos
        self.view = view
        self.end = end
        self.start = start
        self.block_end = block_end
        self.block_start = block_start
        self.proto_analyzer = proto_analyzer
        self.blockranges_for_groups = blockranges_for_groups
        self.decoded = decoded
        self.orig_blocks, self.orig_labelsets = self.proto_analyzer.copy_data()
        self.subproto_hist = {}  # for CFC
        for subproto in self.subprotos:
            self.subproto_hist[subproto] = subproto.copy_data()


        self.setText("Delete Bits")

    def redo(self):
        self.proto_analyzer.delete_blocks(self.block_start, self.block_end, self.start, self.end, self.view,
                                          self.decoded,
                                          self.blockranges_for_groups)

    def undo(self):
        self.proto_analyzer.revert_to(self.orig_blocks, self.orig_labelsets)
        for subproto in self.subproto_hist.keys():
            subproto.revert_to(*self.subproto_hist[subproto])
