import array
import datetime
import re
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
from urh.simulator.SimulatorCounterAction import SimulatorCounterAction
from urh.simulator.SimulatorExpressionParser import SimulatorExpressionParser
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.simulator.SimulatorSleepAction import SimulatorSleepAction
from urh.simulator.SimulatorTriggerCommandAction import SimulatorTriggerCommandAction
from urh.simulator.Transcript import Transcript
from urh.util import util, HTMLFormatter
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class Simulator(QObject):
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()

    def __init__(self, simulator_config: SimulatorConfiguration, modulators,
                 expression_parser: SimulatorExpressionParser, project_manager: ProjectManager,
                 sniffer: ProtocolSniffer, sender: EndlessSender):
        super().__init__()
        self.simulator_config = simulator_config
        self.project_manager = project_manager
        self.expression_parser = expression_parser
        self.modulators = modulators  # type: list[Modulator]
        self.backend_handler = BackendHandler()

        self.transcript = Transcript()

        self.current_item = None
        self.last_sent_message = None
        self.is_simulating = False
        self.do_restart = False
        self.current_repeat = 0
        self.log_messages = []

        self.sniffer_ready = False
        self.sender_ready = False
        self.fatal_device_error_occurred = False

        self.verbose = True

        self.sniffer = sniffer
        self.sender = sender

    def __initialize_counters(self):
        for item in self.simulator_config.get_all_items():
            if isinstance(item, SimulatorCounterAction):
                item.reset_value()

    def start(self):
        self.reset()

        self.transcript.clear()
        self.__initialize_counters()

        # start devices
        if self.sniffer:
            self.sniffer.rcv_device.fatal_error_occurred.connect(self.stop_on_error)
            self.sniffer.rcv_device.ready_for_action.connect(self.on_sniffer_ready)

        if self.sender:
            self.sender.device.fatal_error_occurred.connect(self.stop_on_error)
            self.sender.device.ready_for_action.connect(self.on_sender_ready)

        if self.sniffer:
            self.sniffer.sniff()

        if self.sender:
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
            self.log_message("RX is ready to operate")
            self.sniffer_ready = True

    @pyqtSlot()
    def on_sender_ready(self):
        if not self.sender_ready:
            self.log_message("TX is ready to operate")
            self.sender_ready = True

    def stop(self, msg=""):
        self.log_message("Stop simulation: " + "{}".format(msg))
        self.is_simulating = False

        if msg == "Finished":
            # Ensure devices can send their last data before killing them
            time.sleep(0.5)

        # stop devices
        if self.sniffer:
            self.sniffer.stop()

        if self.sender:
            self.sender.stop()

        self.simulation_stopped.emit()

    def restart(self):
        self.transcript.start_new_round()
        self.reset()
        self.log_message("<b>Restarting simulation</b>")

    def reset(self):
        self.sniffer_ready = False
        self.sender_ready = False
        self.fatal_device_error_occurred = False

        if self.sniffer:
            self.sniffer.clear()

        self.current_item = self.simulator_config.rootItem

        for msg in self.simulator_config.get_all_messages():
            msg.send_recv_messages[:] = []

        self.last_sent_message = None
        self.is_simulating = True
        self.do_restart = False
        self.current_repeat = 0
        self.log_messages[:] = []

    @property
    def devices(self):
        result = []
        if self.sniffer is not None:
            result.append(self.sniffer.rcv_device)
        if self.sender is not None:
            result.append(self.sender.device)
        return result

    def device_messages(self) -> list:
        return [device.read_messages() for device in self.devices]

    def read_log_messages(self):
        result = self.log_messages[:]
        self.log_messages.clear()
        return result

    def cleanup(self):
        for device in self.devices:
            if device.backend not in (Backends.none, Backends.network):
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
        for i in range(10):
            if (self.sniffer is None or self.sniffer_ready) and (self.sender is None or self.sender_ready):
                return True
            if self.fatal_device_error_occurred:
                return False
            self.log_message("<i>Waiting for devices</i>")
            time.sleep(1)

        return True

    def __fill_counter_values(self, command: str):
        result = []
        regex = "(item[0-9]+\.counter_value)"
        for token in re.split(regex, command):
            if re.match(regex, token) is not None:
                try:
                    result.append(str(self.simulator_config.item_dict[token].value))
                except (KeyError, ValueError, AttributeError):
                    logger.error("Could not get counter value for " + token)
            else:
                result.append(token)

        return "".join(result)

    def simulate(self):
        self.simulation_started.emit()
        self.is_simulating = self.__wait_for_devices()

        if not self.is_simulating:
            # Simulation may have ended due to device errors
            self.stop("Devices not ready")
            return

        self.log_message("<b>Simulation is running</b>")

        while self.is_simulating and not self.simulation_is_finished():
            if self.current_item is self.simulator_config.rootItem:
                next_item = self.current_item.next()

            elif isinstance(self.current_item, SimulatorProtocolLabel):
                next_item = self.current_item.next()

            elif isinstance(self.current_item, SimulatorMessage):
                self.process_message()
                next_item = self.current_item.next()

            elif isinstance(self.current_item, SimulatorGotoAction):
                next_item = self.current_item.target
                self.log_message("GOTO item " + next_item.index())

            elif isinstance(self.current_item, SimulatorTriggerCommandAction):
                next_item = self.current_item.next()
                command = self.__fill_counter_values(self.current_item.command)
                self.log_message("Calling {}".format(command))
                if self.current_item.pass_transcript:
                    transcript = "\n".join(self.transcript.get_for_all_participants(all_rounds=False))
                    result, rc = util.run_command(command, transcript, use_stdin=True, return_rc=True)
                else:
                    result, rc = util.run_command(command, param=None, detailed_output=True, return_rc=True)
                self.current_item.return_code = rc
                self.log_message(result)

            elif isinstance(self.current_item, SimulatorRule):
                condition = self.current_item.get_first_applying_condition()

                if condition is not None and condition.logging_active and condition.type != ConditionType.ELSE:
                    self.log_message("Rule condition " + condition.index() + " (" + condition.condition + ") applied")

                if condition is not None and condition.child_count() > 0:
                    next_item = condition.children[0]
                else:
                    next_item = self.current_item.next_sibling()

            elif isinstance(self.current_item, SimulatorRuleCondition):
                if self.current_item.type == ConditionType.IF:
                    next_item = self.current_item.parent()
                else:
                    next_item = self.current_item.parent().next_sibling()

            elif isinstance(self.current_item, SimulatorSleepAction):
                self.log_message(self.current_item.caption)
                time.sleep(self.current_item.sleep_time)
                next_item = self.current_item.next()

            elif isinstance(self.current_item, SimulatorCounterAction):
                self.current_item.progress_value()
                self.log_message("Increase counter by {} to {}".format(self.current_item.step, self.current_item.value))
                next_item = self.current_item.next()

            elif self.current_item is None:
                self.current_repeat += 1
                next_item = self.simulator_config.rootItem
                self.transcript.start_new_round()

            else:
                raise ValueError("Unknown action {}".format(type(self.current_item)))

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
            if sender is None:
                self.log_message("Fatal: No sender configured")
                return

            for lbl in new_message.message_type:
                if isinstance(lbl.label, ChecksumLabel):
                    checksum = lbl.label.calculate_checksum_for_message(new_message, use_decoded_bits=False)
                    label_range = new_message.get_label_range(lbl=lbl.label, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    new_message.plain_bits[start:end] = checksum + array.array("B", [0] * (
                            (end - start) - len(checksum)))

            self.transcript.append(msg.source, msg.destination, new_message, msg.index())
            self.send_message(new_message, msg.repeat, sender, msg.modulator_index)
            self.log_message("Sending message " + msg.index())
            self.log_message_labels(new_message)
            msg.send_recv_messages.append(new_message)
            self.last_sent_message = msg
        else:
            # we have to receive a message
            self.log_message("<i>Waiting for message {}</i>".format(msg.index()))
            sniffer = self.sniffer
            if sniffer is None:
                self.log_message("Fatal: No sniffer configured")
                return

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

                check_result, error_msg = self.check_message(received_msg, new_message, retry=retry,
                                                             msg_index=msg.index())

                if check_result:
                    decoded_msg = Message(received_msg.decoded_bits, 0,
                                          received_msg.message_type, decoder=received_msg.decoder)
                    msg.send_recv_messages.append(decoded_msg)
                    self.transcript.append(msg.source, msg.destination, decoded_msg, msg.index())
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
        timestamp = '{0:%b} {0.day} {0:%H}:{0:%M}:{0:%S}.{0:%f}'.format(datetime.datetime.now())

        if isinstance(message, list) and len(message) > 0:
            self.log_messages.append(timestamp + ": " + message[0])
            self.log_messages.extend(message[1:])
        else:
            self.log_messages.append(timestamp + ": " + message)

    def check_message(self, received_msg, expected_msg, retry: int, msg_index: int) -> (bool, str):
        if len(received_msg.decoded_bits) == 0:
            return False, "Failed to decode message {}".format(msg_index)

        for lbl in received_msg.message_type:
            if lbl.value_type_index in (1, 4):
                # get live, random
                continue

            start_recv, end_recv = received_msg.get_label_range(lbl.label, 0, True)
            start_exp, end_exp = expected_msg.get_label_range(lbl.label, 0, False)

            if isinstance(lbl.label, ChecksumLabel):
                expected = lbl.label.calculate_checksum_for_message(received_msg, use_decoded_bits=True)
                start, end = received_msg.get_label_range(lbl.label, 0, True)
                actual = received_msg.decoded_bits[start:end]
            else:
                actual = received_msg.decoded_bits[start_recv:end_recv]
                expected = expected_msg[start_exp:end_exp]

            if actual != expected:
                log_msg = []
                log_msg.append("Attempt for message {} [{}/{}]".format(msg_index, retry + 1,
                                                                       self.project_manager.simulator_retries))
                log_msg.append(HTMLFormatter.indent_string("Mismatch for label: <b>{}</b>".format(lbl.name)))
                expected_str = util.convert_bits_to_string(expected, lbl.label.display_format_index)
                got_str = util.convert_bits_to_string(actual, lbl.label.display_format_index)
                log_msg.append(HTMLFormatter.align_expected_and_got_value(expected_str, got_str, align_depth=2))
                return False, log_msg

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

            log_msg = lbl.name + ": " + HTMLFormatter.monospace(data)
            self.log_messages.append(HTMLFormatter.indent_string(log_msg))

    def resend_last_message(self):
        self.log_message("Resending last message")
        lsm = self.last_sent_message

        if lsm is None:
            return

        sender = self.sender
        self.send_message(lsm.send_recv_messages[-1], lsm.repeat, sender, lsm.modulator_index)

    def send_message(self, message, repeat, sender, modulator_index):
        modulator = self.modulators[modulator_index]
        modulated = modulator.modulate(message.encoded_bits, pause=message.pause)

        curr_repeat = 0

        while curr_repeat < repeat:
            sender.push_data(modulated)
            curr_repeat += 1

    def receive_message(self, sniffer):
        if len(sniffer.messages) > 0:
            return sniffer.messages.pop(0)

        spy = QSignalSpy(sniffer.message_sniffed)
        if spy.wait(self.project_manager.simulator_timeout_ms):
            try:
                return sniffer.messages.pop(0)
            except IndexError:
                self.log_message("Could not receive message")
                return None
        else:
            self.log_message("Receive timeout")
            return None

    def get_full_transcript(self, start=0, use_bit=True):
        result = []
        for source, destination, msg, msg_index in self.transcript[start:]:
            try:
                data = msg.plain_bits_str if use_bit else msg.plain_hex_str
                result.append(self.TRANSCRIPT_FORMAT.format(msg_index, source.shortname, destination.shortname, data))
            except AttributeError:
                result.append("")
        return result

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
                transcript = self.transcript.get_for_participant(template_msg.source
                                                                 if template_msg.source.simulate
                                                                 else template_msg.destination)

                if template_msg.destination.simulate:
                    direction = "->" if template_msg.source.simulate else "<-"
                    transcript += "\n" + direction + new_message.plain_bits_str + "\n"

                cmd = self.__fill_counter_values(lbl.external_program)
                result = util.run_command(cmd, transcript, use_stdin=True)
                if len(result) != lbl.end - lbl.start:
                    log_msg = "Result value of external program {} ({}) does not match label length {}"
                    logger.error(log_msg.format(result, len(result), lbl.end - lbl.start))
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
