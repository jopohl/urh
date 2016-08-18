import unittest

from urh.signalprocessing.encoding import encoding

class TestCarrier(unittest.TestCase):
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
