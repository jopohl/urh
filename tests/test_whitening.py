import copy

import array

from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Encoding import Encoding
from urh.util import util


class TestWhitening(QtTestCase):
    def test_whitening(self):
        e = Encoding()

        # Test 1
        e.data_whitening_sync = util.hex2bit("67686768")
        original_inpt = util.hex2bit("aaaaaaaa67686768f9ca03909567ba76a8") + array.array("B", [False]) # Korrektes Signal, bitgenau
        inpt = copy.copy(original_inpt)
        #print (util.bit2hex(inpt))
        output, err, _ = e.apply_data_whitening(True, inpt)
        #print (util.bit2hex(output), err)
        newinpt, err, _ = e.apply_data_whitening(False, output)
        #print (util.bit2hex(newinpt), newinpt, err)
        self.assertEqual(original_inpt, newinpt)
