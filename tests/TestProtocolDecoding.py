import copy
import unittest
from PyQt5.QtTest import QTest
from urh.controller.MainController import MainController

import tests.startApp

app = tests.startApp.app

class TestProtocolDecoding(unittest.TestCase):
    def setUp(self):
        self.form = MainController()
        self.cframe = self.form.compare_frame_controller
        self.form.ui.tabWidget.setCurrentIndex(1)

    def test_set_decoding(self):
        """
        Check if decoding is applied for newly added protocol
        :return:
        """
        self.form.add_signalfile("./data/esaver.complex")
        QTest.qWait(100)
        self.assertEqual(self.cframe.protocol_model.row_count, 3)

        display_bits = copy.deepcopy(self.cframe.protocol_model.display_data)
        self.cframe.ui.cbDecoding.setCurrentIndex(1) # NRZ-I
        QTest.qWait(100)
        for i, line in enumerate(self.cframe.protocol_model.display_data):
            for j, bit in enumerate(line):
                self.assertTrue(self.__is_inv(display_bits[i][j], bit),
                                msg="Pos: {0}/{1} Bit1: {2} Bit2: {3}".format(i,j,display_bits[i][j],bit))

        self.form.add_signalfile("./data/esaver.complex")
        QTest.qWait(100)
        self.assertEqual(self.cframe.protocol_model.row_count, 6)

        cfc_bits = self.cframe.protocol_model.display_data
        for i, line in enumerate(display_bits):
            for j, bit in enumerate(line):
                self.assertTrue(self.__is_inv(cfc_bits[i + 3][j], bit),
                    msg="Pos: {0}/{1} Bit1: {2} Bit2: {3}".format(i,j,cfc_bits[i + 3][j],bit))



    def __is_inv(self, a: str, b: str):
        # We only check bits here
        if a not in ("0", "1") or b not in ("0", "1"):
            return True

        if a == "0" and b == "1":
            return True
        if a == "1" and b == "0":
            return True
        return False
