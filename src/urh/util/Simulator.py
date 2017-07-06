import threading
import numpy
from random import randrange

from urh.util.Logger import logger
from urh.SimulatorProtocolManager import SimulatorProtocolManager
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.util.ProjectManager import ProjectManager
from urh.dev.BackendHandler import BackendHandler
from urh.dev.EndlessSender import EndlessSender
from urh import SimulatorSettings
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.signalprocessing.SimulatorGotoAction import SimulatorGotoAction
from urh.signalprocessing.SimulatorProtocolLabel import SimulatorProtocolLabel

class Simulator(object):
    def __init__(self, protocol_manager: SimulatorProtocolManager, expression_parser, project_manager: ProjectManager):
        self.protocol_manager = protocol_manager
        self.project_manager = project_manager
        self.expression_parser = expression_parser
        self.backend_handler = BackendHandler()

        self.profile_sniffer_dict = {}
        self.profile_sender_dict = {}

        self.current_item = None
        self.is_simulating = False
        self.current_repeat = 0

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
#        for sniffer in self.profile_sniffer_dict.keys():
#            sniffer.sniff()

#        for sender in self.profile_sender_dict.keys():
#            sender.start()

        self.current_item = self.protocol_manager.rootItem
        self.is_simulating = True

        self._start_simulation_thread()

    def stop(self):
        self.is_simulating = False

        # stop devices
        for sniffer in self.profile_sniffer_dict.keys():
            sniffer.stop()

        for sender in self.profile_sender_dict.keys():
            sender.stop()

    def _start_simulation_thread(self):
        self.simulation_thread = threading.Thread(target=self.simulate)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()

    def simulation_is_finished(self):
        if SimulatorSettings.num_repeat == 0:
            return False

        return (self.current_repeat >= SimulatorSettings.num_repeat and
                self.current_item is None)

    def simulate(self):
        print("Start simulation ...")
        next_item = None

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

        print("Stop simulation ...")

    def process_message(self):
        assert isinstance(self.current_item, SimulatorMessage)
        msg = self.current_item

        if msg.participant is None:
            return

        if msg.participant.simulate:
            # we have to send a message ...
            sender = self.profile_sender_dict[msg.participant.send_profile['name']]
            new_message = Message(msg.plain_bits, 0, MessageType("dummy"))

            for lbl in msg.children:
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
        elif msg.destination.simulate:
            # we have to receive a message ...
            sniffer = self.profile_sniffer_dict[msg.participant.recv_profile]