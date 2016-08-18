import unittest

from urh.signalprocessing.encoding import encoding

class TestDecoding(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_carrier(self):
        e = encoding()

        # Test 1
        e.carrier = "----1....1**"  # or "....1....101", ...
        original_inpt = e.str2bit("000010000100111111111100")
        inpt = original_inpt.copy()
        print("\nOriginal:", inpt)
        output, err = e.code_carrier(True, inpt)
        print("Decoded: ", output, err)
        newinpt, err = e.code_carrier(False, output)
        print("Encoded: ", newinpt, err)
        self.assertEqual(original_inpt, newinpt)

    def test_enocean(self):
        e = encoding()


        # received = "01010101011010011110101011101110111011101110011000101110101000101110111011011101110100"
        # First step is invert the received bits!!!
        received = "10101010 1001 011000010101 000100010001 000100011001 110100010101 110100010001 0010001000 1011"
        preamble = "10101010"
        sof = "1001"
        eof = "1011"

        self.assertIn(preamble, received)
        self.assertIn(sof, received)
        self.assertIn(eof, received)

        print("Received data", received)

        # Preamble/SOF/EOF remain unchanged
        expected_result = preamble + sof + "01100001 00000000 00000010 11000001 11000000 00100100" + eof

        # Needs to be fixed!
        decoded = e.decode(e.str2bit(received.replace(" ","")))

        self.assertEqual(decoded, e.str2bit(expected_result.replace(" ", "")))






