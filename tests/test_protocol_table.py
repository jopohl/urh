import time
import unittest

from PyQt5.QtCore import Qt

import tests.utils_testing
from urh.controller.MainController import MainController
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

app = tests.utils_testing.get_app()


class TestProtocolTable(unittest.TestCase):
    NUM_MESSAGES = 100
    BITS_PER_MESSAGE = 100
    NUM_LABELS = 25

    def setUp(self):
        self.form = MainController()
        self.cframe = self.form.compare_frame_controller
        self.form.ui.tabWidget.setCurrentIndex(1)
        self.cframe.ui.cbProtoView.setCurrentIndex(0)

        proto = self.__build_protocol()
        self.cframe.add_protocol(proto)
        proto.qt_signals.protocol_updated.emit()

        self.assertEqual(self.cframe.protocol_model.row_count, self.NUM_MESSAGES)
        self.assertEqual(self.cframe.protocol_model.col_count, self.BITS_PER_MESSAGE)

        self.__add_labels()
        self.assertEqual(len(self.cframe.proto_analyzer.protocol_labels), self.NUM_LABELS)

    def tearDown(self):
        self.form.close_all()
        tests.utils_testing.short_wait()

    def test_set_shown_protocols_performance(self):
        t = time.time()
        self.cframe.set_shown_protocols()
        print("{} lines/{} columns: \t\t {:.2f}s".format(self.cframe.protocol_model.row_count,
                                                       self.cframe.protocol_model.col_count,
                                                       time.time()-t))

        for _ in range(9):
            self.cframe.add_protocol(self.__build_protocol())

        t = time.time()
        self.cframe.set_shown_protocols()
        print("{} lines/{} columns: \t {:.2f}s".format(self.cframe.protocol_model.row_count,
                                                       self.cframe.protocol_model.col_count,
                                                       time.time()-t))


    def __build_protocol(self):
        result = ProtocolAnalyzer(signal=None)
        for _ in range(self.NUM_MESSAGES):
            b = Message([True] * self.BITS_PER_MESSAGE, pause=1000, message_type=result.default_message_type)
            result.messages.append(b)
        return result

    def __add_labels(self):
        start = 0
        label_len = 3
        for i in range(self.NUM_LABELS):
            self.cframe.add_protocol_label(start=start, end=start+label_len, proto_view=0, messagenr=0, edit_label_name=False)
            start += label_len +1

    def __role_to_str(self, role):
        if role == Qt.DisplayRole:
            return "Display"
        if role == Qt.BackgroundColorRole:
            return "BG-Color"
        if role == Qt.TextAlignmentRole:
            return "Text-Alignment"
        if role == Qt.TextColorRole:
            return "TextColor"
        if role ==  Qt.ToolTipRole:
            return "ToolTip"
        if role == Qt.FontRole:
            return "Font"
