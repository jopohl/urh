import sys
import unittest

import sip
from PyQt5.QtWidgets import QApplication

from tests import utils_testing
from urh.signalprocessing.encoder import Encoder

utils_testing.write_settings()

class TestWhitening(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication(sys.argv)

    @classmethod
    def tearDownClass(cls):
        cls.app.quit()
        sip.delete(cls.app)

    # Testmethode muss immer mit Präfix test_* starten
    def test_whitening(self):
        e = Encoder()

        # Test 1
        e.data_whitening_sync = e.hex2bit("67686768")
        original_inpt = e.hex2bit("aaaaaaaa67686768f9ca03909567ba76a8") + [False] # Korrektes Signal, bitgenau
        inpt = original_inpt.copy()
        #print (e.bit2hex(inpt))
        output, err, _ = e.apply_data_whitening(True, inpt)
        #print (e.bit2hex(output), err)
        newinpt, err, _ = e.apply_data_whitening(False, output)
        #print (e.bit2hex(newinpt), newinpt, err)
        self.assertEqual(original_inpt, newinpt)


