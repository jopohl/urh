import unittest

from urh.signalprocessing.encoder import Encoder
from urh.util.crc import crc_generic


class TestDecoding(unittest.TestCase):
    # Testmethode muss immer mit Präfix test_* starten
    def test_carrier(self):
        e = Encoder()

        # Test 1
        e.carrier = "----1....1**"  # or "....1....101", ...
        original_inpt = e.str2bit("000010000100111111111100")
        inpt = original_inpt.copy()
        #print("\nOriginal:", inpt)
        output, err, _ = e.code_carrier(True, inpt)
        #print("Decoded: ", output, err)
        newinpt, err, _ = e.code_carrier(False, output)
        #print("Encoded: ", newinpt, err)
        self.assertEqual(original_inpt, newinpt)

    def test_enocean(self):
        e = Encoder()


        received = "010101010110100111101010111011101110111011100110001011101010001011101110110111011101000"
        # First step is invert the received bits!!!
        #received = "10101010 1001 011000010101 000100010001 000100011001 110100010101 110100010001 0010001000 1011"
        preamble = "10101010"
        sof = "1001"
        eof = "1011"

        self.assertIn(preamble, received)
        self.assertIn(sof, received)
        self.assertIn(eof, received)

        # Preamble/SOF/EOF remain unchanged
        expected_result = preamble + sof + "01100001 00000000 00000010 11000001 11000000 00100100" + eof
        expected_result2 = preamble + sof + "01010000 00000000 00000010 11000001 11000000 00100010" + eof

        decoded, err, _ = e.code_enocean(True, e.str2bit(received.replace(" ","")))
        self.assertEqual(err, 0)
        reencoded, err, _ = e.code_enocean(False, decoded)
        self.assertEqual(err, 0)



        self.assertEqual(decoded, e.str2bit(expected_result.replace(" ", "")))
        self.assertEqual(reencoded, e.str2bit(received))

        received = e.str2bit("00001010010101111111000")
        expected_result = e.str2bit("1010010101111111000")
        e.cutmode = 0
        e.cutmark = [True, False, True, False]
        decoded, err, _ = e.code_cut(True, received)
        self.assertEqual(decoded, expected_result)

        received = e.str2bit("00001010010101111111000")
        expected_result = e.str2bit("00001010")
        e.cutmode = 1
        e.cutmark = [True, False, True, False]
        decoded, err, _ = e.code_cut(True, received)
        self.assertEqual(decoded, expected_result)

        received = e.str2bit("00001010010101111111000")
        expected_result = e.str2bit("001010010101111111000")
        e.cutmode = 2
        e.cutmark = 2
        decoded, err, _ = e.code_cut(True, received)
        self.assertEqual(decoded, expected_result)

        received = e.str2bit("00001010010101111111000")
        expected_result = e.str2bit("000")
        e.cutmode = 3
        e.cutmark = 2
        decoded, err, _ = e.code_cut(True, received)
        self.assertEqual(decoded, expected_result)

        received = e.str2bit("00001010010101111111000")
        expected_result = e.str2bit("00001010010101111111000")
        e.cutmode = 0
        e.cutmark = [True, False, True, False, True, False]
        decoded, err, _ = e.code_cut(True, received)
        self.assertEqual(decoded, expected_result)

    def test_enocean_crc_polynomial(self):
        e = Encoder()

        msg1 = "aa9a6d201006401009802019e411e8035b"
        msg2 = "aa9a6d2010000ffdaaf01019e411e8071b"

        # Remove Preamble + SOF + EOF for CRC calculation
        msg1 = e.hex2bit("a6d201006401009802019e411e80")
        crc1 = e.hex2bit("35")
        msg2 = e.hex2bit("a6d2010000ffdaaf01019e411e80")
        crc2 = e.hex2bit("71")

        calc_crc1 = e.enocean_crc8(msg1)
        calc_crc2 = e.enocean_crc8(msg2)
        self.assertTrue(calc_crc1 == crc1)
        self.assertTrue(calc_crc2 == crc2)