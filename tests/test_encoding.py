import copy
import array

from tests.QtTestCase import QtTestCase
from urh.signalprocessing.Encoding import Encoding
from urh.util import util
from urh.util.WSPChecksum import WSPChecksum


class TestDecoding(QtTestCase):
    def setUp(self):
        pass

    def test_carrier(self):
        e = Encoding()

        # Test 1
        e.carrier = "----1....1**"  # or "....1....101", ...
        original_inpt = e.str2bit("000010000100111111111100")
        inpt = copy.copy(original_inpt)
        #print("\nOriginal:", inpt)
        output, err, _ = e.code_carrier(True, inpt)
        #print("Decoded: ", output, err)
        newinpt, err, _ = e.code_carrier(False, output)
        #print("Encoded: ", newinpt, err)
        self.assertEqual(original_inpt, newinpt)

    def test_cut_decoding(self):
        e = Encoding()

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

    def test_enocean_switch_telegram(self):
        e = Encoding()


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


    def test_enocean_crc8_message(self):
        e = Encoding()
        received = util.hex2bit("aacbac4cddd5ddd3bddd5ddcc5ddcddd4c2d5d5c2cdddab200000")
        preamble, sof, eof = "aa", "9", "b"

        decoded, err, state = e.code_enocean(decoding=True, inpt=received)
        self.assertEqual(err, 0)
        self.assertEqual(state, e.ErrorState.SUCCESS)
        self.assertIn(preamble, util.bit2hex(decoded))
        self.assertIn(sof, util.bit2hex(decoded))
        self.assertIn(eof, util.bit2hex(decoded))

        reencoded, errors, state = e.code_enocean(decoding=False, inpt=decoded)
        self.assertEqual(errors, 0)
        self.assertEqual(state, e.ErrorState.SUCCESS)

        redecoded, errors, state = e.code_enocean(decoding=True, inpt=reencoded)
        self.assertEqual(errors, 0)
        self.assertEqual(state, e.ErrorState.SUCCESS)
        self.assertEqual(decoded, redecoded)


    def test_enocean_crc_polynomial(self):
        e = Encoding()

        msg1 = "aa9a6d201006401009802019e411e8035b"
        msg2 = "aa9a6d2010000ffdaaf01019e411e8071b"

        # Remove Preamble + SOF + EOF for CRC calculation
        msg1 = util.hex2bit("a6d201006401009802019e411e8035")
        crc1 = util.hex2bit("35")
        msg2 = util.hex2bit("a6d2010000ffdaaf01019e411e8071")
        crc2 = util.hex2bit("71")

        wsp_checker = WSPChecksum()
        calc_crc1 = wsp_checker.calculate(msg1)
        calc_crc2 = wsp_checker.calculate(msg2)
        self.assertTrue(calc_crc1 == crc1)
        self.assertTrue(calc_crc2 == crc2)

    def test_morse(self):
        e = Encoding()
        e.morse_low = 3
        e.morse_high = 5
        e.morse_wait = 1
        msg1 = "1111111000111100011111100100001111111111111111111111011"
        msg2 = "0111110111011111011101111101110"

        encoded = e.str2bit(msg1)
        compare = e.str2bit(msg2)
        decoded, err, _ = e.code_morse(decoding=True, inpt=encoded)
        reencoded, _, _ = e.code_morse(decoding=False, inpt=decoded)
        self.assertEqual(err, 1)
        self.assertEqual(reencoded, compare)

    def test_substitution(self):
        e = Encoding()
        e.src = [array.array("B", [True, True, True, False]), array.array("B", [True, False, False, False])]
        e.dst = [array.array("B", [True]), array.array("B", [False])]

        # encoded-string with 3 missing trailing zeroes
        encoded = e.str2bit("1000111010001110111011101110111011101110100011101110111011101110111011101000100010001000100010001")
        compare = e.str2bit("1000111010001110111011101110111011101110100011101110111011101110111011101000100010001000100010001000")
        decoded, err, _ = e.code_substitution(decoding=True, inpt=encoded)
        reencoded, _, _ = e.code_substitution(decoding=False, inpt=decoded)
        self.assertEqual(err, 3)
        self.assertEqual(reencoded, compare)
