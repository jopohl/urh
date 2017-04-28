import time
from collections import deque

from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer


class TestGeneratorTable(QtTestCase):
    NUM_MESSAGES = 2**16
    BITS_PER_MESSAGE = 100
    NUM_LABELS = 3

    def setUp(self):
        super().setUp()

    def test_performance(self):
        self.cframe = self.form.compare_frame_controller
        self.gframe = self.form.generator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(2)
        self.cframe.ui.cbProtoView.setCurrentIndex(0)
        self.gframe.ui.cbViewType.setCurrentIndex(0)

        t = time.time()
        proto = self.__build_protocol()
        print("Time for building protocol:", time.time()-t)
        t = time.time()
        self.cframe.add_protocol(proto)
        print("Time for adding protocol:", time.time()-t)
        t = time.time()
        proto.qt_signals.protocol_updated.emit()
        print("Time for emitting signal", time.time()-t)
        self.assertEqual(self.cframe.protocol_model.row_count, self.NUM_MESSAGES)
        self.assertEqual(self.cframe.protocol_model.col_count, self.BITS_PER_MESSAGE)

        t = time.time()
        self.__add_labels()
        print("time for adding labels", time.time()-t)




        t = time.time()
        item = self.gframe.tree_model.rootItem.children[0].children[0]
        index = self.gframe.tree_model.createIndex(0, 0, item)
        rect = self.gframe.ui.treeProtocols.visualRect(index)
        QTest.mousePress(self.gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos = rect.center())
        print("{0}: {1} µs".format("Time for making selection", (time.time() - t) * 10**6))

        self.assertEqual(self.gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = self.gframe.tree_model.mimeData(self.gframe.ui.treeProtocols.selectedIndexes())
        t  = time.time()
        #with PyCallGraph(output=GraphvizOutput()):
        self.gframe.table_model.dropMimeData(mimedata, 1, -1, -1, self.gframe.table_model.createIndex(0, 0))
        print("{0}: {1} s".format("Time for dropping mimedata", (time.time() - t)))
        self.assertEqual(self.gframe.table_model.row_count, self.NUM_MESSAGES)

        indx = self.gframe.table_model.createIndex(int(self.NUM_MESSAGES / 2), int(self.BITS_PER_MESSAGE / 2))
        roles = (Qt.DisplayRole, Qt.BackgroundColorRole, Qt.TextAlignmentRole, Qt.TextColorRole, Qt.FontRole)
        time_for_display = 100
        for role in roles:
            t = time.time()
            self.gframe.table_model.data(indx, role = role)
            microseconds = (time.time() - t) * 10 ** 6
            self.assertLessEqual(microseconds, 2 * time_for_display, msg=self.__role_to_str(role))
            if role == Qt.DisplayRole:
                time_for_display = microseconds
            print("{0}: {1} µs".format(self.__role_to_str(role), microseconds))


    def test_insert_performance(self):
        NUM_INSERTS = 2**20
        l = list(range(100))

        t = time.time()
        for i in range(NUM_INSERTS):
            l.insert(50, i)

        print("list", time.time() - t)

        d = deque(range(100))

        t = time.time()
        for i in range(NUM_INSERTS):
            d.insert(50, i)

        print("deque", time.time() - t)



    def __build_protocol(self):
        result = ProtocolAnalyzer(signal=None)
        for _ in range(self.NUM_MESSAGES):
            b = Message([True] * self.BITS_PER_MESSAGE, pause = 1000, message_type=result.default_message_type)
            result.messages.append(b)
        return result

    def __add_labels(self):
        start = 0
        label_len = 3
        for i in range(self.NUM_LABELS):
            self.cframe.add_protocol_label(start=start, end=start + label_len, messagenr=0, proto_view=0, edit_label_name = False)
            start += label_len + 1

    def __role_to_str(self, role):
        if role == Qt.DisplayRole:
            return "Display"
        if role == Qt.BackgroundColorRole:
            return "BG-Color"
        if role == Qt.TextAlignmentRole:
            return "Text-Alignment"
        if role == Qt.TextColorRole:
            return "TextColor"
        if role == Qt.ToolTipRole:
            return "ToolTip"
        if role == Qt.FontRole:
            return "Font"
