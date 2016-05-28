import time
import unittest

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.startApp
from urh.controller.MainController import MainController
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolBlock import ProtocolBlock

app = tests.startApp.app



class TestProtocolTable(unittest.TestCase):
    NUM_BLOCKS = 100
    BITS_PER_BLOCK = 100
    NUM_LABELS = 25

    def setUp(self):
        self.form = MainController()
        QTest.qWait(10)
        self.cframe = self.form.compare_frame_controller
        self.form.ui.tabWidget.setCurrentIndex(1)

        proto = self.__build_protocol()
        self.cframe.add_protocol(proto)
        proto.qt_signals.protocol_updated.emit()
        QTest.qWait(10)

        self.assertEqual(self.cframe.protocol_model.row_count, self.NUM_BLOCKS)
        self.assertEqual(self.cframe.protocol_model.col_count, self.BITS_PER_BLOCK)

        self.__add_labels()
        QTest.qWait(10)
        self.assertEqual(len(self.cframe.proto_analyzer.protocol_labels), self.NUM_LABELS)


    def test_performance(self):
        indx = self.cframe.protocol_model.createIndex(int(self.NUM_BLOCKS/2), int(self.BITS_PER_BLOCK/2))
        roles = (Qt.DisplayRole, Qt.BackgroundColorRole, Qt.TextAlignmentRole, Qt.TextColorRole, Qt.FontRole)

        for role in roles:
            t = time.time()
            self.cframe.protocol_model.data(indx, role=role)
            microseconds = (time.time()-t)*10**6
            self.assertLess(microseconds, 25)

    def __build_protocol(self):
        result = ProtocolAnalyzer(signal=None)
        for _ in range(self.NUM_BLOCKS):
            b = ProtocolBlock([True] * self.BITS_PER_BLOCK, pause=1000, bit_alignment_positions=[])
            result.blocks.append(b)
        return result

    def __add_labels(self):
        start = 0
        label_len = 3
        for i in range(self.NUM_LABELS):
            self.cframe.add_protocol_label(start, start+label_len, 0, 0, False, edit_label_name=False)
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