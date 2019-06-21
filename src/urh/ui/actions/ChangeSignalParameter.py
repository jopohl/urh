import copy

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

        fmt2 = "d" if isinstance(self.orig_value, int) else ".4n" if isinstance(self.orig_value, float) else "s"
        fmt3 = "d" if isinstance(parameter_value, int) else ".4n" if isinstance(parameter_value, float) else "s"
        signal_name = signal.name[:10] + "..." if len(signal.name) > 10 else signal.name

        self.setText(
            ("change {0} of {1} from {2:" + fmt2 + "} to {3:" + fmt3 + "}")
                .format(parameter_name, signal_name, self.orig_value, parameter_value)
        )

        self.protocol = protocol
        self.orig_messages = copy.deepcopy(self.protocol.messages)

    def redo(self):
        msg_data = [(msg.decoder, msg.participant, msg.message_type) for msg in self.protocol.messages]
        setattr(self.signal, self.parameter_name, self.parameter_value)
        # Restore msg parameters
        if len(msg_data) == self.protocol.num_messages:
            for msg, msg_params in zip(self.protocol.messages, msg_data):
                msg.decoder = msg_params[0]
                msg.participant = msg_params[1]
                msg.message_type = msg_params[2]
            self.protocol.qt_signals.protocol_updated.emit()

    def undo(self):
        block_proto_update = self.signal.block_protocol_update
        self.signal.block_protocol_update = True
        setattr(self.signal, self.parameter_name, self.orig_value)
        self.signal.block_protocol_update = block_proto_update

        self.protocol.messages = self.orig_messages
        self.protocol.qt_signals.protocol_updated.emit()
