import math

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QFont
import numpy

from urh.signalprocessing.ProtocoLabel import ProtocolLabel


class FuzzingTableModel(QAbstractTableModel):
    def __init__(self, fuzzing_label: ProtocolLabel, proto_view: int, parent=None):
        super().__init__(parent)
        self.fuzzing_label = fuzzing_label
        self.col_count = 0
        self.row_count = 0
        self.proto_view = proto_view
        self.data = None

        self.remove_duplicates = True

    def update(self):
        if self.fuzzing_label and len(self.fuzzing_label.fuzz_values) > 0:
            if self.remove_duplicates:
                seq = self.fuzzing_label.fuzz_values[:]
                seen = set()
                add_seen = seen.add
                self.fuzzing_label.fuzz_values = [l for l in seq if not (l in seen or add_seen(l))]

            self.data = self.fuzzing_label.fuzz_values
            if self.proto_view == 0:
                self.col_count = len(self.fuzzing_label.fuzz_values[0])
            elif self.proto_view == 1:
                self.col_count = math.ceil(len(self.fuzzing_label.fuzz_values[0]) / 4)
            elif self.proto_view == 2:
                self.col_count = math.ceil(len(self.fuzzing_label.fuzz_values[0]) / 8)
            self.row_count = len(self.fuzzing_label.fuzz_values)
        else:
            self.col_count = 0
            self.row_count = 0
            self.data = None

        self.beginResetModel()
        self.endResetModel()

    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.row_count

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.col_count

    def data(self, index: QModelIndex, role=None):
        i = index.row()
        j = index.column()
        if role == Qt.DisplayRole:
            if self.data is None:
                return None
            else:
                if self.proto_view == 0:
                    return self.data[i][j]
                elif self.proto_view == 1:
                    return "{0:x}".format(int(self.data[i][4 * j:4 * (j + 1)], 2))
                elif self.proto_view == 2:
                    return chr(int(self.data[i][8 * j:8 * (j + 1)], 2))

        elif role == Qt.FontRole:
            if i == 0:
                font = QFont()
                font.setBold(True)
                return font

    def setData(self, index: QModelIndex, value, role=None):
        i = index.row()
        j = index.column()
        hex_chars = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f")
        if self.proto_view == 0 and value in ("0", "1"):
            l = list(self.data[i])
            l[j] = value
            self.data[i] = ''.join(l)
            self.update()
        elif self.proto_view == 1 and value in hex_chars:
            l = list(self.data[i])
            l[j:4 * (j + 1)] = "{0:04b}".format(int(value, 16))
            self.data[i] = ''.join(l)
            self.update()
        elif self.proto_view == 2 and len(value) == 1:
            l = list(self.data[i])
            l[j:8 * (j + 1)] = "{0:08b}".format(ord(value))
            self.data[i] = ''.join(l)
            self.update()

        return True

    def flags(self, QModelIndex):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def add_range(self, start: int, end: int, step: int, labels=None):
        if labels is None:
            labels = [self.fuzzing_label]

        for l in labels:
            e = end if end < l.fuzz_maximum else l.fuzz_maximum
            for i in range(start, e, step):
                l.add_decimal_fuzz_value(i)

        self.update()

    def add_boundaries(self, lower: int, upper: int, num_vals:int, labels=None):
        if labels is None:
            labels = [self.fuzzing_label]


        if lower > -1:
            for l in labels:
                low = lower if lower < l.fuzz_maximum + num_vals else l.fuzz_maximum - num_vals
                for i in range(low, low + num_vals):
                    l.add_decimal_fuzz_value(i)

        if upper > -1:
            for l in labels:
                up = upper if upper < l.fuzz_maximum + 1 else l.fuzz_maximum - 1
                for i in range(up - num_vals + 1, up + 1):
                    l.add_decimal_fuzz_value(i)

        self.update()

    def add_random(self, number: int, minimum: int, maximum: int, labels=None):
        if labels is None:
            labels = [self.fuzzing_label]

        for l in labels:
            mini = minimum if minimum < l.fuzz_maximum else l.fuzz_maximum
            maxi = maximum if maximum < l.fuzz_maximum else l.fuzz_maximum

            random_vals = numpy.random.randint(mini, maxi + 1, number)
            for val in random_vals:
                l.add_decimal_fuzz_value(val)

        self.update()
