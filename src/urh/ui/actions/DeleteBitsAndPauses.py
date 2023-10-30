import copy

from PyQt5.QtWidgets import QUndoCommand

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class DeleteBitsAndPauses(QUndoCommand):
    def __init__(
        self,
        proto_analyzer: ProtocolAnalyzer,
        start_message: int,
        end_message: int,
        start: int,
        end: int,
        view: int,
        decoded: bool,
        subprotos=None,
        update_label_ranges=True,
    ):
        super().__init__()

        self.sub_protocols = (
            [] if subprotos is None else subprotos
        )  # type: list[ProtocolAnalyzer]
        self.view = view
        self.end = end
        self.start = start
        self.end_message = end_message
        self.start_message = start_message
        self.proto_analyzer = proto_analyzer
        self.decoded = decoded
        self.saved_messages = []
        self.removed_message_indices = []
        self.sub_protocol_history = {}  # for CFC
        self.update_label_ranges = update_label_ranges
        for sub_protocol in self.sub_protocols:
            self.sub_protocol_history[sub_protocol] = sub_protocol.messages

        self.setText("Delete")

    def redo(self):
        self.saved_messages = copy.deepcopy(
            self.proto_analyzer.messages[self.start_message : self.end_message + 1]
        )
        self.removed_message_indices = self.proto_analyzer.delete_messages(
            self.start_message,
            self.end_message,
            self.start,
            self.end,
            self.view,
            self.decoded,
            self.update_label_ranges,
        )

    def undo(self):
        for i in reversed(range(self.start_message, self.end_message + 1)):
            if i in self.removed_message_indices:
                self.proto_analyzer.messages.insert(
                    i, self.saved_messages[i - self.start_message]
                )
            else:
                try:
                    self.proto_analyzer.messages[i] = self.saved_messages[
                        i - self.start_message
                    ]
                except IndexError:
                    self.proto_analyzer.messages.append(
                        self.saved_messages[i - self.start_message]
                    )

        for sub_protocol in self.sub_protocol_history.keys():
            sub_protocol.messages = self.sub_protocol_history[sub_protocol]

        self.saved_messages.clear()
        self.removed_message_indices.clear()
