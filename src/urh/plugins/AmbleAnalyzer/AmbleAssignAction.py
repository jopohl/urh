import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class AmbleAssignAction(QUndoCommand):
    def __init__(self, amble_pattern: str, min_occurences: int, groups, labelset: LabelSet):
        """

        :type group: list of ProtocolGroup
        :return:
        """
        super().__init__()
        self.amble_pattern = amble_pattern
        self.min_occurences = min_occurences
        self.groups = groups
        self.labelset = labelset
        self.orig_labels = copy.deepcopy(labelset)
        self.setText("Auto Assign Amble Labels")

    def redo(self):
        len_pattern = len(self.amble_pattern)
        amble_sequence = self.amble_pattern * self.min_occurences
        len_sequence = len(amble_sequence)
        labels = []

        for group in self.groups:
            count = 0
            for k, block in enumerate(group.blocks):
                bit_str = block.decoded_bits_str
                len_bit_str = len(bit_str)
                indx = bit_str.find(amble_sequence)
                labels.append([])
                while indx != -1:
                    start = indx
                    end = indx + len_sequence
                    for i in range(start + len_sequence, len_bit_str, len_pattern):
                        if bit_str[i:i + len_pattern] != self.amble_pattern:
                            end = i
                            break

                    start = start if start > 1 else 0  # Erstes Bit mitnehmen, wenn Preamble beim zweiten Bit beginnt

                    if count == 0:
                        name = "Preamble"
                    else:
                        name = "Amble #{0:d}".format(count)
                    lbl = ProtocolLabel(name=name, start=start, end = end - 1, val_type_index= 0, color_index=-1)
                    lbl.apply_decoding = False
                    labels[k].append(lbl)
                    indx = bit_str.find(amble_sequence, end - 1)
                    count += 1
                    self.labelset.add_label(lbl)

    def undo(self):
        self.labelset = self.orig_labels

