import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Message import Message


class BlockBreakAction(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, block_nr: int, pos: int):
        super().__init__()
        self.proto_analyzer = proto_analyzer
        self.block_nr = block_nr
        self.pos = pos
        self.orig_blocks = copy.deepcopy(proto_analyzer.blocks)

        self.setText("Break block behind selection")

    def redo(self):
        block = copy.deepcopy(self.proto_analyzer.blocks[self.block_nr])
        block1 = Message(plain_bits=block.plain_bits[:self.pos], pause=0,
                         rssi=0, decoder=block.decoder, labelset=block.labelset,
                         bit_len=block.bit_len)
        block2 = Message(plain_bits=block.plain_bits[self.pos:], pause=block.pause,
                         rssi=0, decoder=block.decoder, labelset=block.labelset,
                         bit_len=block.bit_len)
        self.proto_analyzer.blocks[self.block_nr] = block1
        self.proto_analyzer.blocks.insert(self.block_nr + 1, block2)

    def undo(self):
        self.proto_analyzer.blocks = self.orig_blocks

    def __get_zero_seq_indexes(self, block: str, following_zeros: int):
        """
        :rtype: list[tuple of int]
        """

        result = []
        if following_zeros > len(block):
            return result

        zero_counter = 0
        for i in range(0, len(block)):
            if block[i] == "0":
                zero_counter += 1
            else:
                if zero_counter >= following_zeros:
                    result.append((i - zero_counter, i))
                zero_counter = 0

        if zero_counter >= following_zeros:
            result.append((len(block) - 1 - following_zeros, len(block) - 1))

        return result
