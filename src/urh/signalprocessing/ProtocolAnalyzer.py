import array
import copy
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, Qt

from urh import constants
from urh.awre.FormatFinder import FormatFinder
from urh.cythonext import signal_functions, util
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.Signal import Signal
from urh.util import util as urh_util
from urh.util.Logger import logger


class ProtocolAnalyzerSignals(QObject):
    protocol_updated = pyqtSignal()
    show_state_changed = pyqtSignal()
    sniff_device_errors_changed = pyqtSignal(str)
    line_duplicated = pyqtSignal()
    fuzzing_started = pyqtSignal(int)
    current_fuzzing_message_changed = pyqtSignal(int)
    fuzzing_finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)


class ProtocolAnalyzer(object):
    """
    The ProtocolAnalyzer is what you would refer to as "protocol".
    The data is stored in the messages variable.
    This class offers several methods for protocol analysis.
    """

    def __init__(self, signal: Signal or None, filename=None):
        self.messages = []  # type: list[Message]
        self.signal = signal
        if filename is None:
            self.filename = self.signal.filename if self.signal is not None else ""
        else:
            assert signal is None
            self.filename = filename

        self.__name = urh_util.get_name_from_filename(filename)  # Fallback if Signal has no Name

        self.show = Qt.Checked  # Show in Compare Frame?
        self.qt_signals = ProtocolAnalyzerSignals()

        self.decoder = Encoding(["Non Return To Zero (NRZ)"])  # For Default Encoding of Protocol

        self.message_types = [MessageType("Default")]

    @property
    def default_message_type(self) -> MessageType:
        if len(self.message_types) == 0:
            self.message_types.append(MessageType("Default"))

        return self.message_types[0]

    @default_message_type.setter
    def default_message_type(self, val: MessageType):
        if len(self.message_types) > 0:
            self.message_types[0] = val
        else:
            self.message_types.append(val)

    @property
    def protocol_labels(self):
        """

        :rtype: list of ProtocolLabel
        """
        return [lbl for message_type in self.message_types for lbl in message_type]

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "qt_signals" and k != "signal":
                setattr(result, k, copy.deepcopy(v, memo))
        result.signal = self.signal
        result.qt_signals = ProtocolAnalyzerSignals()
        return result

    @property
    def name(self):
        name = self.signal.name if self.signal is not None else self.__name
        return name

    @name.setter
    def name(self, val: str):
        if self.signal is None:
            self.__name = val
        else:
            self.signal.name = val

    @property
    def pauses(self):
        return [msg.pause for msg in self.messages]

    @property
    def plain_bits_str(self):
        return [str(msg) for msg in self.messages]

    @property
    def plain_hex_str(self):
        return [msg.plain_hex_str for msg in self.messages]

    @property
    def plain_ascii_str(self):
        return [msg.plain_ascii_str for msg in self.messages]

    @property
    def decoded_proto_bits_str(self):
        """

        :rtype: list of str
        """
        return [msg.decoded_bits_str for msg in self.messages]

    @property
    def decoded_hex_str(self):
        """

        :rtype: list of str
        """
        return [msg.decoded_hex_str for msg in self.messages]

    @property
    def decoded_ascii_str(self):
        """

        :rtype: list of str
        """
        return [msg.decoded_ascii_str for msg in self.messages]

    @property
    def num_messages(self):
        return len([msg for msg in self.messages if msg])

    def clear_decoded_bits(self):
        [msg.clear_decoded_bits() for msg in self.messages]

    def decoded_to_str_list(self, view_type):
        if view_type == 0:
            return self.decoded_proto_bits_str
        elif view_type == 1:
            return self.decoded_hex_str
        elif view_type == 2:
            return self.decoded_ascii_str

    def plain_to_string(self, view: int, show_pauses=True) -> str:
        """

        :param view: 0 - Bits ## 1 - Hex ## 2 - ASCII
        """
        time = constants.SETTINGS.value('show_pause_as_time', type=bool)
        if show_pauses and time and self.signal:
            srate = self.signal.sample_rate
        else:
            srate = None

        return '\n'.join(msg.view_to_string(view, False, show_pauses,
                                            sample_rate=srate
                                            ) for msg in self.messages)

    def plain_to_html(self, view, show_pauses=True) -> str:
        time = constants.SETTINGS.value('show_pause_as_time', type=bool)
        if show_pauses and time and self.signal:
            srate = self.signal.sample_rate
        else:
            srate = None

        result = []
        for message in self.messages:
            cur_str = ""
            if message.participant:
                color = constants.PARTICIPANT_COLORS[message.participant.color_index]
                red, green, blue = color.red(), color.green(), color.blue()
                fgcolor = "#000000" if (red * 0.299 + green * 0.587 + blue * 0.114) > 186 else "#ffffff"
                cur_str += '<span style="background-color: rgb({0},{1},{2}); color: {3}">'.format(red, green, blue,
                                                                                                  fgcolor)

                # cur_str += '<span style="color: rgb({0},{1},{2})">'.format(red, green, blue)

            cur_str += message.view_to_string(view=view, decoded=False, show_pauses=False, sample_rate=srate)

            if message.participant:
                cur_str += '</span>'

            cur_str += message.get_pause_str(sample_rate=srate)
            result.append(cur_str)

        return "<br>".join(result)

    def set_decoder_for_messages(self, decoder: Encoding, messages=None):
        messages = messages if messages is not None else self.messages
        self.decoder = decoder
        for message in messages:
            message.decoder = decoder

    def get_protocol_from_signal(self):
        signal = self.signal
        if signal is None:
            self.messages = None
            return

        if self.messages is not None:
            self.messages[:] = []
        else:
            self.messages = []

        bit_len = signal.bit_len

        ppseq = signal_functions.grab_pulse_lens(signal.qad, signal.qad_center, signal.tolerance,
                                                signal.modulation_type, signal.bit_len)

        bit_data, pauses, bit_sample_pos = self._ppseq_to_bits(ppseq, bit_len, pause_threshold=signal.pause_threshold)
        if signal.message_length_divisor > 1 and signal.modulation_type_str == "ASK":
            self.__ensure_message_length_multiple(bit_data, signal.bit_len, pauses, bit_sample_pos,
                                                  signal.message_length_divisor)

        i = 0
        for bits, pause in zip(bit_data, pauses):
            middle_bit_pos = bit_sample_pos[i][int(len(bits) / 2)]
            start, end = middle_bit_pos, middle_bit_pos + bit_len
            rssi = np.mean(np.abs(signal.data[start:end]))
            message = Message(bits, pause, message_type=self.default_message_type,
                              bit_len=bit_len, rssi=rssi, decoder=self.decoder, bit_sample_pos=bit_sample_pos[i])
            self.messages.append(message)
            i += 1

        self.qt_signals.protocol_updated.emit()

    @staticmethod
    def __ensure_message_length_multiple(bit_data, bit_len: int, pauses, bit_sample_pos, divisor: int):
        """
        In case of ASK modulation, this method tries to use pauses after messages as zero bits so that
        the bit lengths of messages are divisible by divisor
        :param bit_data: List of bit arrays
        :param bit_len: Bit length that was used for demodulation
        :param pauses: List of pauses
        :param bit_sample_pos: List of Array of bit sample positions
        :param divisor: Divisor the messages should be divisible by
        """
        for i in range(len(bit_data)):
            missing_bits = (divisor - (len(bit_data[i]) % divisor)) % divisor
            if missing_bits > 0 and pauses[i] >= bit_len * missing_bits:
                bit_data[i].extend([0] * missing_bits)
                pauses[i] = pauses[i] - missing_bits * bit_len

                try:
                    bit_sample_pos[i][-1] = bit_sample_pos[i][-2] + bit_len
                except IndexError as e:
                    logger.warning("Error padding message " + str(e))
                    continue

                bit_sample_pos[i].extend([bit_sample_pos[i][-1] + (k + 1) * bit_len for k in range(missing_bits - 1)])
                bit_sample_pos[i].append(bit_sample_pos[i][-1] + pauses[i])

    def _ppseq_to_bits(self, ppseq, bit_len: int, write_bit_sample_pos=True, pause_threshold=8):
        bit_sampl_pos = array.array("L", [])
        bit_sample_positions = []

        data_bits = array.array("B", [])
        resulting_data_bits = []
        pauses = array.array("L", [])
        start = 0
        total_samples = 0

        pause_type = 42
        zero_pulse_type = 0
        one_pulse_type = 1

        there_was_data = False

        if len(ppseq) > 0 and ppseq[0, 0] == pause_type:
            start = 1  # Starts with Pause
            total_samples = ppseq[0, 1]

        for i in range(start, len(ppseq)):
            cur_pulse_type = ppseq[i, 0]
            num_samples = ppseq[i, 1]
            num_bits_floated = num_samples / bit_len
            num_bits = int(num_bits_floated)
            decimal_place = num_bits_floated - num_bits

            if decimal_place > 0.5:
                num_bits += 1

            if cur_pulse_type == pause_type:
                # OOK
                if num_bits <= pause_threshold or pause_threshold == 0:
                    data_bits.extend([False] * num_bits)
                    if write_bit_sample_pos:
                        bit_sampl_pos.extend([total_samples + k * bit_len for k in range(num_bits)])

                elif not there_was_data:
                    # Ignore this pause, if there were no information
                    # transmitted previously
                    data_bits[:] = array.array("B", [])
                    bit_sampl_pos[:] = array.array("L", [])

                else:
                    if write_bit_sample_pos:
                        bit_sampl_pos.append(total_samples)
                        bit_sampl_pos.append(total_samples + num_samples)
                        bit_sample_positions.append(bit_sampl_pos[:])
                        bit_sampl_pos[:] = array.array("L", [])

                    resulting_data_bits.append(data_bits[:])
                    data_bits[:] = array.array("B", [])
                    pauses.append(num_samples)
                    there_was_data = False

            elif cur_pulse_type == zero_pulse_type:
                data_bits.extend([False] * num_bits)
                if write_bit_sample_pos:
                    bit_sampl_pos.extend([total_samples + k * bit_len for k in range(num_bits)])

            elif cur_pulse_type == one_pulse_type:
                if not there_was_data:
                    there_was_data = num_bits > 0
                data_bits.extend([True] * num_bits)
                if write_bit_sample_pos:
                    bit_sampl_pos.extend([total_samples + k * bit_len for k in range(num_bits)])

            total_samples += num_samples

        if there_was_data:
            resulting_data_bits.append(data_bits[:])
            if write_bit_sample_pos:
                bit_sample_positions.append(bit_sampl_pos[:] + array.array("L", [total_samples]))
            pause = ppseq[-1, 1] if ppseq[-1, 0] == pause_type else 0
            pauses.append(pause)

        return resulting_data_bits, pauses, bit_sample_positions

    def get_samplepos_of_bitseq(self, start_message: int, start_index: int, end_message: int, end_index: int,
                                include_pause: bool):
        """
        Determine on which place (regarding samples) a bit sequence is
        :rtype: tuple[int,int]
        """
        try:
            if start_message > end_message:
                start_message, end_message = end_message, start_message

            if start_index >= len(self.messages[start_message].bit_sample_pos) - 1:
                start_index = len(self.messages[start_message].bit_sample_pos) - 1
                if not include_pause:
                    start_index -= 1

            if end_index >= len(self.messages[end_message].bit_sample_pos) - 1:
                end_index = len(self.messages[end_message].bit_sample_pos) - 1
                if not include_pause:
                    end_index -= 1

            start = self.messages[start_message].bit_sample_pos[start_index]
            num_samples = self.messages[end_message].bit_sample_pos[end_index] - start

            return start, num_samples
        except (KeyError, IndexError):
            return -1, -1

    def get_bitseq_from_selection(self, selection_start: int, selection_width: int):
        """
        get start and end index of bit sequence from selected samples

        :rtype: tuple[int,int,int,int]
        :return: start_message index, start index, end message index, end index
        """
        start_message, start_index, end_message, end_index = -1, -1, -1, -1
        if not self.messages or not self.messages[0].bit_sample_pos:
            return start_message, start_index, end_message, end_index

        if selection_start + selection_width < self.messages[0].bit_sample_pos[0]:
            return start_message, start_index, end_message, end_index

        for i, msg in enumerate(self.messages):
            msg_sample_pos = msg.bit_sample_pos
            if msg_sample_pos[-2] < selection_start:
                continue
            elif start_message == -1:
                start_message = i
                for j, sample_pos in enumerate(msg_sample_pos):
                    if sample_pos < selection_start:
                        continue
                    elif start_index == -1:
                        start_index = j
                        if msg_sample_pos[-1] - selection_start < selection_width:
                            break
                    elif sample_pos - selection_start > selection_width:
                        return start_message, start_index, i, j
            elif msg_sample_pos[-1] - selection_start < selection_width:
                continue
            else:
                for j, sample_pos in enumerate(msg_sample_pos):
                    if sample_pos - selection_start > selection_width:
                        return start_message, start_index, i, j

        last_message = len(self.messages) - 1
        last_index = len(self.messages[-1].plain_bits) + 1
        return start_message, start_index, last_message, last_index

    def delete_messages(self, msg_start: int, msg_end: int, start: int, end: int, view: int, decoded: bool,
                        update_label_ranges=True):
        removable_msg_indices = []

        for i in range(msg_start, msg_end + 1):
            try:
                bs, be = self.convert_range(start, end, view, 0, decoded, message_indx=i)
                self.messages[i].clear_decoded_bits()
                if update_label_ranges:
                    del self.messages[i][bs:be + 1]
                else:
                    self.messages[i].delete_range_without_label_range_update(bs, be + 1)
                if len(self.messages[i]) == 0:
                    removable_msg_indices.append(i)
            except IndexError:
                continue

        # Remove empty messages and Pause after empty message
        for i in reversed(removable_msg_indices):
            del self.messages[i]

        return removable_msg_indices

    def convert_index(self, index: int, from_view: int, to_view: int, decoded: bool, message_indx=-1) -> tuple:
        """
        Konvertiert einen Index aus der einen Sicht (z.B. Bit) in eine andere (z.B. Hex)

        :param message_indx: if -1, the message with max length is chosen
        :return:
        """
        if len(self.messages) == 0:
            return 0, 0

        if message_indx == -1:
            message_indx = self.messages.index(max(self.messages, key=len))  # Longest message

        if message_indx >= len(self.messages):
            message_indx = len(self.messages) - 1

        return self.messages[message_indx].convert_index(index, from_view, to_view, decoded)

    def convert_range(self, index1: int, index2: int, from_view: int,
                      to_view: int, decoded: bool, message_indx=-1):
        if len(self.messages) == 0:
            return 0, 0

        if message_indx == -1:
            message_indx = self.messages.index(max(self.messages, key=len))  # Longest message

        if message_indx >= len(self.messages):
            message_indx = len(self.messages) - 1

        return self.messages[message_indx].convert_range(index1, index2, from_view, to_view, decoded)

    def estimate_frequency_for_one(self, sample_rate: float, nbits=42) -> float:
        """
        Calculates the frequency of at most nbits logical ones and returns the mean of these frequencies

        :param nbits:
        :return:
        """
        return self.__estimate_frequency_for_bit(True, sample_rate, nbits)

    def align_messages(self, pattern: str, view_type: int, use_decoded=True):
        if view_type == 0:
            bit_pattern = pattern
        elif view_type == 1:
            bit_pattern = "".join(map(str, urh_util.hex2bit(pattern)))
        elif view_type == 2:
            bit_pattern = "".join(map(str, urh_util.ascii2bit(pattern)))
        else:
            raise ValueError("Unknown view type {}".format(view_type))

        indices = [msg.decoded_bits_str.find(bit_pattern) if use_decoded else msg.plain_bits_str.find(bit_pattern)
                   for msg in self.messages]

        max_index = max(indices)
        for i, msg in enumerate(self.messages):
            msg.alignment_offset = 0 if indices[i] == -1 else max_index - indices[i]

    def estimate_frequency_for_zero(self, sample_rate: float, nbits=42) -> float:
        """
        Calculates the frequency of at most nbits logical zeros and returns the mean of these frequencies

        :param nbits:
        :return:
        """
        return self.__estimate_frequency_for_bit(False, sample_rate, nbits)

    def __estimate_frequency_for_bit(self, bit: bool, sample_rate: float, nbits: int) -> float:
        if nbits == 0:
            return 0

        assert self.signal is not None
        frequencies = []
        for i, message in enumerate(self.messages):
            for j, msg_bit in enumerate(message.plain_bits):
                if msg_bit == bit:
                    start, num_samples = self.get_samplepos_of_bitseq(i, j, i, j + 1, False)
                    freq = self.signal.estimate_frequency(start, start + num_samples, sample_rate)
                    frequencies.append(freq)
                    if len(frequencies) == nbits:
                        return np.mean(frequencies)
        if frequencies:
            return np.mean(frequencies)
        else:
            return 0

    def __str__(self):
        return "ProtoAnalyzer " + self.name

    def set_labels(self, val):
        self._protocol_labels = val

    def add_new_message_type(self, labels):
        names = set(message_type.name for message_type in self.message_types)
        name = "Message type #"
        i = 0
        while True:
            i += 1
            if name + str(i) not in names:
                self.message_types.append(
                    MessageType(name=name + str(i), iterable=[copy.deepcopy(lbl) for lbl in labels]))
                break

    def to_binary(self, filename: str, use_decoded: bool):
        with open(filename, "wb") as f:
            for msg in self.messages:
                bits = msg.decoded_bits if use_decoded else msg.plain_bits
                aggregated = urh_util.aggregate_bits(bits, size=8)
                f.write(bytes(aggregated))

    def from_binary(self, filename: str):
        aggregated = np.fromfile(filename, dtype=np.uint8)
        unaggregated = [int(b) for n in aggregated for b in "{0:08b}".format(n)]
        self.messages.append(Message(unaggregated, 0, self.default_message_type))

    def to_xml_tag(self, decodings, participants, tag_name="protocol",
                   include_message_type=False, write_bits=False, messages=None, modulators=None) -> ET.Element:
        root = ET.Element(tag_name)
        messages = self.messages if messages is None else messages

        # Save modulators
        if modulators is not None:  # For protocol analyzer container
            root.append(Modulator.modulators_to_xml_tag(modulators))

        root.append(Encoding.decodings_to_xml_tag(decodings))
        root.append(Participant.participants_to_xml_tag(participants))

        # Save data
        data_tag = ET.SubElement(root, "messages")
        for i, message in enumerate(messages):
            message_tag = message.to_xml(decoders=decodings,
                                         include_message_type=include_message_type,
                                         write_bits=write_bits)
            data_tag.append(message_tag)

        # Save message types separatively as not saved in messages already
        if not include_message_type:
            message_types_tag = ET.SubElement(root, "message_types")
            for message_type in self.message_types:
                message_types_tag.append(message_type.to_xml())

        return root

    def to_xml_file(self, filename: str, decoders, participants, tag_name="protocol",
                    include_message_types=False, write_bits=False, modulators=None):
        tag = self.to_xml_tag(decodings=decoders, participants=participants, tag_name=tag_name,
                              include_message_type=include_message_types, write_bits=write_bits,
                              modulators=modulators)

        xmlstr = minidom.parseString(ET.tostring(tag)).toprettyxml(indent="   ")
        with open(filename, "w") as f:
            for line in xmlstr.split("\n"):
                if line.strip():
                    f.write(line + "\n")

    def from_xml_tag(self, root: ET.Element, read_bits=False, participants=None, decodings=None):
        if not root:
            return None

        decoders = Encoding.read_decoders_from_xml_tag(root) if decodings is None else decodings

        if participants is None:
            participants = Participant.read_participants_from_xml_tag(root)

        if read_bits:
            self.messages[:] = []

        try:
            message_types = []
            for message_type_tag in root.find("message_types").findall("message_type"):
                message_types.append(MessageType.from_xml(message_type_tag))
        except AttributeError:
            message_types = []

        for message_type in message_types:
            if message_type not in self.message_types:
                self.message_types.append(message_type)

        try:
            message_tags = root.find("messages").findall("message")
            for i, message_tag in enumerate(message_tags):
                if read_bits:
                    self.messages.append(Message.new_from_xml(tag=message_tag,
                                                              participants=participants,
                                                              decoders=decoders,
                                                              message_types=self.message_types))
                else:
                    try:
                        self.messages[i].from_xml(tag=message_tag, participants=participants,
                                                  decoders=decoders, message_types=self.message_types)
                    except IndexError:
                        pass  # Part of signal was copied in last session but signal was not saved

        except AttributeError:
            pass

    def from_xml_file(self, filename: str, read_bits=False):
        try:
            tree = ET.parse(filename)
        except FileNotFoundError:
            logger.error("Could not find file " + filename)
            return
        except ET.ParseError:
            logger.error("Could not parse file " + filename)
            return

        root = tree.getroot()
        self.from_xml_tag(root, read_bits=read_bits)

    def eliminate(self):
        self.message_types = None
        self.messages = None
        if self.signal is not None:
            self.signal.eliminate()
        self.signal = None

    def update_auto_message_types(self):
        for message in self.messages:
            for message_type in filter(lambda m: m.assigned_by_ruleset and len(m.ruleset) > 0, self.message_types):
                if message_type.ruleset.applies_for_message(message):
                    message.message_type = message_type
                    break

    def auto_assign_participants(self, participants):
        """

        :type participants: list of Participant
        :return:
        """
        if len(participants) == 0:
            return

        if len(participants) == 1:
            for message in self.messages:
                message.participant = participants[0]
            return

        # Try to assign participants based on SRC_ADDRESS label and participant address
        for msg in filter(lambda m: m.participant is None, self.messages):
            src_address = msg.get_src_address_from_data()
            if src_address:
                try:
                    msg.participant = next(p for p in participants if p.address_hex == src_address)
                except StopIteration:
                    pass

        # Assign remaining participants based on RSSI of messages
        rssis = np.array([msg.rssi for msg in self.messages], dtype=np.float32)
        min_rssi, max_rssi = util.minmax(rssis)
        center_spacing = (max_rssi - min_rssi) / (len(participants) - 1)
        centers = [min_rssi + i * center_spacing for i in range(0, len(participants))]
        rssi_assigned_centers = []

        for rssi in rssis:
            center_index = np.argmin(np.abs(rssi - centers))
            rssi_assigned_centers.append(int(center_index))

        participants.sort(key=lambda participant: participant.relative_rssi)
        for message, center_index in zip(self.messages, rssi_assigned_centers):
            if message.participant is None:
                message.participant = participants[center_index]

    def auto_assign_participant_addresses(self, participants):
        """

        :type participants: list of Participant
        :return:
        """
        participants_without_address = [p for p in participants if not p.address_hex]

        if len(participants_without_address) == 0:
            return

        for msg in self.messages:
            if msg.participant in participants_without_address:
                src_address = msg.get_src_address_from_data()
                if src_address:
                    participants_without_address.remove(msg.participant)
                    msg.participant.address_hex = src_address

    def auto_assign_decodings(self, decodings):
        """
        :type decodings: list of Encoding
        """
        nrz_decodings = [decoding for decoding in decodings if decoding.is_nrz or decoding.is_nrzi]
        fallback = nrz_decodings[0] if nrz_decodings else None
        candidate_decodings = [decoding for decoding in decodings
                               if decoding not in nrz_decodings and not decoding.contains_cut]

        for message in self.messages:
            decoder_found = False

            for decoder in candidate_decodings:
                if decoder.applies_for_message(message.plain_bits):
                    message.decoder = decoder
                    decoder_found = True
                    break

            if not decoder_found and fallback:
                message.decoder = fallback

    def auto_assign_labels(self):
        format_finder = FormatFinder(self)

        # OPEN: Perform multiple iterations with varying priorities later
        format_finder.perform_iteration()

    @staticmethod
    def get_protocol_from_string(message_strings: list, is_hex=None, default_pause=0, sample_rate=1e6):
        """

        :param message_strings:
        :param is_hex: None means auto detects
        :return:
        """
        protocol = ProtocolAnalyzer(None)

        def parse_line(line: str):
            # support transcript files e.g 1 (A->B): 10101111
            index = line.rfind(" ")
            line = line[index + 1:]

            # support pauses given like 100101/10s
            try:
                data, pause = line.split(constants.PAUSE_SEP)
            except ValueError:
                data, pause = line, str(default_pause)
            if pause.endswith("ms"):
                pause = float(pause[:-2]) * float(sample_rate) / 1e3
            elif pause.endswith("µs"):
                pause = float(pause[:-2]) * float(sample_rate) / 1e6
            elif pause.endswith("ns"):
                pause = float(pause[:-2]) * float(sample_rate) / 1e9
            elif pause.endswith("s"):
                pause = float(pause[:-1]) * float(sample_rate)
            else:
                pause = float(pause)

            return data, int(pause)

        if not is_hex:
            for line in filter(None, map(str.strip, message_strings)):
                bits, pause = parse_line(line)
                try:
                    protocol.messages.append(Message.from_plain_bits_str(bits, pause=pause))
                except ValueError:
                    is_hex = True if is_hex is None else is_hex
                    break

        if is_hex:
            protocol.messages.clear()
            lookup = {"{0:0x}".format(i): "{0:04b}".format(i) for i in range(16)}

            for line in filter(None, map(str.strip, message_strings)):
                bits, pause = parse_line(line)
                bit_str = [lookup[bits[i].lower()] for i in range(0, len(bits))]
                protocol.messages.append(Message.from_plain_bits_str("".join(bit_str), pause=pause))

        return protocol
