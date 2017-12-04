import threading
import numpy
import array
import time
import datetime

from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject

from urh.util.Logger import logger
from urh.SimulatorProtocolManager import SimulatorProtocolManager
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.util.ProjectManager import ProjectManager
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.EndlessSender import EndlessSender
from urh import SimulatorSettings
from urh.signalprocessing.Message import Message
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.signalprocessing.SimulatorExpressionParser import SimulatorExpressionParser

from urh.signalprocessing.Encoding import Encoding

class Simulator(QObject):
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    stopping_simulation = pyqtSignal()

    def __init__(self, protocol_manager: SimulatorProtocolManager, modulators,
                 expression_parser: SimulatorExpressionParser, project_manager: ProjectManager):
        super().__init__()
        self.protocol_manager = protocol_manager
        self.project_manager = project_manager
        self.expression_parser = expression_parser
        self.modulators = modulators
        self.backend_handler = BackendHandler()

        self.profile_sniffer_dict = {}
        self.profile_sender_dict = {}

        self.current_item = None
        self.last_sent_message = None
        self.is_simulating = False
        self.do_restart = False
        self.current_repeat = 0
        self.messages = []

        self.measure_started = False
        self.time = None

        self.init_devices()

    def init_devices(self):
        for participant in self.protocol_manager.active_participants:
            if not participant.simulate:
                recv_profile = participant.recv_profile

                if recv_profile['name'] not in self.profile_sniffer_dict:
                    bit_length = recv_profile['bit_length']
                    center = recv_profile['center']
                    noise = recv_profile['noise']
                    tolerance = recv_profile['error_tolerance']
                    modulation = recv_profile['modulation']
                    device = recv_profile['device']

                    sniffer = ProtocolSniffer(bit_length, center, noise, tolerance,
                                              modulation, device, self.backend_handler, raw_mode=True, real_time=True)

                    self.load_device_parameter(sniffer.rcv_device, recv_profile, is_rx=True)
                    self.profile_sniffer_dict[recv_profile['name']] = sniffer
            else:
                send_profile = participant.send_profile

                if send_profile['name'] not in self.profile_sender_dict:
                    device = send_profile['device']

                    sender = EndlessSender(self.backend_handler, device)

                    self.load_device_parameter(sender.device, send_profile, is_rx=False)
                    self.profile_sender_dict[send_profile['name']] = sender

    def load_device_parameter(self, device, profile, is_rx):
        prefix = "rx_" if is_rx else "tx_"

        device.device_args = profile['device_args']
        device.frequency = profile['center_freq']
        device.sample_rate = profile['sample_rate']
        device.bandwidth = profile['bandwidth']
        device.freq_correction = profile['freq_correction']
        device.direct_sampling_mode = profile['direct_sampling']
        device.channel_index = profile[prefix + 'channel']
        device.antenna_index = profile[prefix + 'antenna']
        device.ip = profile[prefix + 'ip']
        device.gain = profile[prefix + 'rf_gain']
        device.if_gain = profile[prefix + 'if_gain']
        device.baseband_gain = profile[prefix + 'baseband_gain']

    def start(self):
        self.reset()

        # start devices
        for _, sniffer in self.profile_sniffer_dict.items():
            sniffer.sniff()

        for _, sender in self.profile_sender_dict.items():
            sender.start()

        time.sleep(2)

        self._start_simulation_thread()

    def stop(self):
        if not self.is_simulating:
            return

        self.log_message("Stop simulation ...")
        self.is_simulating = False

        self.stopping_simulation.emit()

        # stop devices
        for _, sniffer in self.profile_sniffer_dict.items():
            sniffer.stop()

        for _, sender in self.profile_sender_dict.items():
            sender.stop()

    def restart(self):
        self.reset()
        self.log_message("Restart simulation ...")

    def reset(self):
        for _, sniffer in self.profile_sniffer_dict.items():
            sniffer.clear()

        self.current_item = self.protocol_manager.rootItem

        for msg in self.protocol_manager.get_all_messages():
            msg.send_recv_messages[:] = []

        self.last_sent_message = None
        self.is_simulating = True
        self.do_restart = False
        self.current_repeat = 0
        self.messages[:] = []
        self.measure_started  = False

    @property
    def devices(self):
        result = []

        for _, sniffer in self.profile_sniffer_dict.items():
            result.append(sniffer.rcv_device)

        for _, sender in self.profile_sender_dict.items():
            result.append(sender.device)

        return result
        
    def device_messages(self):
        messages = ""

        for device in self.devices:
            messages += device.read_messages()

            if messages and not messages.endswith("\n"):
                messages += "\n"

        return messages

    def read_messages(self):
        messages = "\n".join(self.messages)

        if messages and not messages.endswith("\n"):
            messages += "\n"

        self.messages[:] = []
        return messages            

    def cleanup(self):
        for device in self.devices:
            if device.backend not in (Backends.none, Backends.network):
                try:
                    # For Protocol Sniffer
                    device.index_changed.disconnect()
                except TypeError:
                    pass

                device.cleanup()

            if device is not None:
                device.free_data()

    def _start_simulation_thread(self):
        self.simulation_thread = threading.Thread(target=self.simulate)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

    def simulation_is_finished(self):
        if SimulatorSettings.num_repeat == 0:
            return False

        return self.current_repeat >= SimulatorSettings.num_repeat

    def simulate(self):
        self.simulation_started.emit()
        self.log_message("Start simulation ...")

        while self.is_simulating and not self.simulation_is_finished():
            if (self.current_item is self.protocol_manager.rootItem or
                    isinstance(self.current_item, SimulatorProtocolLabel)):
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorMessage):
                self.process_message()
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorGotoAction):
                next_item = self.current_item.target
                self.log_message("GOTO item " + next_item.index())
            elif isinstance(self.current_item, SimulatorRule):
                true_cond = self.current_item.true_condition()

                if true_cond is not None and true_cond.logging_active and true_cond.type != ConditionType.ELSE:
                    self.log_message("Rule condition " + true_cond.index() + " (" + true_cond.condition + ") applied")
                
                next_item = true_cond.children[0] if true_cond is not None and true_cond.child_count() else self.current_item.next_sibling()
            elif (isinstance(self.current_item, SimulatorRuleCondition) and 
                    self.current_item.type != ConditionType.IF):
                next_item = self.current_item.parent().next_sibling()
            elif (isinstance(self.current_item, SimulatorRuleCondition) and
                    self.current_item.type == ConditionType.IF):
                next_item = self.current_item.parent()
            elif self.current_item is None:
                self.current_repeat += 1
                next_item = self.protocol_manager.rootItem 
            else:
                raise NotImplementedError("TODO")

            self.current_item = next_item

            if self.do_restart:
                self.restart()

        self.stop()
        self.simulation_stopped.emit()

    def process_message(self):
        assert isinstance(self.current_item, SimulatorMessage)
        msg = self.current_item

        if msg.participant is None:
            return

        new_message = self.generate_message_from_template(msg)

        if msg.participant.simulate:
            # we have to send a message ...
            sender = self.profile_sender_dict[msg.participant.send_profile['name']]

            start_time = time.perf_counter()

            for lbl in new_message.message_type:
                if lbl.value_type_index == 4:
                    # random value
                    result = numpy.random.randint(lbl.random_min, lbl.random_max + 1)
                    self.set_label_value(new_message, lbl, result)

            print("Random values: " + str(time.perf_counter() - start_time))

            # calculate checksums ...

            start_time  = time.perf_counter()

            for lbl in new_message.message_type:
                if isinstance(lbl.label, ChecksumLabel):
                    checksum = lbl.label.calculate_checksum_for_message(new_message, use_decoded_bits=False)
                    label_range = new_message.get_label_range(lbl=lbl.label, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    new_message.plain_bits[start:end] = checksum + array.array("B", [0] *(
                    (end - start) - len(checksum)))

            print("Checksums: " + str(time.perf_counter() - start_time))

            start_time = time.perf_counter()
            self.send_message(new_message, msg.repeat, sender, msg.modulator_index)

            print("Send message: " + str(time.perf_counter() - start_time))

            self.log_message("Sending message " + msg.index())
            self.log_message_labels(new_message)
            msg.send_recv_messages.append(new_message)
            self.last_sent_message = msg
        else:
            # we have to receive a message ...
            self.log_message("Waiting for message " + msg.index() + " ...")
            sniffer = self.profile_sniffer_dict[msg.participant.recv_profile['name']]
            retry = 0

            while self.is_simulating and not self.simulation_is_finished() and retry < SimulatorSettings.retries:
                start_time = time.perf_counter()
                received_msg = self.receive_message(sniffer)
                print("Receive message: " + str(time.perf_counter() - start_time))

                if not self.is_simulating:
                    return

                if received_msg is None:
                    if SimulatorSettings.error_handling_index == 0:
                        # resend last message
                        self.resend_last_message()

                        # and try again ...
                        retry += 1
                        continue
                    elif SimulatorSettings.error_handling_index == 1:
                        self.stop()
                        return
                    elif SimulatorSettings.error_handling_index == 2:
                        self.do_restart = True
                        return

                received_msg.decoder = new_message.decoder
                received_msg.message_type = new_message.message_type

                if (not self.measure_started) and received_msg.decoded_bits_str == "10101010100111010101000010010000000110001100010011011101011100000000100011111011":
                    self.measure_started = True
                    self.time = time.perf_counter()

                if self.measure_started and received_msg.decoded_bits_str == "101010101001110100100000010000000000111001000000000100000000100110000000001000000000010101011011":
                    self.measure_started = False
                    print("--- " + str(time.perf_counter() - self.time) + " ---")
                    

                start_time = time.perf_counter()
                check_result = self.check_message(received_msg, new_message)
                print("Check message: " + str(time.perf_counter() - start_time) + " " + str(check_result))

                if check_result:
                    decoded_msg = Message(received_msg.decoded_bits, 0,
                        received_msg.message_type, decoder=received_msg.decoder)
                    msg.send_recv_messages.append(decoded_msg)
                    self.log_message("Received message " + msg.index() + ": ")
                    self.log_message_labels(decoded_msg)
                    return

                retry += 1

            if retry == SimulatorSettings.retries:
                self.log_message("Message " + msg.index() + " not received")
                self.stop()

    def log_message(self, message):
        now = datetime.datetime.now()
        timestamp = '{0:%b} {0.day} {0:%H}:{0:%M}:{0:%S}.{0:%f}'.format(now)
        self.messages.append(timestamp + ": " + message)

    def check_message(self, received_msg, expected_msg):
        # do we have a crc label?
        crc_label = next((lbl.label for lbl in received_msg.message_type if isinstance(lbl.label, ChecksumLabel)), None)

        if crc_label is not None:
            checksum = crc_label.calculate_checksum_for_message(received_msg, use_decoded_bits=True)
            start, end = received_msg.get_label_range(crc_label, 0, True)

            if checksum != received_msg.decoded_bits[start:end]:
                # checksum wrong ...
                return False

        for lbl in received_msg.message_type:
            if isinstance(lbl.label, ChecksumLabel):
                continue

            if lbl.value_type_index in [1, 3, 4]:
                # get live, external program, random
                continue

            start_recv, end_recv = received_msg.get_label_range(lbl.label, 0, True)
            start_exp, end_exp = expected_msg.get_label_range(lbl.label, 0, False)

            if received_msg.decoded_bits[start_recv:end_recv] != expected_msg[start_exp:end_exp]:
                return False

        return True

    def log_message_labels(self, message: Message):
        for lbl in message.message_type:
            if lbl.logging_active:
                start, end = message.get_label_range(lbl, lbl.display_format_index % 3, False)

                if lbl.display_format_index == 0:
                    value = message.plain_bits_str[start:end]
                elif lbl.display_format_index == 1:
                    value = message.plain_hex_str[start:end]
                elif lbl.display_format_index == 2:
                    value =  message.plain_ascii_str[start:end]
                elif lbl.display_format_index == 3:
                    try:
                        value = str(int(message.plain_bits_str[start:end], 2))
                    except ValueError:
                        value = ""

                self.messages.append("\t" + lbl.name + ": " + value)

    def resend_last_message(self):
        self.log_message("Resending last message ...")
        lsm = self.last_sent_message

        if lsm is None:
            return

        sender = self.profile_sender_dict[lsm.participant.send_profile['name']]
        self.send_message(lsm.send_recv_messages[-1], lsm.repeat, sender, lsm.modulator_index)

    def send_message(self, message, repeat, sender, modulator_index):
        modulator = self.modulators[modulator_index]
        modulator.modulate(message.encoded_bits, pause=message.pause)

        curr_repeat = 0

        while curr_repeat < repeat:
            sender.push_data(modulator.modulated_samples)
            curr_repeat += 1

    def receive_message(self, sniffer):
        msg = None
        loop = QEventLoop()
        sniffer.qt_signals.data_sniffed.connect(loop.quit)
        self.stopping_simulation.connect(loop.quit)

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(SimulatorSettings.timeout * 1000)

        while self.is_simulating and timer.isActive():
            if len(sniffer.messages):
                msg = sniffer.messages[0]
                sniffer.messages.remove(msg)
                break

            loop.exec()

        if not timer.isActive():
            self.log_message("Receive timeout")

        # just to be sure ...
        timer.stop()
        return msg

    def set_label_value(self, message, label, value):
        lbl_len = label.end - label.start
        f_string = "{0:0" + str(lbl_len) + "b}"
        bits = f_string.format(value)

        if len(bits) > lbl_len:
            logger.warning("Value {0} too big for label {1}, bits truncated".format(value, label.name))

        for i in range(lbl_len):
            message[label.start + i] = bool(int(bits[i]))
        
    def generate_message_from_template(self, template_msg):
        new_message = Message(template_msg.plain_bits, pause=template_msg.pause, rssi=0,
                        message_type=template_msg.message_type, decoder=template_msg.decoder)

        for lbl in template_msg.children:
            if lbl.value_type_index == 2:
                # formula
                valid, _, node = self.expression_parser.validate_expression(lbl.formula)
                assert valid == True
                result = self.expression_parser.evaluate_node(node)
            else:
                continue

            self.set_label_value(new_message, lbl, result)

        return new_message
