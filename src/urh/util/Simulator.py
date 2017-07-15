import threading
import numpy
import array
from random import randrange

from PyQt5.QtCore import QEventLoop, QTimer

from urh.util.Logger import logger
from urh.SimulatorProtocolManager import SimulatorProtocolManager
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.util.ProjectManager import ProjectManager
from urh.dev.BackendHandler import BackendHandler
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

class Simulator(object):
    def __init__(self, protocol_manager: SimulatorProtocolManager, modulators,
                 expression_parser: SimulatorExpressionParser, project_manager: ProjectManager):
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
        self.receive_timeout = False

        self.init_devices()

    def init_devices(self):
        for participant in self.project_manager.participants:
            if not participant.simulate:
                continue

            recv_profile = participant.recv_profile

            if recv_profile['name'] not in self.profile_sniffer_dict:
                bit_length = recv_profile['bit_length']
                center = recv_profile['center']
                noise = recv_profile['noise']
                tolerance = recv_profile['error_tolerance']
                modulation = recv_profile['modulation']
                device = recv_profile['device']

                sniffer = ProtocolSniffer(bit_length, center, noise, tolerance,
                                          modulation, device, self.backend_handler)

                self.load_device_parameter(sniffer.rcv_device, recv_profile, is_rx=True)
                self.profile_sniffer_dict[recv_profile['name']] = sniffer

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
        # start devices
        for _, sniffer in self.profile_sniffer_dict.items():
            sniffer.sniff()

        for _, sender in self.profile_sender_dict.items():
            sender.start()

        self.current_item = self.protocol_manager.rootItem

        for msg in self.protocol_manager.get_all_messages():
            msg.send_recv_messages[:] = []

        self.last_sent_message = None
        self.is_simulating = True
        self.current_repeat = 0

        self._start_simulation_thread()

    def stop(self):
        print("Stop simulation ...")
        self.is_simulating = False

        # stop devices
        for _, sniffer in self.profile_sniffer_dict.items():
            sniffer.stop()

        for _, sender in self.profile_sender_dict.items():
            sender.stop()

    def _start_simulation_thread(self):
        self.simulation_thread = threading.Thread(target=self.simulate)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

    def simulation_is_finished(self):
        if SimulatorSettings.num_repeat == 0:
            return False

        return self.current_repeat >= SimulatorSettings.num_repeat

    def simulate(self):
        print("Start simulation ...")

        while self.is_simulating and not self.simulation_is_finished():
            if (self.current_item is self.protocol_manager.rootItem or
                    isinstance(self.current_item, SimulatorProtocolLabel)):
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorMessage):
                self.process_message()
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorGotoAction):
                next_item = self.current_item.target
            elif isinstance(self.current_item, SimulatorRule):
                next_item = self.current_item.next_item()
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

        self.stop()

    def process_message(self):
        assert isinstance(self.current_item, SimulatorMessage)
        msg = self.current_item
        print("Processing message " + msg.index())

        if msg.participant is None:
            return

        new_message = self.generate_message_from_template(msg)

        if msg.participant.simulate:
            # we have to send a message ...

            # calculate checksums ...
            for lbl in new_message.message_type:
                if isinstance(lbl.label, ChecksumLabel):
                    checksum = lbl.label.calculate_checksum_for_message(new_message, use_decoded_bits=False)
                    label_range = new_message.get_label_range(lbl=lbl.label, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    new_message.plain_bits[start:end] = checksum + array.array("B", [0] *(
                    (end - start) - len(checksum)))

            print("Send message " + msg.index())
            sender = self.profile_sender_dict[msg.participant.send_profile['name']]
            self.send_message(new_message, sender, msg.modulator_indx)
            msg.send_recv_messages.append(new_message)
            self.last_sent_message = msg
        elif msg.destination.simulate:
#        if True:
            # we have to receive a message ...
            sniffer = self.profile_sniffer_dict[msg.destination.recv_profile['name']]

            retry = 0

            while retry < 10:
                received_msg = self.receive_message(sniffer)
                received_msg.decoder = new_message.decoder
                received_msg.message_type = new_message.message_type

                print("Bits: " + received_msg.decoded_bits_str)

                if received_msg is None:
                    if SimulatorSettings.error_handling_index == 0:
                        # resend last message
                        self.resend_last_message()

                        # and try again ...
                        received_msg = self.receive_message(sniffer)

                        if received_msg is None:
                            self.stop()
                            return
                    elif SimulatorSettings.error_handling_index == 1:
                        self.stop()
                        return
                    elif SimulatorSettings.error_handling_index == 2:
                        self.do_restart = True
                        return

                decoded_msg = Message(received_msg.decoded_bits, 0,
                        received_msg.message_type, decoder=received_msg.decoder)

                if self.check_message(received_msg, new_message):
                    msg.send_recv_messages.append(decoded_msg)
                    print("Received message for message !! :)" + msg.index())
                    break
                else:
                    if isinstance(msg.next_sibling(), SimulatorMessage):
                        next_message = msg.next_sibling()
                        next_new_message = self.generate_message_from_template(next_message)
                        received_msg.decoder = next_message.decoder
                        received_msg.message_type = next_message.message_type

                        if self.check_message(received_msg, next_new_message):
                            print("Omitting message :(" + msg.index())
                            self.current_item = next_message
                            next_message.send_recv_messages.append(decoded_msg)
                            break

                retry += 1

    def check_message(self, received_msg, expected_msg):
        # do we have a crc label?
        crc_label = next((lbl.label for lbl in received_msg.message_type if isinstance(lbl.label, ChecksumLabel)), None)

        if crc_label is not None:
            checksum = crc_label.calculate_checksum_for_message(received_msg, use_decoded_bits=True)
            start, end = received_msg.get_label_range(crc_label, 0, True)

            if checksum == received_msg.decoded_bits[start:end]:
                print("Checksum correct :)")
            else:
                print("Checksum wrong :(")
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
                print("Label " + lbl.name + " did not met expectation :(")
                return False

        return True

    def resend_last_message(self):
        lsm = self.last_sent_message

        if lsm is None:
            return

        sender = self.profile_sender_dict[lsm.participant.send_profile['name']]
        self.send_message(lsm.send_recv_messages[-1], sender, lsm.modulator_indx)

    def send_message(self, message, sender, modulator_index):
        modulator = self.modulators[modulator_index]
        modulator.modulate(message.encoded_bits, pause=message.pause)
        sender.push_data(modulator.modulated_samples)

    def on_receive_timeout(self):
        self.receive_timeout = True

    def receive_message(self, sniffer):
        self.receive_timeout = False
        msg = None

        loop = QEventLoop()
        sniffer.qt_signals.data_sniffed.connect(loop.quit)

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.timeout.connect(self.on_receive_timeout)
        timer.start(SimulatorSettings.timeout * 1000)

        while not self.receive_timeout:
            if len(sniffer.messages):
                msg = sniffer.messages[0]
                sniffer.messages.remove(msg)
                break

            loop.exec()

        # just to be sure ...
        timer.stop()
        return msg

    def generate_message_from_template(self, template_msg):
        new_message = Message(template_msg.plain_bits, pause=template_msg.pause, rssi=0,
                        message_type=template_msg.message_type, decoder=template_msg.decoder)

        for lbl in template_msg.children:
            lbl_len = lbl.end - lbl.start
            f_string = "{0:0" + str(lbl_len) + "b}"

            if lbl.value_type_index == 2:
                # formula
                formula = lbl.formula
                valid, _, node = self.expression_parser.validate_expression(formula)
                assert valid == True
                result = self.expression_parser.evaluate_node(node)
            elif lbl.value_type_index == 4:
                # random value
                result = numpy.random.randint(lbl.random_min, lbl.random_max + 1)
                print(result)
            else:
                continue

            bits = f_string.format(result)

            if len(bits) > lbl_len:
                logger.warning("Value {0} too big for label {1}, bits truncated".format(result, lbl.name))

            for i in range(lbl_len):
                new_message[lbl.start + i] = bool(int(bits[i]))

        return new_message