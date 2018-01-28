import array
import datetime
import threading
import time

import numpy
from PyQt5.QtCore import QEventLoop, QTimer, pyqtSignal, QObject, pyqtSlot

from urh.simulator.SimulatorConfiguration import SimulatorConfiguration
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.EndlessSender import EndlessSender
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.simulator.SimulatorExpressionParser import SimulatorExpressionParser
from urh.simulator.SimulatorGotoAction import SimulatorGotoAction
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.simulator.SimulatorRule import SimulatorRule, SimulatorRuleCondition, ConditionType
from urh.util.Logger import logger
from urh.util.ProjectManager import ProjectManager


class Simulator(QObject):
    simulation_started = pyqtSignal()
    simulation_stopped = pyqtSignal()
    stopping_simulation = pyqtSignal()

    def __init__(self, protocol_manager: SimulatorConfiguration, modulators,
                 expression_parser: SimulatorExpressionParser, project_manager: ProjectManager,
                 sniffer: ProtocolSniffer, sender: EndlessSender):
        super().__init__()
        self.protocol_manager = protocol_manager
        self.project_manager = project_manager
        self.expression_parser = expression_parser
        self.modulators = modulators  # type: list[Modulator]
        self.backend_handler = BackendHandler()

        self.current_item = None
        self.last_sent_message = None
        self.is_simulating = False
        self.do_restart = False
        self.current_repeat = 0
        self.messages = []

        self.sniffer_ready = False
        self.sender_ready = False
        self.fatal_device_error_occurred = False

        self.measure_started = False
        self.time = None

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

    @pyqtSlot(str)
    def stop_on_error(self, msg: str):
        self.fatal_device_error_occurred = True
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
        if not self.is_simulating:
            return

        self.log_message("Stop simulation ..." + "{}".format(msg))
        self.is_simulating = False

        self.stopping_simulation.emit()

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
        self.messages[:] = []
        self.measure_started = False

    @property
    def devices(self):
        result = [self.sniffer.rcv_device, self.sender.device]
        return result

    def device_messages(self):
        messages = ""

        for device in self.devices:
            new_messages = device.read_messages()
            if new_messages:
                messages += new_messages

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
            time.sleep(0.5)

    def simulate(self):
        self.simulation_started.emit()
        self.__wait_for_devices()

        if not self.is_simulating:
            # Simulation may have ended due to device errors
            self.stop("Devices not ready")
            return

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

                next_item = true_cond.children[
                    0] if true_cond is not None and true_cond.child_count() else self.current_item.next_sibling()
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

        if msg.participant is None:
            return

        new_message = self.generate_message_from_template(msg)

        if msg.participant.simulate:
            # we have to send a message ...
            sender = self.sender

            for lbl in new_message.message_type:
                if lbl.value_type_index == 4:
                    # random value
                    result = numpy.random.randint(lbl.random_min, lbl.random_max + 1)
                    self.set_label_value(new_message, lbl, result)

            for lbl in new_message.message_type:
                if isinstance(lbl.label, ChecksumLabel):
                    checksum = lbl.label.calculate_checksum_for_message(new_message, use_decoded_bits=False)
                    label_range = new_message.get_label_range(lbl=lbl.label, view=0, decode=False)
                    start, end = label_range[0], label_range[1]
                    new_message.plain_bits[start:end] = checksum + array.array("B", [0] * (
                            (end - start) - len(checksum)))

            self.send_message(new_message, msg.repeat, sender, msg.modulator_index)
            self.log_message("Sending message " + msg.index())
            self.log_message_labels(new_message)
            msg.send_recv_messages.append(new_message)
            self.last_sent_message = msg
        else:
            # we have to receive a message ...
            self.log_message("Waiting for message " + msg.index() + " ...")
            sniffer = self.sniffer
            retry = 0

            while self.is_simulating \
                    and not self.simulation_is_finished() \
                    and retry < self.project_manager.simulator_retries:
                received_msg = self.receive_message(sniffer)

                if not self.is_simulating:
                    return

                if received_msg is None:
                    if self.project_manager.simulator_error_handling_index == 0:
                        # resend last message
                        self.resend_last_message()

                        # and try again ...
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

                if (
                        not self.measure_started) and received_msg.decoded_bits_str == "10101010100111010101000010010000000110001100010011011101011100000000100011111011":
                    self.measure_started = True
                    self.time = time.perf_counter()

                if self.measure_started and received_msg.decoded_bits_str == "101010101001110100100000010000000000111001000000000100000000100110000000001000000000010101011011":
                    self.measure_started = False

                check_result = self.check_message(received_msg, new_message)

                if check_result:
                    decoded_msg = Message(received_msg.decoded_bits, 0,
                                          received_msg.message_type, decoder=received_msg.decoder)
                    msg.send_recv_messages.append(decoded_msg)
                    self.log_message("Received message " + msg.index() + ": ")
                    self.log_message_labels(decoded_msg)
                    return

                retry += 1

            if retry == self.project_manager.simulator_retries:
                self.log_message("Message " + msg.index() + " not received")
                self.stop()

    def log_message(self, message):
        now = datetime.datetime.now()
        timestamp = '{0:%b} {0.day} {0:%H}:{0:%M}:{0:%S}.{0:%f}'.format(now)
        self.messages.append(timestamp + ": " + message)

    def check_message(self, received_msg, expected_msg):
        # do we have a crc label?
        crc_label = next((lbl.label for lbl in received_msg.message_type if isinstance(lbl.label, ChecksumLabel)), None)

        #      if crc_label is not None:
        #          checksum = crc_label.calculate_checksum_for_message(received_msg, use_decoded_bits=True)
        #          start, end = received_msg.get_label_range(crc_label, 0, True)

        #           if checksum != received_msg.decoded_bits[start:end]:
        # checksum wrong ...
        #               return False

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
                    value = message.plain_ascii_str[start:end]
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
        msg = None
        loop = QEventLoop()
        sniffer.qt_signals.data_sniffed.connect(loop.quit)
        self.stopping_simulation.connect(loop.quit)

        timer = QTimer()
        timer.setSingleShot(True)
        timer.timeout.connect(loop.quit)
        timer.start(self.project_manager.simulator_timeout * 1000)

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
