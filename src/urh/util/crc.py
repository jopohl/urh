#!/usr/bin/env python3
__author__ = 'andreas.noack@fh-stralsund.de'


class crc_generic:
    def __init__(self, polynomial="16_standard", start_value=False, final_xor=False, reverse_polynomial=False,
                 reverse_all=False, little_endian=False, lsb_first=False):
        self.polynomial = self.choose_polynomial(polynomial)
        self.poly_order = len(self.polynomial)
        self.reverse_polynomial = reverse_polynomial
        self.reverse_all = reverse_all
        self.little_endian = little_endian
        self.lsb_first = lsb_first

        if not isinstance(start_value, bool):
            if len(start_value) == self.poly_order - 1:
                self.start_value = start_value
            else:
                self.start_value = start_value[0] * (self.poly_order - 1)
        else:
            self.start_value = [start_value] * (self.poly_order - 1)

        if not isinstance(final_xor, bool):
            if len(final_xor) == self.poly_order - 1:
                self.final_xor = final_xor
            else:
                self.final_xor = final_xor[0] * (self.poly_order - 1)
        else:
            self.final_xor = [final_xor] * (self.poly_order - 1)

    def choose_polynomial(self, polynomial):
        if polynomial == "16_standard" or polynomial == 0:
            return [True,
                    True, False, False, False, False, False, False, False,
                    False, False, False, False, False, True, False, True]  # x^16+x^15+x^2+x^0
        elif polynomial == "16_ccitt" or polynomial == 1:
            return [True,
                    False, False, False, True, False, False, False, False,
                    False, False, True, False, False, False, False, True]  # x^16+x^12+x^5+x^0
        elif polynomial == "16_dnp" or polynomial == 2:
            return [True,
                    False, False, True, True, True, True, False, True,
                    False, True, True, False, False, True, False, True]  # x^16+x^13+x^12+x^11+x^10+x^8+x^6+x^5+x^2+x^0
        elif polynomial == "8_en" or polynomial == 3:
            return [True,
                    False, False, False, False, False, True, True, True] # x^8+x^2+x+1
        return polynomial

    def crc(self, inpt):
        data = inpt.copy()
        if not len(data) % 8 == 0:
            data.extend([False] * int(8 - (len(data) % 8)))  # Padding with 0 to multiple of crc-order
        len_data = len(data)

        crc = self.start_value.copy()

        for i in range(0, len_data, 8):
            for j in range(0, 8):

                if self.lsb_first:
                    idx = i + (7 - j)
                else:
                    idx = i + j

                if crc[0] != data[idx]:
                    crc[0:self.poly_order - 2] = crc[1:self.poly_order - 1]  # crc = crc << 1
                    crc[self.poly_order - 2] = False
                    for x in range(0, self.poly_order - 1):
                        if self.reverse_polynomial:
                            crc[x] ^= self.polynomial[self.poly_order - 1 - x]
                        else:
                            crc[x] ^= self.polynomial[x + 1]
                else:
                    crc[0:self.poly_order - 2] = crc[1:self.poly_order - 1]  # crc = crc << 1
                    crc[self.poly_order - 2] = False

        for i in range(0, self.poly_order - 1):
            if self.final_xor[i]:
                crc[i] = not crc[i]

        if self.reverse_all:
            crc_old = []
            for i in range(0, self.poly_order - 1):
                crc_old.append(crc[self.poly_order - 2 - i])
            crc = crc_old

        if self.little_endian:
            if self.poly_order - 1 == 16:
                crc[0:8], crc[8:16] = crc[8:16], crc[0:8]
            elif self.poly_order - 1 == 32:
                crc[0:8], crc[8:16], crc[16:24], crc[24:32] = crc[24:32], crc[16:32], crc[8:16], crc[0:8]
            elif self.poly_order - 1 == 64:
                crc[0:8], crc[8:16], crc[16:24], crc[24:32] = crc[24:32], crc[16:32], crc[8:16], crc[0:8]
                crc[32 + 0:32 + 8], crc[32 + 8:32 + 16], crc[32 + 16:32 + 24], crc[32 + 24:32 + 32] = \
                    crc[32 + 24:32 + 32], crc[32 + 16:32 + 32], crc[32 + 8:32 + 16], crc[32 + 0:32 + 8]

        return crc

    def guess_standard_parameters(self, inpt, vrfy_crc):
        # Test all standard parameters and return true, if a valid CRC could be computed.
        for i in range(0, 2 ** 8):
            # Bit 0,1 = Polynomial
            val = (i >> 0) & 3
            self.polynomial = self.choose_polynomial(val)
            self.poly_order = len(self.polynomial)

            # Bit 2 = Start Value
            val = (i >> 2) & 1
            if val == 0:
                self.start_value = [False] * (self.poly_order - 1)
            else:
                self.start_value = [True] * (self.poly_order - 1)

            # Bit 3 = Final XOR
            val = (i >> 3) & 1
            if val == 0:
                self.final_xor = [False] * (self.poly_order - 1)
            else:
                self.final_xor = [True] * (self.poly_order - 1)

            # Bit 4 = Reverse Polynomial
            val = (i >> 4) & 1
            if val == 0:
                self.reverse_polynomial = False
            else:
                self.reverse_polynomial = True

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

            if self.crc(inpt.copy()) == vrfy_crc:
                return True

        return False

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
                if len(dataset[i]) == len(dataset[j]) and len(crcset[i]) == len(crcset[j]):
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
                if i != j and one_bitter[i] + 1 == one_bitter[j] and one_bitter_crc[j][0] == True:
                    # Compute Polynomial
                    polynomial = one_bitter_crc[i].copy()
                    for x in range(0, len(one_bitter_crc[i]) - 1):
                        polynomial[x] ^= one_bitter_crc[j][x + 1]
                    return polynomial
        return False

    @staticmethod
    def bit2str(inpt, points=False):
        if not points:
            return "".join(["1" if x else "0" for x in inpt])
        else:
            bitstring = ""
            for i in range(0, len(inpt)):
                if i > 0 and i % 4 == 0:
                    bitstring += "."
                if inpt[i]:
                    bitstring += "1"
                else:
                    bitstring += "0"
            return bitstring

    @staticmethod
    def str2bit(inpt):
        return [True if x == "1" else False for x in inpt]

    @staticmethod
    def bit2hex(inpt):
        bitstring = "".join(["1" if x else "0" for x in inpt])
        return hex(int(bitstring, 2))

    @staticmethod
    def hex2bit(inpt):
        bitstring = bin(int(inpt, base=16))[2:]
        return [True if x == "1" else False for x in "0" * (4 * len(inpt.lstrip('0x')) - len(bitstring)) + bitstring]

    @staticmethod
    def hex2str(inpt):
        bitstring = bin(int(inpt, base=16))[2:]
        return "0" * (4 * len(inpt.lstrip('0x')) - len(bitstring)) + bitstring


