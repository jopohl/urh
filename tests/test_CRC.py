import time
import unittest

from urh.signalprocessing.Encoding import Encoding
from urh.util import util
from urh.util.GenericCRC import GenericCRC
from urh.util.WSPChecksum import WSPChecksum


class TestCRC(unittest.TestCase):
    def test_crc(self):
        # http://depa.usst.edu.cn/chenjq/www2/software/crc/CRC_Javascript/CRCcalculation.htm
        # CRC-16: polynomial="16_standard", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False
        # CRC-16-CCITT: polynomial="16_ccitt", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False

        # http://www.lammertbies.nl/comm/info/crc-calculation.html <- Fehler
        # CRC-16: polynomial="16_standard", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False
        c = GenericCRC(polynomial=WSPChecksum.CRC_8_POLYNOMIAL)
        e = Encoding()

        bitstr = [
            "010101010110100111011010111011101110111011100110001011101010001011101110110110101101",
            "010101010110101001101110111011101110111011100110001011101010001011101110110111100101",
            "010101010110100111010010111011101110111011100110001011101010001011101110110110100101",
        ]

        expected = ["78", "c9", "f2"]

        for value, expect in zip(bitstr, expected):
            nv = ""
            for i in range(0, len(value)):
                if value[i] == "1":
                    nv += "0"
                else:
                    nv += "1"

            self.assertEqual(util.bit2hex(c.crc(e.str2bit(value[4:-8]))), expect)

    def test_crc8(self):
        messages = ["aabbcc", "abcdee", "dacafe"]

        expected = ["7d", "24", "33"]
        crc = GenericCRC(polynomial=GenericCRC.DEFAULT_POLYNOMIALS["8_ccitt"])

        for msg, expect in zip(messages, expected):
            bits = util.hex2bit(msg)
            self.assertEqual(util.bit2hex(crc.crc(bits)), expect)

    def test_different_crcs(self):
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        bitstring_set = [
            "101001001010101010101011101111111000000000000111101010011101011",
            "101001001010101101111010110111101010010110111010",
            "00000000000000000000000000000000100000000000000000000000000000000001111111111111",
            "1111111111111111111111111111111110111111111111111111110111111111111111110000000000"
            "1",
        ]

        for j in c.DEFAULT_POLYNOMIALS:
            c.polynomial = c.choose_polynomial(j)
            for i in bitstring_set:
                # Standard
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)

                # Special final xor
                c.final_xor = c.str2bit("0000111100001111")
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.final_xor = [False] * 16

                # Special start value
                c.start_value = c.str2bit("1010101010101010")
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.start_value = [False] * 16

                # reverse_polynomial
                c.reverse_polynomial = True
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.reverse_polynomial = False

                # lsb_first
                c.lsb_first = True
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.lsb_first = False

                # little_endian
                c.little_endian = True
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.little_endian = False

                # reverse all
                c.reverse_all = True
                crc_new = c.crc(c.str2bit(i))
                crc_old = c.reference_crc(c.str2bit(i))
                self.assertEqual(crc_new, crc_old)
                c.reverse_all = False

    def test_cache(self):
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        c.calculate_cache(8)
        self.assertEqual(len(c.cache), 256)

    def test_different_crcs_fast(self):
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        bitstring_set = [
            "10101010",
            "00000001",
            "000000010",
            "000000011",
            "0000000100000001",
            "101001001010101010101011101111111000000000000111101010011101011",
            "101001001010101101111010110111101010010110111010",
            "00000000000000000000000000000000100000000000000000000000000000000001111111111111",
            "1111111111111111111111111111111110111111111111111111110111111111111111110000000000"
            "1",
        ]

        for j in c.DEFAULT_POLYNOMIALS:
            c.polynomial = c.choose_polynomial(j)
            for i in bitstring_set:
                for cache in [8, 4, 7, 12, 16]:
                    c.calculate_cache(cache)
                    # Standard
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)

                    # Special final xor
                    c.final_xor = c.str2bit("0000111100001111")
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.final_xor = [False] * 16

                    # Special start value
                    c.start_value = c.str2bit("1010101010101010")
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.start_value = [False] * 16

                    # little_endian
                    c.little_endian = True
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.little_endian = False

                    # reverse all
                    c.reverse_all = True
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.reverse_all = False

                    # reverse_polynomial
                    # We need to clear the cache before and after
                    c.cache = []
                    #
                    c.reverse_polynomial = True
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.reverse_polynomial = False
                    #
                    c.cache = []

                    # TODO: Does only work for cachesize = 8
                    # lsb_first
                    c.calculate_cache(8)
                    c.lsb_first = True
                    crc_new = c.cached_crc(c.str2bit(i))
                    crc_old = c.reference_crc(c.str2bit(i))
                    self.assertEqual(crc_old, crc_new)
                    c.lsb_first = False

    def test_reverse_engineering(self):
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        bitstring_set = [
            "1110001111001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110010011001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110010111001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110011011001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
        ]
        bitset = []
        crcset = []

        for i in bitstring_set:
            tmp = c.str2bit(i)
            bitset.append(tmp)
            crcset.append(c.crc(tmp))

        polynomial = c.reverse_engineer_polynomial(bitset, crcset)
        if polynomial:
            self.assertEqual(c.bit2str(polynomial), "1000000000000101")
            self.assertEqual(util.bit2hex(polynomial), "8005")

    def test_not_aligned_data_len(self):
        c = GenericCRC(
            polynomial="16_standard",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        polynomials = ["8_standard", "16_standard", "16_ccitt", "16_dnp"]
        crcs = {
            "8_standard": 0xD5,
            "16_standard": 0x8005,
            "16_ccitt": 0x1021,
            "16_dnp": 0x3D65,
        }
        for j in polynomials:
            c.polynomial = c.choose_polynomial(j)
            inpt = "1"
            for i in range(0, 32):
                val = c.bit2int(c.crc(c.str2bit(inpt)))
                self.assertEqual(val, crcs[j])
                inpt = "0" + inpt

    def test_bruteforce_parameters_and_data_range(self):
        c = GenericCRC(
            polynomial="16_ccitt",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        inpt = "101010101010101010000000111000000000000011100000001011010010110100000000111000000101001010000100000000000100111001111110010000000011011111111001001101100001100010100000000000111011110100010"
        vrfy_crc = "0011101111010001"

        result = c.bruteforce_parameters_and_data_range(
            c.str2arr(inpt), len(inpt) - len(vrfy_crc) - 1
        )
        self.assertEqual(result, (2, 84, 172))
        self.assertEqual(
            vrfy_crc, c.bit2str(c.crc(c.str2arr(inpt[result[1] : result[2]])))
        )

    def test_bruteforce_parameters_and_data_range_improved(self):
        c = GenericCRC(
            polynomial="16_ccitt",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        inpt = "101010101010101010000000111000000000000011100000001011010010110100000000111000000101001010000100000000000100111001111110010000000011011111111001001101100001100010100000000000111011110100010"
        vrfy_crc = "0011101111010001"

        t1 = 0
        runs = 100
        for i in range(0, runs):
            t = time.time()
            result = c.bruteforce_parameters_and_data_range(
                c.str2arr(inpt), len(inpt) - len(vrfy_crc) - 1
            )
            t1 += time.time() - t
            # print(result, c.bit2str(c.crc(c.str2arr(inpt[result[1]:result[2]]))))
            self.assertEqual(result[0], 2)  # Parameters = 2
            self.assertEqual(result[1], len(inpt) - 1 - 16 - 88)  # start of datarange
            self.assertEqual(result[2], len(inpt) - 1 - 16)  # end of datarange
            inpt = "0" + inpt if i % 2 == 0 else "1" + inpt
        # print("Performance:", t1/runs)
        self.assertLess(t1 / runs, 0.1)  # Should be faster than 100ms in average

    def test_adaptive_crc_calculation(self):
        c = GenericCRC(
            polynomial="16_ccitt",
            start_value=False,
            final_xor=False,
            reverse_polynomial=False,
            reverse_all=False,
            lsb_first=False,
            little_endian=False,
        )
        inpt1 = "10101010101010"
        inpt2 = "1010101010101001"

        crc1 = c.crc(c.str2arr(inpt1))
        crc2 = c.crc(c.str2arr(inpt2))

        # Compute crc2 from crc1 in a faster way
        # Note: In general only forward direction
        delta = "01"
        c.start_value = crc1
        crcx = c.crc(c.str2arr(delta))

        self.assertEqual(crcx, crc2)
