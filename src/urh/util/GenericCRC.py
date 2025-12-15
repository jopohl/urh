import array
import copy
from collections import OrderedDict
from xml.etree import ElementTree as ET

from urh.cythonext import util as c_util
from urh.util import util


class GenericCRC(object):
    # https://en.wikipedia.org/wiki/Polynomial_representations_of_cyclic_redundancy_checks
    DEFAULT_POLYNOMIALS = OrderedDict(
        [
            # x^8 + x^7 + x^6 + x^4 + x^2 + 1
            ("8_standard", array.array("B", [1, 1, 1, 0, 1, 0, 1, 0, 1])),
            # x^16+x^15+x^2+x^0
            (
                "16_standard",
                array.array("B", [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1]),
            ),
            # x^16+x^12+x^5+x^0
            (
                "16_ccitt",
                array.array("B", [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]),
            ),
            # x^16+x^13+x^12+x^11+x^10+x^8+x^6+x^5+x^2+x^0
            (
                "16_dnp",
                array.array("B", [1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1]),
            ),
            # x^8 + x^2 + x + 1
            ("8_ccitt", array.array("B", [1, 0, 0, 0, 0, 0, 1, 1, 1])),
        ]
    )

    STANDARD_CHECKSUMS = OrderedDict(
        [
            # see method guess_standard_parameters_and_datarange for default parameters
            # Links:
            #  - https://en.wikipedia.org/wiki/Cyclic_redundancy_check
            #  - http://reveng.sourceforge.net/crc-catalogue/1-15.htm
            #  - https://crccalc.com/
            ("CRC8 (default)", dict(polynomial="0xD5")),
            ("CRC8 CCITT", dict(polynomial="0x07")),
            ("CRC8 Bluetooth", dict(polynomial="0xA7", ref_in=True, ref_out=True)),
            ("CRC8 DARC", dict(polynomial="0x39", ref_in=True, ref_out=True)),
            ("CRC8 NRSC-5", dict(polynomial="0x31", start_value=1)),
            ("CRC16 (default)", dict(polynomial="0x8005", ref_in=True, ref_out=True)),
            ("CRC16 CCITT", dict(polynomial="0x1021", ref_in=True, ref_out=True)),
            (
                "CRC16 NRSC-5",
                dict(polynomial="0x080B", start_value=1, ref_in=True, ref_out=True),
            ),
            ("CRC16 CC1101", dict(polynomial="0x8005", start_value=1)),
            ("CRC16 CDMA2000", dict(polynomial="0xC867", start_value=1)),
            (
                "CRC32 (default)",
                dict(
                    polynomial="0x04C11DB7",
                    start_value=1,
                    final_xor=1,
                    ref_in=True,
                    ref_out=True,
                ),
            ),
        ]
    )

    def __init__(
        self,
        polynomial="16_standard",
        start_value=False,
        final_xor=False,
        reverse_polynomial=False,
        reverse_all=False,
        little_endian=False,
        lsb_first=False,
    ):
        if isinstance(polynomial, str):
            self.caption = polynomial
        else:
            self.caption = ""

        self.polynomial = self.choose_polynomial(polynomial)
        self.reverse_polynomial = reverse_polynomial
        self.reverse_all = reverse_all
        self.little_endian = little_endian
        self.lsb_first = lsb_first

        self.start_value = self.__read_parameter(start_value)
        self.final_xor = self.__read_parameter(final_xor)
        self.cache = []
        self.__cache_bits = 8

    def __read_parameter(self, value):
        if isinstance(value, bool) or isinstance(value, int):
            return array.array("B", [value] * (self.poly_order - 1))
        else:
            if len(value) == self.poly_order - 1:
                return value
            else:
                return array.array("B", value[0] * (self.poly_order - 1))

    def __eq__(self, other):
        if not isinstance(other, GenericCRC):
            return False

        return all(
            getattr(self, attrib) == getattr(other, attrib)
            for attrib in (
                "polynomial",
                "reverse_polynomial",
                "reverse_all",
                "little_endian",
                "lsb_first",
                "start_value",
                "final_xor",
            )
        )

    def __hash__(self):
        return hash(
            (
                self.polynomial.tobytes(),
                self.reverse_polynomial,
                self.reverse_all,
                self.little_endian,
                self.lsb_first,
                self.start_value.tobytes(),
                self.final_xor.tobytes(),
            )
        )

    @property
    def poly_order(self):
        return len(self.polynomial)

    @property
    def polynomial_as_bit_str(self) -> str:
        return "".join("1" if p else "0" for p in self.polynomial)

    @property
    def polynomial_as_hex_str(self) -> str:
        return util.bit2hex(self.polynomial[1:])  # do not show leading one

    @property
    def polynomial_to_html(self) -> str:
        result = ""
        for i in range(self.poly_order):
            index = self.poly_order - 1 - i
            if self.polynomial[i] > 0:
                if index > 1:
                    result += "x<sup>{0}</sup> + ".format(index)
                elif index == 1:
                    result += "x + "
                elif index == 0:
                    result += "1"

        result = result.rstrip(" + ")
        return result

    def set_polynomial_from_hex(self, hex_str: str):
        old = self.polynomial
        self.polynomial = array.array("B", [1]) + util.hex2bit(hex_str)
        if self.polynomial != old:
            self.cache = []
            self.__cache_bits = 8

    def choose_polynomial(self, polynomial):
        if isinstance(polynomial, str):
            return self.DEFAULT_POLYNOMIALS[polynomial]
        elif isinstance(polynomial, int):
            return list(self.DEFAULT_POLYNOMIALS.items())[polynomial][1]
        else:
            return polynomial

    def get_parameters(self):
        return (
            self.polynomial,
            self.start_value,
            self.final_xor,
            self.lsb_first,
            self.reverse_polynomial,
            self.reverse_all,
            self.little_endian,
        )

    def crc(self, inpt):
        result = c_util.crc(
            array.array("B", inpt),
            array.array("B", self.polynomial),
            array.array("B", self.start_value),
            array.array("B", self.final_xor),
            self.lsb_first,
            self.reverse_polynomial,
            self.reverse_all,
            self.little_endian,
        )
        return util.number_to_bits(result, self.poly_order - 1)

    def cached_crc(self, inpt, bits=8):
        if len(self.cache) == 0:
            self.calculate_cache(bits)
        result = c_util.cached_crc(
            self.cache,
            self.__cache_bits,
            array.array("B", inpt),
            array.array("B", self.polynomial),
            array.array("B", self.start_value),
            array.array("B", self.final_xor),
            self.lsb_first,
            self.reverse_polynomial,
            self.reverse_all,
            self.little_endian,
        )
        return util.number_to_bits(result, self.poly_order - 1)

    def calculate_cache(self, bits=8):
        if 0 < bits < self.poly_order:
            self.__cache_bits = bits
        else:
            self.__cache_bits = 8 if self.poly_order > 8 else self.poly_order - 1
        self.cache = c_util.calculate_cache(
            array.array("B", self.polynomial),
            self.reverse_polynomial,
            self.__cache_bits,
        )

    def get_crc_datarange(self, inpt, vrfy_crc_start):
        return c_util.get_crc_datarange(
            array.array("B", inpt),
            array.array("B", self.polynomial),
            vrfy_crc_start,
            array.array("B", self.start_value),
            array.array("B", self.final_xor),
            self.lsb_first,
            self.reverse_polynomial,
            self.reverse_all,
            self.little_endian,
        )

    def reference_crc(self, inpt):
        len_inpt = len(inpt)
        if len(self.start_value) < self.poly_order - 1:
            return False
        crc = copy.copy(self.start_value[0 : (self.poly_order - 1)])

        for i in range(0, len_inpt + 7, 8):
            for j in range(0, 8):
                if self.lsb_first:
                    idx = i + (7 - j)
                else:
                    idx = i + j

                if idx >= len_inpt:
                    break

                if crc[0] != inpt[idx]:
                    crc[0 : self.poly_order - 2] = crc[
                        1 : self.poly_order - 1
                    ]  # crc = crc << 1
                    crc[self.poly_order - 2] = False
                    for x in range(0, self.poly_order - 1):
                        if self.reverse_polynomial:
                            crc[x] ^= self.polynomial[self.poly_order - 1 - x]
                        else:
                            crc[x] ^= self.polynomial[x + 1]
                else:
                    crc[0 : self.poly_order - 2] = crc[
                        1 : self.poly_order - 1
                    ]  # crc = crc << 1
                    crc[self.poly_order - 2] = False

        for i in range(0, self.poly_order - 1):
            if self.final_xor[i]:
                crc[i] = not crc[i]

        if self.reverse_all:
            crc_old = []
            for i in range(0, self.poly_order - 1):
                crc_old.append(crc[self.poly_order - 2 - i])
            crc = crc_old

        if self.poly_order - 1 == 16 and self.little_endian:
            self.__swap_bytes(crc, 0, 1)
        elif self.poly_order - 1 == 32 and self.little_endian:
            self.__swap_bytes(crc, 0, 3)
            self.__swap_bytes(crc, 1, 2)
        elif self.poly_order - 1 == 64 and self.little_endian:
            for pos1, pos2 in [(0, 7), (1, 6), (2, 5), (3, 4)]:
                self.__swap_bytes(crc, pos1, pos2)
        # return crc
        return array.array("B", crc)

    def calculate(self, bits: array.array):
        return self.crc(bits)

    @staticmethod
    def __swap_bytes(array, pos1: int, pos2: int):
        array[pos1 * 8 : pos1 * 8 + 8], array[pos2 * 8 : pos2 * 8 + 8] = (
            array[pos2 * 8 : pos2 * 8 + 8],
            array[pos1 * 8 : pos1 * 8 + 8],
        )

    @staticmethod
    def from_standard_checksum(name: str):
        result = GenericCRC()
        result.set_individual_parameters(**GenericCRC.STANDARD_CHECKSUMS[name])
        result.caption = name
        return result

    def set_individual_parameters(
        self,
        polynomial,
        start_value=0,
        final_xor=0,
        ref_in=False,
        ref_out=False,
        little_endian=False,
        reverse_polynomial=False,
    ):
        # Set polynomial from hex or bit array
        old = self.polynomial
        if isinstance(polynomial, str):
            self.set_polynomial_from_hex(polynomial)
        else:
            self.polynomial = polynomial
        # Clear cache if polynomial changes
        if self.polynomial != old:
            self.cache = []
            self.__cache_bits = 8

        # Set start value completely or 0000/FFFF
        if isinstance(start_value, int):
            self.start_value = array.array("B", [start_value] * (self.poly_order - 1))
        elif (
            isinstance(start_value, array.array)
            and len(start_value) == self.poly_order - 1
        ):
            self.start_value = start_value
        else:
            raise ValueError("Invalid start value length")

        # Set final xor completely or 0000/FFFF
        if isinstance(final_xor, int):
            self.final_xor = array.array("B", [final_xor] * (self.poly_order - 1))
        elif (
            isinstance(final_xor, array.array) and len(final_xor) == self.poly_order - 1
        ):
            self.final_xor = final_xor
        else:
            raise ValueError("Invalid final xor length")

        # Set boolean parameters
        old_reverse = self.reverse_polynomial
        self.reverse_polynomial = reverse_polynomial
        if self.reverse_polynomial != old_reverse:
            self.cache = []
            self.__cache_bits = 8

        self.reverse_all = ref_out
        self.little_endian = little_endian
        self.lsb_first = ref_in

    def set_crc_parameters(self, i):
        # Bit 0,1 = Polynomial
        val = (i >> 0) & 3
        old = self.polynomial
        self.polynomial = self.choose_polynomial(val)
        poly_order = len(self.polynomial)
        if self.polynomial != old:
            self.cache = []
            self.__cache_bits = 8

        # Bit 2 = Start Value
        val = (i >> 2) & 1
        self.start_value = [val != 0] * (poly_order - 1)

        # Bit 3 = Final XOR
        val = (i >> 3) & 1
        self.final_xor = [val != 0] * (poly_order - 1)

        # Bit 4 = Reverse Polynomial
        val = (i >> 4) & 1
        old_reverse = self.reverse_polynomial
        if val == 0:
            self.reverse_polynomial = False
        else:
            self.reverse_polynomial = True
        if self.reverse_polynomial != old_reverse:
            self.cache = []
            self.__cache_bits = 8

        # Bit 5 = Reverse (all) Result
        val = (i >> 5) & 1
        if val == 0:
            self.reverse_all = False
        else:
            self.reverse_all = True

        # Bit 6 = Little Endian
        val = (i >> 6) & 1
        if val == 0:
            self.little_endian = False
        else:
            self.little_endian = True

        # Bit 7 = Least Significant Bit (LSB) first
        val = (i >> 7) & 1
        if val == 0:
            self.lsb_first = False
        else:
            self.lsb_first = True

    @classmethod
    def __initialize_standard_checksums(cls):
        for name in cls.STANDARD_CHECKSUMS:
            polynomial = cls.STANDARD_CHECKSUMS[name]["polynomial"]
            if isinstance(polynomial, str):
                polynomial = array.array("B", [1]) + util.hex2bit(polynomial)
                cls.STANDARD_CHECKSUMS[name]["polynomial"] = polynomial

            n = len(polynomial) - 1
            try:
                start_val = cls.STANDARD_CHECKSUMS[name]["start_value"]
            except KeyError:
                start_val = 0

            if isinstance(start_val, int):
                cls.STANDARD_CHECKSUMS[name]["start_value"] = array.array(
                    "B", [start_val] * n
                )

            try:
                final_xor = cls.STANDARD_CHECKSUMS[name]["final_xor"]
            except KeyError:
                final_xor = 0

            if isinstance(final_xor, int):
                cls.STANDARD_CHECKSUMS[name]["final_xor"] = array.array(
                    "B", [final_xor] * n
                )

    def guess_all(self, bits, trash_max=7, ignore_positions: set = None):
        """

        :param bits:
        :param trash_max:
        :param ignore_positions: columns to ignore (e.g. if already another label on them)
        :return: a CRC object, data_range_start, data_range_end, crc_start, crc_end
        """
        self.__initialize_standard_checksums()

        ignore_positions = set() if ignore_positions is None else ignore_positions
        for i in range(0, trash_max):
            ret = self.guess_standard_parameters_and_datarange(bits, i)
            if ret == (0, 0, 0):
                continue  # nothing found

            crc_start, crc_end = len(bits) - i - ret[0].poly_order + 1, len(bits) - i
            if not any(i in ignore_positions for i in range(crc_start, crc_end)):
                return ret[0], ret[1], ret[2], crc_start, crc_end
        return 0, 0, 0, 0, 0

    def bruteforce_all(self, inpt, trash_max=7):
        polynomial_sizes = [16, 8]
        len_input = len(inpt)
        for s in polynomial_sizes:
            for i in range(len_input - s - trash_max, len_input - s):
                ret = self.bruteforce_parameters_and_data_range(inpt, i)
                if ret != (0, 0, 0):
                    return ret[0], ret[1], ret[2], i, i + s
        return 0, 0, 0, 0, 0

    def guess_standard_parameters(self, inpt, vrfy_crc):
        # Tests all standard parameters and return parameter_value (else False), if a valid CRC could be computed.
        # Note: vfry_crc is included inpt!
        for i in range(0, 2**8):
            self.set_crc_parameters(i)
            if len(vrfy_crc) == self.poly_order and self.crc(inpt) == vrfy_crc:
                return i
        return False

    def guess_standard_parameters_and_datarange(self, inpt, trash):
        """
        Tests standard parameters from dict and return polynomial object, if a valid CRC could be computed
        and determines start and end of crc datarange (end is set before crc)
        Note: vfry_crc is included inpt!
        """
        # Test longer polynomials first, because smaller polynomials have higher risk of false positive
        for name, parameters in sorted(
            self.STANDARD_CHECKSUMS.items(),
            key=lambda x: len(x[1]["polynomial"]),
            reverse=True,
        ):
            self.caption = name
            data_begin, data_end = c_util.get_crc_datarange(
                inpt,
                parameters["polynomial"],
                max(0, len(inpt) - trash - len(parameters["polynomial"])) + 1,
                parameters["start_value"],
                parameters["final_xor"],
                parameters.get("ref_in", False),
                parameters.get("reverse_polynomial", False),
                parameters.get("ref_out", False),
                parameters.get("little_endian", False),
            )
            if (data_begin, data_end) != (0, 0):
                self.set_individual_parameters(**parameters)
                return self, data_begin, data_end
        return 0, 0, 0

    def bruteforce_parameters_and_data_range(self, inpt, vrfy_crc_start):
        # Tests all standard parameters and return parameter_value (else False), if a valid CRC could be computed
        # and determines start and end of crc datarange (end is set before crc)
        # Note: vfry_crc is included inpt!
        for i in range(0, 2**8):
            self.set_crc_parameters(i)
            data_begin, data_end = self.get_crc_datarange(inpt, vrfy_crc_start)
            if (data_begin, data_end) != (0, 0):
                return i, data_begin, data_end
        return 0, 0, 0

    def reverse_engineer_polynomial(self, dataset, crcset):
        # Sets must be of equal size and > 2
        setlen = len(dataset)
        if setlen != len(crcset) or setlen < 3:
            return False

        # XOR each data string with every other string and find strings that only differ in one bit
        one_bitter = []
        one_bitter_crc = []
        for i in range(0, setlen):
            for j in range(i + 1, setlen):
                if len(dataset[i]) == len(dataset[j]) and len(crcset[i]) == len(
                    crcset[j]
                ):
                    count = 0
                    tmp = -1
                    for x in range(0, len(dataset[i])):
                        if dataset[i][x] != dataset[j][x]:
                            tmp = x
                            count += 1
                            if count > 1:
                                break
                    if count == 1:
                        one_bitter.append(tmp)
                        tmp_crc = []
                        for x in range(0, len(crcset[i])):
                            tmp_crc.append(crcset[i][x] ^ crcset[j][x])
                        one_bitter_crc.extend([tmp_crc])

        # Find two CRCs from one bit sequences with position i and i+1. CRC from one bit sequence with position i+1 must have MSB=1
        setlen = len(one_bitter)
        for i in range(0, setlen):
            for j in range(0, setlen):
                if (
                    i != j
                    and one_bitter[i] + 1 == one_bitter[j]
                    and one_bitter_crc[j][0] == True
                ):
                    # Compute Polynomial
                    polynomial = one_bitter_crc[i].copy()
                    for x in range(0, len(one_bitter_crc[i]) - 1):
                        polynomial[x] ^= one_bitter_crc[j][x + 1]
                    return polynomial
        return False

    def to_xml(self):
        root = ET.Element("crc")
        root.set("polynomial", util.convert_bits_to_string(self.polynomial, 0))
        root.set("start_value", util.convert_bits_to_string(self.start_value, 0))
        root.set("final_xor", util.convert_bits_to_string(self.final_xor, 0))
        root.set("ref_in", str(int(self.lsb_first)))
        root.set("ref_out", str(int(self.reverse_all)))
        return root

    @classmethod
    def from_xml(cls, tag: ET.Element):
        polynomial = tag.get("polynomial", "1010")
        start_value = tag.get("start_value", "0000")
        final_xor = tag.get("final_xor", "0000")
        ref_in = bool(int(tag.get("ref_in", "0")))
        ref_out = bool(int(tag.get("ref_out", "0")))
        return GenericCRC(
            polynomial=util.string2bits(polynomial),
            start_value=util.string2bits(start_value),
            final_xor=util.string2bits(final_xor),
            lsb_first=ref_in,
            reverse_all=ref_out,
        )

    @staticmethod
    def bit2str(inpt):
        return "".join(["1" if x else "0" for x in inpt])

    @staticmethod
    def str2bit(inpt):
        return [True if x == "1" else False for x in inpt]

    @staticmethod
    def int2bit(inpt):
        return [True if x == "1" else False for x in "{0:08b}".format(inpt)]

    @staticmethod
    def str2arr(inpt):
        return array.array("B", GenericCRC.str2bit(inpt))

    @staticmethod
    def bit2int(inpt):
        return int(GenericCRC.bit2str(inpt), 2)

    @staticmethod
    def hex2str(inpt):
        bitstring = bin(int(inpt, base=16))[2:]
        return "0" * (4 * len(inpt.lstrip("0x")) - len(bitstring)) + bitstring
