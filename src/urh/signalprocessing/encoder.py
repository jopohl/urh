import copy

import array

from urh import constants
from urh.util.crc import crc_generic


class Encoder(object):
    """
    Full featured encoding/decoding of protocols.
    """

    class ErrorState:
        SUCCESS = "success"
        WRONG_CRC = "wrong crc"
        PREAMBLE_NOT_FOUND = "preamble not found"
        SYNC_NOT_FOUND = "sync not found"
        EOF_NOT_FOUND = "eof not found"
        WRONG_INPUT = "wrong input"
        MISSING_EXTERNAL_PROGRAM = "Please set external de/encoder program!"
        INVALID_CUTMARK = "cutmark is not valid"
        MISC = "general error"
        WRONG_PARAMETERS = "wrong parameters"

    def __init__(self, chain=None):
        if chain is None:
            chain = []

        self.mode = 0
        self.external_decoder = ""
        self.external_encoder = ""
        self.multiple = 1
        self.src = []  # [[True, True], [True, False], [False, True], [False, False]]
        self.dst = []  # [[False, False], [False, True], [True, False], [True, True]]
        self.carrier = "1_"
        self.cutmark = array.array("B", [True, False])
        self.cutmode = 0  # 0 = before, 1 = after, 2 = before_pos, 3 = after_pos
        self.morse_low = 1
        self.morse_high = 3
        self.morse_wait = 1
        self.__symbol_len = 1

        # Configure CC1101 Date Whitening
        polynomial = array.array("B", [False, False, True, False, False, False, False, True])  # x^5+x^0
        sync_bytes = array.array("B", [True, True, True, False, True, False, False, True, True, True, False, False,
                      True, False, True, False, True, True, True, False, True, False, False, True,
                      True, True, False, False, True, False, True, False])  # "e9cae9ca"
        # sync_bytes = self.str2bit("01100111011010000110011101101000") # "67686768" (RWE Default)
        # sync_bytes = self.str2bit("01101001111101100110100111110111") # "69f669f7" (Special RWE)

        self.data_whitening_polynomial = polynomial  # Set polynomial
        self.data_whitening_sync = sync_bytes  # Sync Bytes
        self.data_whitening_crc = array.array("B", [False] * 16)  # CRC is 16 Bit long
        self.data_whitening_preamble = array.array("B", [True, False] * 16)  # 010101...
        self.lfsr_state = array.array("B", [])

        self.data_whitening_apply_crc = True  # Apply CRC with XOR
        self.data_whitening_preamble_rm = True  # Remove Preamble
        self.data_whitening_sync_rm = True  # Remove Sync Bytes
        self.data_whitening_crc_rm = False  # Remove CRC

        # Get CRC Object
        self.c = crc_generic(polynomial="16_standard", start_value=True)

        # Set Chain
        self.chain = []
        self.set_chain(chain)

    @property
    def symbol_len(self):
        return int(self.__symbol_len)

    @property
    def name(self):
        return self.chain[0]

    @property
    def is_nrz(self) -> bool:
        return len(self.chain) <= 1

    @property
    def is_nrzi(self) -> bool:
        return len(self.chain) == 2 and self.chain[1] == self.code_invert

    @property
    def contains_cut(self) -> bool:
        return self.code_cut in self.chain

    def __str__(self):
        return self.name

    def set_chain(self, names):
        if len(names) < 1:
            return
        self.chain = [names[0]]

        i = 1
        while i < len(names):
            if constants.DECODING_INVERT in names[i]:
                self.chain.append(self.code_invert)
            elif constants.DECODING_ENOCEAN in names[i]:
                self.chain.append(self.code_enocean)
            elif constants.DECODING_DIFFERENTIAL in names[i]:
                self.chain.append(self.code_differential)
            elif constants.DECODING_REDUNDANCY in names[i]:
                self.chain.append(self.code_redundancy)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append(2)
            elif constants.DECODING_DATAWHITENING in names[i]:
                self.chain.append(self.code_data_whitening)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append("0xe9cae9ca;0x21;0x8")  # Default Sync Bytes
            elif constants.DECODING_CARRIER in names[i]:
                self.chain.append(self.code_carrier)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append("1_")
            elif constants.DECODING_BITORDER in names[i]:
                self.chain.append(self.code_lsb_first)
            elif constants.DECODING_EDGE in names[i]:
                self.chain.append(self.code_edge)
            elif constants.DECODING_SUBSTITUTION in names[i]:
                self.chain.append(self.code_substitution)
                i += 1
                if i < len(names):
                    self.chain.append(self.get_subst_array(names[i]))
                else:
                    self.chain.append(self.get_subst_array("0:1;1:0;"))
            elif constants.DECODING_EXTERNAL in names[i]:
                self.chain.append(self.code_externalprogram)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append("./;./")
            elif constants.DECODING_CUT in names[i]:
                self.chain.append(self.code_cut)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append("0;1010")
            elif constants.DECODING_MORSE in names[i]:
                self.chain.append(self.code_morse)
                i += 1
                if i < len(names):
                    self.chain.append(names[i])
                else:
                    self.chain.append("1;3;1")
            i += 1

    def get_chain(self):
        chainstr = [self.name]

        i = 1
        while i < len(self.chain):
            if self.code_invert == self.chain[i]:
                chainstr.append(constants.DECODING_INVERT)
            elif self.code_enocean == self.chain[i]:
                chainstr.append(constants.DECODING_ENOCEAN)
            elif self.code_differential == self.chain[i]:
                chainstr.append(constants.DECODING_DIFFERENTIAL)
            elif self.code_redundancy == self.chain[i]:
                chainstr.append(constants.DECODING_REDUNDANCY)
                i += 1
                chainstr.append(self.chain[i])
            elif self.code_data_whitening == self.chain[i]:
                chainstr.append(constants.DECODING_DATAWHITENING)
                i += 1
                chainstr.append(self.chain[i])
            elif self.code_carrier == self.chain[i]:
                chainstr.append(constants.DECODING_CARRIER)
                i += 1
                chainstr.append(self.chain[i])
            elif self.code_lsb_first == self.chain[i]:
                chainstr.append(constants.DECODING_BITORDER)
            elif self.code_edge == self.chain[i]:
                chainstr.append(constants.DECODING_EDGE)
            elif self.code_substitution == self.chain[i]:
                chainstr.append(constants.DECODING_SUBSTITUTION)
                i += 1
                chainstr.append(self.get_subst_string(self.chain[i]))
            elif self.code_externalprogram == self.chain[i]:
                chainstr.append(constants.DECODING_EXTERNAL)
                i += 1
                chainstr.append(self.chain[i])
            elif self.code_cut == self.chain[i]:
                chainstr.append(constants.DECODING_CUT)
                i += 1
                chainstr.append(self.chain[i])
            elif self.code_morse == self.chain[i]:
                chainstr.append(constants.DECODING_MORSE)
                i += 1
                chainstr.append(self.chain[i])
            i += 1

        return chainstr

    def get_subst_array(self, string):
        src = []
        dst = []
        elements = string.split(";")
        for i in elements:
            if len(i):
                try:
                    tsrc, tdst = i.split(":")
                    src.append(self.str2bit(tsrc))
                    dst.append(self.str2bit(tdst))
                except (ValueError, AttributeError):
                    pass
        return [src, dst]

    def get_subst_string(self, inpt):
        src = inpt[0]
        dst = inpt[1]
        output = ""
        if len(src) == len(dst):
            for i in range(0, len(src)):
                output += self.bit2str(src[i]) + ":" + self.bit2str(dst[i]) + ";"

        return output

    def code(self, decoding, inputbits: array.array):
        temp = array.array("B", inputbits)
        output = temp
        errors = 0
        error_states = []

        # operation order
        if decoding:
            i = 0
            ops = len(self.chain)
            step = 1
        else:
            i = len(self.chain) - 1
            ops = -1
            step = -1

        # do operations
        while i != ops:
            operation = self.chain[i]
            while not callable(operation) and i + step != ops:
                i += step
                operation = self.chain[i]

            # Ops with parameters
            if self.code_redundancy == operation:
                self.multiple = int(self.chain[i + 1])
            elif self.code_carrier == operation:
                self.carrier = self.chain[i + 1]
            elif self.code_substitution == operation:
                self.src = self.chain[i + 1][0]
                self.dst = self.chain[i + 1][1]
            elif self.code_externalprogram == operation:
                if self.chain[i + 1] != "":
                    try:
                        self.external_decoder, self.external_encoder = self.chain[i + 1].split(";")
                    except ValueError:
                        pass
                else:
                    self.external_decoder, self.external_encoder = "", ""
            elif self.code_data_whitening == operation:
                if self.chain[i + 1].count(';') == 2:
                    self.data_whitening_sync, self.data_whitening_polynomial, opt = self.chain[i + 1].split(";")
                    if (len(self.data_whitening_sync) > 0 and len(self.data_whitening_polynomial) > 0) and len(opt) > 0:
                        self.data_whitening_sync = self.hex2bit(self.data_whitening_sync)
                        self.data_whitening_polynomial = self.hex2bit(self.data_whitening_polynomial)
                        opt = self.hex2bit(opt)
                        if len(opt) >= 4:
                            self.data_whitening_apply_crc = opt[0]
                            self.data_whitening_preamble_rm = opt[1]
                            self.data_whitening_sync_rm = opt[2]
                            self.data_whitening_crc_rm = opt[3]
            elif self.code_cut == operation:
                if self.chain[i + 1] != "" and self.chain[i + 1].count(';') == 1:
                    self.cutmode, tmp = self.chain[i + 1].split(";")
                    self.cutmode = int(self.cutmode)
                    if self.cutmode < 0 or self.cutmode > 3:
                        self.cutmode = 0
                    if self.cutmode == 0 or self.cutmode == 1:
                        self.cutmark = self.str2bit(tmp)
                        if len(self.cutmark) == 0: self.cutmark = array.array("B", [True, False, True, False])
                    else:
                        try:
                            self.cutmark = int(tmp)
                        except ValueError:
                            self.cutmark = 1
            elif self.code_morse == operation:
                if self.chain[i + 1] != "" and self.chain[i + 1].count(';') == 2:
                    try:
                        l, h, w = self.chain[i + 1].split(";")
                        self.morse_low = int(l)
                        self.morse_high = int(h)
                        self.morse_wait = int(w)
                    except ValueError:
                        self.morse_low, self.morse_high, self.morse_wait = (1, 3, 1)

            # Execute Ops
            if callable(operation) and len(temp) > 0:
                output, temp_errors, state = operation(decoding, temp)
                errors += temp_errors
                if state != self.ErrorState.SUCCESS and state not in error_states:
                    error_states.append(state)

            # Loop Footer
            i += step
            temp = output

        if len(inputbits):
            self.__symbol_len = len(output) / len(inputbits)

        if error_states:
            error_state = error_states[0]
        else:
            error_state = self.ErrorState.SUCCESS

        return output, errors, error_state

    def lfsr(self, clock):
        poly = array.array("B", [False])
        poly.extend(self.data_whitening_polynomial)
        len_pol = len(poly)

        if len(self.lfsr_state) == 0:
            self.lfsr_state.extend([True] * len_pol)
        for i in range(0, clock):
            # Determine first bit with polynomial
            first_bit = -1
            for j in range(len_pol - 1, 0, -1):
                if poly[j] and self.lfsr_state[j]:
                    if first_bit == -1:
                        first_bit = True
                    else:
                        first_bit = not first_bit
            if first_bit == -1:
                first_bit = False
            # Clock
            for j in range(len_pol - 1, 0, -1):
                self.lfsr_state[j] = self.lfsr_state[j - 1]
            self.lfsr_state[0] = first_bit
        return self.lfsr_state[1:len_pol]

    def apply_data_whitening(self, decoding, inpt):
        len_sync = len(self.data_whitening_sync)
        len_polynomial = len(self.data_whitening_polynomial)
        inpt_from = 0
        inpt_to = len(inpt)

        # Crop last bit, if duplicate
        if decoding and inpt_to > 1:
            if inpt[-1] == inpt[-2]:
                inpt_to -= 1

        # inpt empty, polynomial or syncbytes are zero! (Shouldn't happen)
        if inpt_to < 1 or len_polynomial < 1 or len_sync < 1:
            return inpt[inpt_from:inpt_to], 0, self.ErrorState.MISC  # Misc Error

        # Search for whitening start position (after sync bytes)
        whitening_start_pos = inpt_from
        i = inpt_from
        while i < (inpt_to - len_sync):
            equalbits = 0
            for j in range(0, len_sync):
                if inpt[i + j] == self.data_whitening_sync[j]:
                    equalbits += 1
                else:
                    continue
            if len_sync == equalbits:
                whitening_start_pos = i + j + 1
                break
            else:
                i += 1
        # Sync not found
        if decoding and whitening_start_pos == inpt_from:
            return inpt[inpt_from:inpt_to], 0, self.ErrorState.SYNC_NOT_FOUND

        # If encoding and crc_rm is active, extend inpt with 0s
        if not decoding and self.data_whitening_crc_rm:
            inpt = inpt + self.data_whitening_crc
            inpt_to += len(self.data_whitening_crc)

        # Prepare keystream
        self.lfsr_state = array.array("B", [])
        keystream = self.lfsr(0)
        for i in range(whitening_start_pos, inpt_to, 8):
            keystream.extend(self.lfsr(8))

        # If data whitening polynomial is wrong, keystream can be less than needed. Check and exit.
        if len(keystream) < inpt_to - whitening_start_pos:
            return inpt[inpt_from:inpt_to], 0, self.ErrorState.MISC  # Error 31338

        # Apply keystream (xor) - Decoding
        if decoding:
            for i in range(whitening_start_pos, inpt_to):
                inpt[i] ^= keystream[i - whitening_start_pos]

        # Apply CRC-16
        if self.data_whitening_apply_crc:
            # Calculate CRC-16:
            if not decoding and self.data_whitening_crc_rm:
                crc = self.c.crc(inpt[whitening_start_pos:inpt_to])
            else:
                crc = self.c.crc(inpt[whitening_start_pos:inpt_to - len(self.data_whitening_crc)])
            # XOR calculated CRC to original CRC -> Zero if no errors
            for i in range(0, 16):
                inpt[inpt_to - len(self.data_whitening_crc) + i] ^= crc[i]

        # Apply keystream (xor) - Decoding
        if not decoding:
            for i in range(whitening_start_pos, inpt_to):
                inpt[i] ^= keystream[i - whitening_start_pos]

        # Remove preamble/sync bytes/crc
        if decoding:
            if self.data_whitening_preamble_rm:
                inpt_from += whitening_start_pos - len_sync
            if self.data_whitening_sync_rm:
                inpt_from += len_sync
            if self.data_whitening_crc_rm:
                inpt_to -= len(self.data_whitening_crc)
        else:
            if self.data_whitening_sync_rm:
                inpt = self.data_whitening_sync + inpt
                inpt_to += len(self.data_whitening_sync)
            if self.data_whitening_preamble_rm:
                inpt = self.data_whitening_preamble + inpt
                inpt_to += len(self.data_whitening_preamble)
            # Duplicate last bit when encoding
            inpt += array.array("B", [inpt[-1]])
            inpt_to += 1

        return inpt[inpt_from:inpt_to], 0, self.ErrorState.SUCCESS

    def run_command(self, command, param):
        # add shlex.quote(param) later for security reasons
        # print(command, param)
        try:
            import subprocess
            p = subprocess.Popen([command + " " + param],
                                 shell=True,
                                 # stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE)
            out, _ = p.communicate(param.encode())
            return out.decode()
        except:
            print("Error running", command, param)
            return ""

    def code_carrier(self, decoding, inpt):
        output = array.array("B", [])
        errors = 0

        if decoding:
            # Remove carrier if decoding
            if len(self.carrier) > 0:
                for x in range(0, len(inpt)):
                    tmp = self.carrier[x % len(self.carrier)]
                    if tmp not in ("0", "1", "*"):  # Data!
                        output.append(inpt[x])
                    else:  # Carrier -> 0, 1, *
                        if tmp in ("0", "1"):
                            if (inpt[x] and tmp != "1") or (not inpt[x] and tmp != "0"):
                                errors += 1
        else:
            # Add carrier if encoding
            if len(self.carrier) > 0:
                x = 0
                for i in inpt:
                    tmp = self.carrier[x % len(self.carrier)]
                    if not tmp in ("0", "1", "*"):
                        output.append(i)
                        x += 1
                    while self.carrier[x % len(self.carrier)] in ("0", "1", "*"):
                        output.append(False if self.carrier[x % len(self.carrier)] in (
                        "0", "*") else True)  # Add 0 when there is a wildcard (*) in carrier description
                        x += 1
        return output, errors, self.ErrorState.SUCCESS

    def code_data_whitening(self, decoding, inpt):
        """
        XOR Data Whitening
        :param decoding:
        :param inpt:
        :return:
        """
        return self.apply_data_whitening(decoding, inpt)

    def code_lsb_first(self, decoding, inpt):
        output = array.array("B", inpt)
        errors = len(inpt) % 8

        # Change Byteorder to LSB first <-> LSB last
        i = 0
        while i < len(output) - 7:
            output[i + 0], output[i + 1], output[i + 2], output[i + 3], output[i + 4], output[i + 5], output[i + 6], \
            output[i + 7] = \
                output[i + 7], output[i + 6], output[i + 5], output[i + 4], output[i + 3], output[i + 2], output[i + 1], \
                output[i + 0]
            i += 8
        return output, errors, self.ErrorState.SUCCESS

    def code_redundancy(self, decoding, inpt):
        output = array.array("B", [])
        errors = 0

        if len(inpt) and self.multiple > 1:
            if decoding:
                # Remove multiple
                count = 0
                what = -1
                for i in inpt:
                    if i:
                        if not what:
                            if count > 0:
                                errors += 1
                            count = 0
                        what = True
                        count += 1
                        if count >= self.multiple:
                            output.append(True)
                            count = 0
                    else:
                        if what:
                            if count > 0:
                                errors += 1
                            count = 0
                        what = False
                        count += 1
                        if count >= self.multiple:
                            output.append(False)
                            count = 0
            else:
                # Add multiple
                for i in inpt:
                    output.extend([i] * self.multiple)
        return output, errors, self.ErrorState.SUCCESS

    def code_invert(self, decoding, inpt):
        errors = 0
        return array.array("B", [True if not x else False for x in inpt]), errors, self.ErrorState.SUCCESS

    def code_differential(self, decoding, inpt):
        output = array.array("B", [inpt[0]])
        errors = 0

        if decoding:
            # Remove differential from inpt stream
            i = 1
            while i < len(inpt):
                if inpt[i] != inpt[i - 1]:
                    output.append(True)
                else:
                    output.append(False)
                i += 1
        else:
            # Add differential encoding to output stream
            i = 1
            while i < len(inpt):
                if not inpt[i]:
                    output.append(output[i - 1])
                else:
                    if not output[i - 1]:
                        output.append(True)
                    else:
                        output.append(False)
                i += 1
        return output, errors, self.ErrorState.SUCCESS

    def code_edge(self, decoding, inpt):
        errors = 0
        output = array.array("B", [])

        if decoding:
            i = 1
            while i < len(inpt):
                if inpt[i] == inpt[i - 1]:
                    errors += 1
                    i += 1
                    continue
                output.append(inpt[i])
                i += 2
        else:
            for i in inpt:
                if not i:
                    output.extend([True, False])
                else:
                    output.extend([False, True])
        return output, errors, self.ErrorState.SUCCESS

    def code_substitution(self, decoding, inpt):
        padded_inpt = copy.copy(inpt)
        output = array.array("B", [])

        # Every element in src has to have the same size
        src = self.src
        dst = self.dst

        if len(src) < 1 or len(dst) < 1:
            return [], 1, self.ErrorState.WRONG_INPUT

        if not decoding:
            src, dst = dst, src

        # Padding of inpt with zeros to multiple of SRC[0] length (every SRC/DST-length should be the same)
        minimum_item_size = len(src[0])
        zero_padding = (minimum_item_size - (len(padded_inpt) % minimum_item_size)) % minimum_item_size
        padded_inpt.extend([False]*zero_padding)
        errors = zero_padding

        i = 0
        while i < len(padded_inpt):
            cnt = src.count(padded_inpt[i:i + minimum_item_size])
            if cnt == 1:
                output.extend(dst[src.index(padded_inpt[i:i + minimum_item_size])])
            elif cnt < 1:
                output.extend(padded_inpt[i:i + 1])
                i += 1
                errors += 1
                continue
            i += minimum_item_size

        return output, errors, self.ErrorState.SUCCESS

    def code_morse(self, decoding, inpt):
        errors = 0
        output = array.array("B", [])

        if self.morse_low >= self.morse_high:
            return inpt, 1, self.ErrorState.WRONG_PARAMETERS

        i = 0
        if decoding:
            cnt = 0
            while i < len(inpt):
                if inpt[i] and i < len(inpt) - 1:
                    cnt += 1
                else:
                    # Consider last value
                    if i == len(inpt) - 1:
                        cnt += 1

                    # Evaluate sequence whenever we get a zero
                    if cnt >= self.morse_high:
                        output.append(True)
                    elif cnt > 0 and cnt <= self.morse_low:
                        output.append(False)
                    else:
                        if cnt > 0:
                            if cnt > (self.morse_high+self.morse_low // 2):
                                output.append(True)
                            else:
                                output.append(False)
                            errors += 1
                    cnt = 0
                i += 1
        else:
            while i < len(inpt):
                output.extend([False] * self.morse_wait)
                if inpt[i]:
                    output.extend([True] * self.morse_high)
                else:
                    output.extend([True] * self.morse_low)
                i += 1
            output.extend([False] * self.morse_wait)

        return output, errors, self.ErrorState.SUCCESS

    def code_externalprogram(self, decoding, inpt):
        errors = 0

        if decoding and self.external_decoder != "":
            output = self.charstr2bit(self.run_command(self.external_decoder, self.bit2str(inpt)))
        elif not decoding and self.external_encoder != "":
            output = self.charstr2bit(self.run_command(self.external_encoder, self.bit2str(inpt)))
        else:
            return [], 1, self.ErrorState.MISSING_EXTERNAL_PROGRAM

        return output, errors, self.ErrorState.SUCCESS

    def code_cut(self, decoding, inpt) -> array.array:
        errors = 0
        state = self.ErrorState.SUCCESS
        output = array.array("B", [])

        # cutmark -> [True, False]
        # cutmode -> 0 = before, 1 = after, 2 = before_pos, 3 = after_pos

        pos = -1
        if decoding:
            # Search for cutmark and save to pos
            if self.cutmode == 0 or self.cutmode == 1:
                len_cutmark = len(self.cutmark)
                if len_cutmark < 1:
                    # Cutmark is not valid
                    return inpt, 0, self.ErrorState.INVALID_CUTMARK

                for i in range(0, len(inpt) - len_cutmark):
                    if all(inpt[i + j] == self.cutmark[j] for j in range(len_cutmark)):
                        pos = i
                        break
            else:
                pos = int(self.cutmark)

            if 0 <= pos < len(inpt):
                # Delete before
                if self.cutmode == 0 or self.cutmode == 2:
                    output.extend(inpt[pos:])
                else:
                    # Delete after
                    if self.cutmode == 1:
                        pos += len(self.cutmark)
                    else:
                        pos += 1
                    output.extend(inpt[:pos])
            else:
                # Position not found or not in range, do nothing!
                state = self.ErrorState.PREAMBLE_NOT_FOUND
                output.extend(inpt)
        else:
            # Can't undo removing information :-(
            output.extend(inpt)
        return output, errors, state

    def enocean_hash(self, msg):
        """
        Get the hash for an enocean message. There are three hashes possible:
        1) 4 Bit Hash - For Switch Telegram (RORG=5 or 6 and STATUS = 0x20 or 0x30)
        2) 8 Bit Checksum: STATUS bit 2^7 = 0
        3) 8 Bit CRC: STATUS bit 2^7 = 1

        :param msg: the message without Preamble/SOF and EOF. Message starts with RORG and ends with CRC
        :type msg: list of bool
        :rtype: list of bool
        """
        try:
            if msg[0:4] == self.hex2bit("5") or msg[0:4] == self.hex2bit("6"):
                # Switch telegram
                return self.enocean_checksum4(msg)

            status = msg[-16:-8]
            if status[0]:
                return self.enocean_crc8(msg[:-8])  # ignore trailing hash
            else:
                return self.enocean_checksum8(msg[:-8])  # ignore trailing hash

        except IndexError:
            return None

    @staticmethod
    def enocean_checksum4(inpt) -> array.array:
        hash = 0
        val = copy.copy(inpt)
        val[-4:] = array.array("B", [False, False, False, False])
        for i in range(0, len(val), 8):
            hash += int("".join(map(str, map(int, val[i:i + 8]))), 2)
        hash = (((hash & 0xf0) >> 4) + (hash & 0x0f)) & 0x0f
        return array.array("B", list(map(bool, map(int, "{0:04b}".format(hash)))))

    @staticmethod
    def enocean_checksum8(inpt) -> array.array:
        hash = 0
        for i in range(0, len(inpt) - 8, 8):
            hash += int("".join(map(str, map(int, inpt[i:i + 8]))), 2)
        return array.array("B", list(map(bool, map(int, "{0:08b}".format(hash % 256)))))

    @staticmethod
    def enocean_crc8(inpt):
        c = crc_generic(polynomial="8_en")
        return array.array("B", c.crc(inpt))

    def code_enocean(self, decoding: bool, inpt):
        errors = 0
        output = array.array("B", [])
        preamble = array.array("B", [True, False, True, False, True, False, True, False])
        sof = array.array("B", [True, False, False, True])
        eof = array.array("B", [True, False, True, True])

        if decoding:
            inpt, _, _ = self.code_invert(True, inpt)  # Invert
            # Insert a leading 1, to ensure protocol starts with 1
            # The first 1 (inverted) of EnOcean is so weak, that it often drowns in noise
            inpt.insert(0, True)

        # search for begin
        try:
            n = inpt.index(False) - 1
        except ValueError:
            return inpt, 0, self.ErrorState.PREAMBLE_NOT_FOUND

        # check preamble
        if inpt[n:n + 8] != preamble:
            return inpt, 0, self.ErrorState.PREAMBLE_NOT_FOUND

        # check SoF
        if inpt[n + 8:n + 12] != sof:
            return inpt, 0, self.ErrorState.SYNC_NOT_FOUND

        output.extend(inpt[n:n + 12])

        # search for data limits
        start = n + 12
        n = len(inpt)
        while n > start and inpt[n - 4:n] != eof:
            n -= 1
        end = n - 4

        state = self.ErrorState.SUCCESS

        if decoding:
            try:
                for n in range(start, end, 12):
                    errors += sum([inpt[n + 2] == inpt[n + 3], inpt[n + 6] == inpt[n + 7]])
                    errors += sum([inpt[n + 10] != False, inpt[n + 11] != True]) if n < end - 11 else 0
                    output.extend([inpt[n], inpt[n + 1], inpt[n + 2], inpt[n + 4], inpt[n + 5], inpt[n + 6], inpt[n + 8],
                                   inpt[n + 9]])
            except IndexError: # compatibility for old project files
                return inpt, 0, self.ErrorState.MISC

            enocean_hash = self.enocean_hash(output[12:])
            if enocean_hash is None or output[-len(enocean_hash):] != enocean_hash:
                state = self.ErrorState.WRONG_CRC

            # Finalize output
            output.extend(inpt[end:end + 4])

        else:
            # Calculate hash
            enocean_hash = self.enocean_hash(inpt[start:end])
            if enocean_hash is not None:
                inpt[end - len(enocean_hash):end] = enocean_hash
            else:
                state = self.ErrorState.WRONG_CRC

            for n in range(start, end, 8):
                output.extend(
                    [inpt[n], inpt[n + 1], inpt[n + 2], not inpt[n + 2], inpt[n + 3], inpt[n + 4], inpt[n + 5],
                     not inpt[n + 5], inpt[n + 6], inpt[n + 7]])
                if n < len(inpt) - 15:
                    output.extend([False, True])

            # Extend eof and trash
            output.extend(eof)
            output.append(True)

            # Invert
            output, _, _ = self.code_invert(True, output)  # Invert

        return output, errors, state

    def encode(self, inpt):
        return self.code(False, inpt)[0]

    def decode(self, inpt):
        return self.code(True, inpt)[0]

    def applies_for_message(self, msg: array.array) -> bool:
        bit_errors, state = self.analyze(msg)
        return bit_errors == 0 and state == self.ErrorState.SUCCESS

    def analyze(self, inpt):
        """
        return number of bit errors and state
        :param inpt: array.array
        :rtype: tuple[int, str]
        """
        return self.code(True, inpt)[1:3]

    @staticmethod
    def bit2str(inpt):
        return "".join(map(str, inpt))

    @staticmethod
    def str2bit(inpt: str):
        return array.array("B", map(int, inpt))

    @staticmethod
    def charstr2bit(inpt: str):
        output = array.array("B", [])
        for i in inpt:
            if i == '0':
                output.append(False)
            elif i == '1':
                output.append(True)
        return output

    @staticmethod
    def bit2hex(inpt):
        try:
            bitstring = "".join(["1" if x else "0" for x in inpt])
            # Better alignment
            if len(bitstring) % 4 != 0:
                bitstring += "0" * (4 - (len(bitstring) % 4))
            return hex(int(bitstring, 2))
        except (TypeError, ValueError) as e:
            pass
        return ""

    @staticmethod
    def hex2bit(inpt: str) -> array:
        if not isinstance(inpt, str):
            return array.array("B", [])
        try:
            bitstring = bin(int(inpt, base=16))[2:]
            if len(bitstring) % 4 != 0:
                bitstring = "0" * (4 - (len(bitstring) % 4)) + bitstring
            return array.array("B", [True if x == "1" else False for x in bitstring])
        except (TypeError, ValueError) as e:
            pass
        return array.array("B", [])

    @staticmethod
    def hex2str(inpt):
        bitstring = bin(int(inpt, base=16))[2:]
        return "0" * (4 * len(inpt.lstrip('0x')) - len(bitstring)) + bitstring

    def __eq__(self, other):
        if other is None:
            return False

        return self.get_chain() == other.get_chain()