if __name__ == "__main__":
    c = crc_generic(polynomial="16_standard", start_value=False, final_xor=False,
                    reverse_polynomial=False, reverse_all=False, lsb_first=False, little_endian=False)

    # http://depa.usst.edu.cn/chenjq/www2/software/crc/CRC_Javascript/CRCcalculation.htm
    # CRC-16: polynomial="16_standard", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False
    # CRC-16-CCITT: polynomial="16_ccitt", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False

    # http://www.lammertbies.nl/comm/info/crc-calculation.html <- Fehler
    # CRC-16: polynomial="16_standard", start_value = False, final_xor = False, reverse_polynomial=False, reverse_all=False

    test = False
    if test:
        bitstring_a = "1110001111001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010"
        bitstring_b = "1110010011001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010"
        # bitstring_a="100000000000000000000000"
        # bitstring_b="010000000000000000000000"
        # bitstring_a="001000000000000000000000"
        # bitstring_b="000100000000000000000000"
        bits_a = c.str2bit(bitstring_a)
        bits_b = c.str2bit(bitstring_b)
        crc_a = c.crc(bits_a)
        crc_b = c.crc(bits_b)

        count = [0] * (2 ** 16)
        for i in range(0, 2 ** 16):
            c.start_value = []
            for bits in range(0, 16):
                if (i >> bits) & 1 == 1:
                    c.start_value.append(True)
                else:
                    c.start_value.append(False)
            num = int(c.bit2str(c.crc(bits_a)), 2) ^ int(c.bit2str(crc_a), 2)
            count[num] += 1

            if i % 1000 == 0:
                print(i)

        num = 4
        for i in range(0, 2 ** 16):
            # if count[i] > 1:
            #    num += 2
            # else:
            #    num -= 2
            print(">", hex(i), "Count =", hex(count[i]), "#" * num)

    else:
        bitstring_set = [
            "1110001111001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110010011001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110010111001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010",
            "1110011011001011100010000101010100000010110111000101100010100100111110111101100110110111011001010010001011101010"]
        bitset = []
        crcset = []

        for i in bitstring_set:
            tmp = c.str2bit(i)
            bitset.append(tmp)
            crcset.append(c.crc(tmp))

        # print(c.guess_standard_parameters(bitset[0], crcset[0]))
        polynomial = c.reverse_engineer_polynomial(bitset, crcset)
        if polynomial:
            print("Polynomial =", c.bit2str(polynomial), c.bit2hex(polynomial))
