import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock


class BlockBreakAction(QUndoCommand):
    def __init__(self, proto_analyzer: ProtocolAnalyzer, block_nr: int, pos: int):
        super().__init__()
        self.proto_analyzer = proto_analyzer
        self.block_nr = block_nr
        self.pos = pos
        self.orig_blocks, self.orig_labels = proto_analyzer.copy_data()

        self.setText("Break block behind selection")

    def redo(self):
        block = copy.deepcopy(self.proto_analyzer.blocks[self.block_nr])
        block1 = ProtocolBlock(block.plain_bits[:self.pos], 0,
                               self.proto_analyzer.bit_alignment_positions, 0, block.decoder, bit_len=block.bit_len,
                               exclude_from_decoding_labels=block.exclude_from_decoding_labels)
        block2 = ProtocolBlock(block.plain_bits[self.pos:], block.pause,
                               self.proto_analyzer.bit_alignment_positions, 0, block.decoder, bit_len=block.bit_len,
                               exclude_from_decoding_labels=block.exclude_from_decoding_labels)
        self.proto_analyzer.blocks[self.block_nr] = block1
        self.proto_analyzer.blocks.insert(self.block_nr + 1, block2)

    def undo(self):
        self.proto_analyzer.revert_to(self.orig_blocks, self.orig_labels)

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
