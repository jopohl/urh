import faulthandler
import os
import sip
import time
import unittest

import gc
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDropEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.utils_testing import write_settings, get_path_for_data_file
from urh.controller.MainController import MainController
from urh.util.Logger import logger

faulthandler.enable()


class QtTestCase(unittest.TestCase):
    CLOSE_TIMEOUT = 10
    WAIT_TIMEOUT_BEFORE_NEW = 10
    SHOW = os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "show_gui"))

    @classmethod
    def setUpClass(cls):
        import multiprocessing as mp
        try:
            mp.set_start_method("spawn")
        except RuntimeError:
            pass
        assert mp.get_start_method() == "spawn"

        write_settings()
        cls.app = QApplication([cls.__name__])
        logger.debug("Start new app with name {}".format(cls.app.applicationName()))

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)
        cls.app = None
        QTest.qWait(10)
        time.sleep(0.1)

    def setUp(self):
        self.form = MainController()
        if self.SHOW:
            self.form.show()

    def tearDown(self):
        if hasattr(self, "dialog"):
            self.dialog.close()
            sip.delete(self.dialog)
            self.dialog = None
        if hasattr(self, "form"):
            self.form.close_all()
            self.form.close()
            sip.delete(self.form)
            self.form = None
        gc.collect()

    def wait_before_new_file(self):
        QApplication.instance().processEvents()
        QTest.qWait(self.WAIT_TIMEOUT_BEFORE_NEW)

    def add_signal_to_form(self, filename: str):
        self.wait_before_new_file()
        self.form.add_signalfile(get_path_for_data_file(filename))

    def get_path_for_filename(self, filename) -> str:
        return get_path_for_data_file(filename)

    def add_signal_to_generator(self, signal_index: int):
        gframe = self.form.generator_tab_controller
        item = gframe.tree_model.rootItem.children[0].children[signal_index]
        index = gframe.tree_model.createIndex(signal_index, 0, item)
        rect = gframe.ui.treeProtocols.visualRect(index)
        QTest.mousePress(gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos=rect.center())
        self.assertEqual(gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = gframe.tree_model.mimeData(gframe.ui.treeProtocols.selectedIndexes())
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))

    def add_all_signals_to_simulator(self):
        assert isinstance(self.form, MainController)
        sim_frame = self.form.simulator_tab_controller
        sim_frame.ui.treeProtocols.selectAll()
        self.assertGreater(len(sim_frame.ui.treeProtocols.selectedIndexes()), 0)
        mimedata = sim_frame.tree_model.mimeData(sim_frame.ui.treeProtocols.selectedIndexes())
        drop_event = QDropEvent(sim_frame.ui.gvSimulator.rect().center(), Qt.CopyAction | Qt.MoveAction,
                                mimedata, Qt.LeftButton, Qt.NoModifier)
        drop_event.acceptProposedAction()
        sim_frame.ui.gvSimulator.dropEvent(drop_event)

    def get_free_port(self):
        import socket
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
