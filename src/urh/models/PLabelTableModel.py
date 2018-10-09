from PyQt5.QtCore import QAbstractTableModel, pyqtSignal, Qt, QModelIndex

from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel


class PLabelTableModel(QAbstractTableModel):
    header_labels = ["Name", "Start", "End", "Color", "Apply decoding"]

    label_removed = pyqtSignal(ProtocolLabel)
    special_status_label_changed = pyqtSignal(ProtocolLabel)
    apply_decoding_changed = pyqtSignal(ProtocolLabel)

    def __init__(self, message: Message, field_types, parent=None):
        """

        :param message:
        :type field_types: list of FieldType
        :param parent:
        """
        super().__init__(parent)
        self.row_count = len(message.message_type)
        self.proto_view = 0
        self.__message = None
        self.message = message

        self.message_type = message.message_type  # type: MessageType
        self.field_types_by_caption = {ft.caption: ft for ft in field_types}
        self.update()

    @property
    def message(self) -> Message:
        return self.__message

    @message.setter
    def message(self, value: Message):
        self.__message = value
        # Ensure bit alignment positions in message are set
        self.__message.split(decode=True)

    def __get_label_at(self, index: int) -> ProtocolLabel:
        result = self.message_type[index]
        if isinstance(result, SimulatorProtocolLabel):
            return result.label
        else:
            return result

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.message_type)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        i, j = index.row(), index.column()
        if role == Qt.DisplayRole:
            try:
                lbl = self.message_type[i]
            except IndexError:
                return False
            if j == 0:
                return lbl.name
            elif j == 1:
                return self.message.get_label_range(lbl, view=self.proto_view, decode=True)[0] + 1
            elif j == 2:
                return self.message.get_label_range(lbl, view=self.proto_view, decode=True)[1]
            elif j == 3:
                return lbl.color_index
            elif j == 4:
                return lbl.apply_decoding
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None

    def setData(self, index: QModelIndex, value, role=Qt.EditRole):
        if value == "":
            return True

        i = index.row()
        j = index.column()
        if i >= len(self.message_type):
            return False

        lbl = self.__get_label_at(i)

        if j == 0:
            lbl.name = value
            type_before = type(lbl)
            self.message_type.change_field_type_of_label(lbl, self.field_types_by_caption.get(value, None))

            lbl = self.__get_label_at(i)

            if type_before != ProtocolLabel or type(lbl) != ProtocolLabel:
                self.special_status_label_changed.emit(lbl)

        elif j == 1:
            lbl.start = self.message.convert_index(int(value - 1), from_view=self.proto_view, to_view=0, decoded=True)[
                0]
        elif j == 2:
            lbl.end = self.message.convert_index(int(value), from_view=self.proto_view, to_view=0, decoded=True)[0]
        elif j == 3:
            lbl.color_index = value
        elif j == 4:
            if bool(value) != lbl.apply_decoding:
                lbl.apply_decoding = bool(value)
                self.apply_decoding_changed.emit(lbl)

        return True

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        try:
            _ = self.message_type[index.row()]
        except IndexError:
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def remove_label(self, label):
        self.message_type.remove(label)
        self.update()
        self.label_removed.emit(label)

    def remove_label_at(self, index: int):
        try:
            label = self.message_type[index]
            self.remove_label(label)
        except IndexError:
            pass
