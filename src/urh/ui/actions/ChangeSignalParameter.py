import copy

import numpy as np
from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class ChangeSignalParameter(QUndoCommand):
    def __init__(self, signal: Signal, protocol: ProtocolAnalyzer, parameter_name: str, parameter_value):
        super().__init__()
        if not hasattr(signal, parameter_name):
            raise ValueError("signal has no attribute {}".format(parameter_name))

        self.signal = signal
        self.parameter_name = parameter_name
        self.parameter_value = parameter_value
        self.orig_value = getattr(self.signal, self.parameter_name)
        self.setText("Change {0} of {1} from {2} to {3}".format(parameter_name, signal.name, self.orig_value, parameter_value))

        self.protocol = protocol
        self.orig_blocks, self.orig_labels = protocol.copy_data()

    def redo(self):
        block_data = [(block.decoder, block.participant, block.labelset) for block in self.protocol.blocks]
        setattr(self.signal, self.parameter_name, self.parameter_value)
        # Restore block parameters
        if len(block_data) == self.protocol.num_blocks:
            for block, block_params in zip(self.protocol.blocks, block_data):
                block.decoder = block_params[0]
                block.participant = block_params[1]
                block.labelset = block_params[2]
            self.protocol.qt_signals.protocol_updated.emit()


    def undo(self):
        block_proto_update = self.signal.block_protocol_update
        self.signal.block_protocol_update = True
        setattr(self.signal, self.parameter_name, self.orig_value)
        self.signal.block_protocol_update = block_proto_update

        self.protocol.revert_to(self.orig_blocks, self.orig_labels)
        self.protocol.qt_signals.protocol_updated.emit()