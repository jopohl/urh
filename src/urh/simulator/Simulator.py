import array
import datetime
import threading
import time

import numpy
from PyQt5.QtCore import pyqtSignal, QObject, pyqtSlot
from PyQt5.QtTest import QSignalSpy

from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.EndlessSender import EndlessSender
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.simulator.SimulatorExpressionParser import SimulatorExpressionParser
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.util import util
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class Simulator(QObject):
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()

    def __init__(self, protocol_manager: SimulatorConfiguration, modulators,
                 expression_parser: SimulatorExpressionParser, project_manager: ProjectManager,
                 sniffer: ProtocolSniffer, sender: EndlessSender):
        super().__init__()
        self.protocol_manager = protocol_manager
        self.project_manager = project_manager
        self.expression_parser = expression_parser
        self.modulators = modulators  # type: list[Modulator]
        self.backend_handler = BackendHandler()

        self.transcript = []

        self.current_item = None
        self.last_sent_message = None
        self.is_simulating = False
        self.do_restart = False
        self.current_repeat = 0
        self.log_messages = []

        self.sniffer_ready = False
        self.sender_ready = False
        self.fatal_device_error_occurred = False

        self.measure_started = False
        self.time = None

        self.verbose = True

        self.sniffer = sniffer
        self.sender = sender

    def start(self):
        self.reset()

        # start devices
        self.sniffer.rcv_device.fatal_error_occurred.connect(self.stop_on_error)
        self.sniffer.rcv_device.ready_for_action.connect(self.on_sniffer_ready)
        self.sender.device.fatal_error_occurred.connect(self.stop_on_error)
        self.sender.device.ready_for_action.connect(self.on_sender_ready)

        self.sniffer.sniff()
        self.sender.start()

        self._start_simulation_thread()

        # Ensure all ongoing qt signals can be processed
        time.sleep(0.1)

    @pyqtSlot(str)
    def stop_on_error(self, msg: str):
        self.fatal_device_error_occurred = True
        if self.is_simulating:
            self.stop(msg=msg)

    @pyqtSlot()
    def on_sniffer_ready(self):
        if not self.sniffer_ready:
            self.log_message("Sniffer is ready to operate")
            self.sniffer_ready = True

    @pyqtSlot()
    def on_sender_ready(self):
        if not self.sender_ready:
            self.log_message("Sender is ready to operate")
            self.sender_ready = True

    def stop(self, msg=""):
        self.log_message("Stop simulation ..." + "{}".format(msg))
        self.is_simulating = False

        if msg == "Finished":
            # Ensure devices can send their last data before killing them
            time.sleep(0.5)

        # stop devices
        self.sniffer.stop()
        self.sender.stop()

        self.simulation_stopped.emit()

    def restart(self):
        self.reset()
        self.log_message("Restart simulation ...")

    def reset(self):
        self.sniffer_ready = False
        self.sender_ready = False
        self.fatal_device_error_occurred = False
        self.sniffer.clear()

        self.current_item = self.protocol_manager.rootItem

        for msg in self.protocol_manager.get_all_messages():
            msg.send_recv_messages[:] = []

        self.last_sent_message = None
        self.is_simulating = True
        self.do_restart = False
        self.current_repeat = 0
        self.log_messages[:] = []
        self.measure_started = False
        self.transcript.clear()

    @property
    def devices(self):
        result = [self.sniffer.rcv_device, self.sender.device]
        return result

    def device_messages(self):
        result = ""

        for device in self.devices:
            new_messages = device.read_messages()
            if new_messages:
                result += new_messages

            if result and not result.endswith("\n"):
                result += "\n"

        return result

    def read_log_messages(self):
        result = "\n".join(self.log_messages)

        if result and not result.endswith("\n"):
            result += "\n"

        self.log_messages.clear()
        return result

    def cleanup(self):
        for device in self.devices:
            if device.backend not in (Backends.none, Backends.network):
                try:
                    # For Protocol Sniffer
                    device.data_received.disconnect()
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
        if self.project_manager.simulator_num_repeat == 0:
            return False

        return self.current_repeat >= self.project_manager.simulator_num_repeat

    def __wait_for_devices(self):
        for i in range(5):
            if self.sniffer_ready and self.sender_ready:
                return True
            if self.fatal_device_error_occurred:
                return False
            self.log_message("Waiting for devices ...")
            time.sleep(1)

        return True

    def simulate(self):
        self.simulation_started.emit()
        self.is_simulating = self.__wait_for_devices()

        if not self.is_simulating:
            # Simulation may have ended due to device errors
            self.stop("Devices not ready")
            return

        self.log_message("Start simulation ...")

        while self.is_simulating and not self.simulation_is_finished():
            if self.current_item is self.protocol_manager.rootItem:
                self.transcript.clear()
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorProtocolLabel):
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorMessage):
                self.process_message()
                next_item = self.current_item.next()
            elif isinstance(self.current_item, SimulatorGotoAction):
                next_item = self.current_item.target
                self.log_message("GOTO item " + next_item.index())
            elif isinstance(self.current_item, SimulatorRule):
                condition = self.current_item.get_first_applying_condition()

                if condition is not None and condition.logging_active and condition.type != ConditionType.ELSE:
                    self.log_message("Rule condition " + condition.index() + " (" + condition.condition + ") applied")

                if condition is not None and condition.child_count() > 0:
                    next_item = condition.children[0]
                else:
                    next_item = self.current_item.next_sibling()

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

        self.stop(msg="Finished")

    def process_message(self):
        assert isinstance(self.current_item, SimulatorMessage)
        msg = self.current_item

        if msg.source is None:
            return

        new_message = self.generate_message_from_template(msg)

        if msg.source.simulate:
            # we have to send a message
            sender = self.sender

            for lbl in new_message.message_type:
                if isinstance(lbl.label, ChecksumLabel):
                    checksum = lbl.label.calculate_checksum_for_message(new_message, use_decoded_bits=False)
                    label_range = new_message.get_label_range(lbl=lbl.label, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    new_message.plain_bits[start:end] = checksum + array.array("B", [0] * (
                            (end - start) - len(checksum)))

            self.transcript.append((msg.source, msg.destination, new_message))
            self.send_message(new_message, msg.repeat, sender, msg.modulator_index)
            self.log_message("Sending message " + msg.index())
            self.log_message_labels(new_message)
            msg.send_recv_messages.append(new_message)
            self.last_sent_message = msg
        else:
            # we have to receive a message
            self.log_message("Waiting for message " + msg.index() + " ...")
            sniffer = self.sniffer
            retry = 0

            max_retries = self.project_manager.simulator_retries
            while self.is_simulating and not self.simulation_is_finished() and retry < max_retries:
                received_msg = self.receive_message(sniffer)

                if not self.is_simulating:
                    return

                if received_msg is None:
                    if self.project_manager.simulator_error_handling_index == 0:
                        self.resend_last_message()
                        retry += 1
                        continue
                    elif self.project_manager.simulator_error_handling_index == 1:
                        self.stop()
                        return
                    elif self.project_manager.simulator_error_handling_index == 2:
                        self.do_restart = True
                        return

                received_msg.decoder = new_message.decoder
                received_msg.message_type = new_message.message_type

                check_result, error_msg = self.check_message(received_msg, new_message, retry=retry)

                if check_result:
                    decoded_msg = Message(received_msg.decoded_bits, 0,
                                          received_msg.message_type, decoder=received_msg.decoder)
                    msg.send_recv_messages.append(decoded_msg)
                    self.transcript.append((msg.source, msg.destination, decoded_msg))
                    self.log_message("Received message " + msg.index() + ": ")
                    self.log_message_labels(decoded_msg)
                    return
                elif self.verbose:
                    self.log_message(error_msg)

                retry += 1

            if retry == self.project_manager.simulator_retries:
                self.log_message("Message " + msg.index() + " not received")
                self.stop()

    def log_message(self, message):
        now = datetime.datetime.now()
        timestamp = '{0:%b} {0.day} {0:%H}:{0:%M}:{0:%S}.{0:%f}'.format(now)
        self.log_messages.append(timestamp + ": " + message)
        logger.debug(timestamp + ": " + message)

    def check_message(self, received_msg, expected_msg, retry: int) -> (bool, str):
        # do we have a crc label?
        crc_label = next((lbl.label for lbl in received_msg.message_type if isinstance(lbl.label, ChecksumLabel)), None)

        if crc_label is not None:
            checksum = crc_label.calculate_checksum_for_message(received_msg, use_decoded_bits=True)
            start, end = received_msg.get_label_range(crc_label, 0, True)

            if checksum != received_msg.decoded_bits[start:end]:
                return False, "CRC mismatch"

        for lbl in received_msg.message_type:
            if isinstance(lbl.label, ChecksumLabel):
                continue

            if lbl.value_type_index in [1, 3, 4]:
                # get live, external program, random
                continue

            start_recv, end_recv = received_msg.get_label_range(lbl.label, 0, True)
            start_exp, end_exp = expected_msg.get_label_range(lbl.label, 0, False)

            actual = received_msg.decoded_bits[start_recv:end_recv]
            expected = expected_msg[start_exp:end_exp]
            if actual != expected:
                error_msg = "\n  [Attempt {}/{}] Mismatch for label {}.\n" \
                            "  Expected:\t{}\n  Got:\t{}".format(retry + 1,
                                                                 self.project_manager.simulator_retries,
                                                                 lbl.name,
                                                                 "".join(map(str, expected)),
                                                                 "".join(map(str, actual)))
                return False, error_msg

        return True, ""

    def log_message_labels(self, message: Message):
        message.split(decode=False)
        for lbl in message.message_type:
            if not lbl.logging_active:
                continue

            try:
                data = message.plain_bits[lbl.start:lbl.end]
            except IndexError:
                return None

            lsb = lbl.display_bit_order_index == 1
            lsd = lbl.display_bit_order_index == 2

            data = util.convert_bits_to_string(data, lbl.display_format_index, pad_zeros=True, lsb=lsb, lsd=lsd)
            if data is None:
                continue

            logger.debug("\t" + lbl.name + ": " + data)
            self.log_messages.append("\t" + lbl.name + ": " + data)

    def resend_last_message(self):
        self.log_message("Resending last message ...")
        lsm = self.last_sent_message

        if lsm is None:
            return

        sender = self.sender
        self.send_message(lsm.send_recv_messages[-1], lsm.repeat, sender, lsm.modulator_index)

    def send_message(self, message, repeat, sender, modulator_index):
        modulator = self.modulators[modulator_index]
        modulator.modulate(message.encoded_bits, pause=message.pause)

        curr_repeat = 0

        while curr_repeat < repeat:
            sender.push_data(modulator.modulated_samples)
            curr_repeat += 1

    def receive_message(self, sniffer):
        if sniffer.messages:
            return sniffer.messages.pop(0)

        spy = QSignalSpy(sniffer.message_sniffed)
        if spy.wait(self.project_manager.simulator_timeout * 1000):
            return sniffer.messages.pop(0)
        else:
            self.log_message("Receive timeout")
            return None

    def get_transcript(self, participant: Participant):
        result = []
        for source, destination, msg in self.transcript:
            if participant == destination:
                result.append("->" + msg.plain_bits_str)
            elif participant == source:
                result.append("<-" + msg.plain_bits_str)

        return "\n".join(result)

    def generate_message_from_template(self, template_msg: SimulatorMessage):
        new_message = Message(template_msg.plain_bits, pause=template_msg.pause, rssi=0,
                              message_type=template_msg.message_type, decoder=template_msg.decoder)

        for lbl in template_msg.children:  # type: SimulatorProtocolLabel
            if lbl.value_type_index == 2:
                # formula
                valid, _, node = self.expression_parser.validate_expression(lbl.formula)
                assert valid
                result = self.expression_parser.evaluate_node(node)
            elif lbl.value_type_index == 3:
                transcript = self.get_transcript(template_msg.source
                                                 if template_msg.source.simulate
                                                 else template_msg.destination)
                direction = "->" if template_msg.source.simulate else "<-"
                transcript += direction + new_message.plain_bits_str + "\n"
                result = util.run_command(lbl.external_program, transcript, use_stdin=True)
                if len(result) != lbl.end - lbl.start:
                    log_msg = "Result value of external program {} ({}) does not match label length {}"
                    logger.error(log_msg.format(result, len(result), lbl.end-lbl.start))
                    continue

                try:
                    new_message[lbl.start:lbl.end] = array.array("B", (map(bool, map(int, result))))
                except Exception as e:
                    log_msg = "Could not assign {} to range because {}".format(result, e)
                    logger.error(log_msg)

                continue
            elif lbl.value_type_index == 4:
                # random value
                result = numpy.random.randint(lbl.random_min, lbl.random_max + 1)
            else:
                continue

            self.set_label_value(new_message, lbl, result)

        return new_message

    @staticmethod
    def set_label_value(message, label, decimal_value: int):
        lbl_len = label.end - label.start
        f_string = "{0:0" + str(lbl_len) + "b}"
        bits = f_string.format(decimal_value)

        if len(bits) > lbl_len:
            logger.warning("Value {0} too big for label {1}, bits truncated".format(decimal_value, label.name))

        for i in range(lbl_len):
            message[label.start + i] = bool(int(bits[i]))
