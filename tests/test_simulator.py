import os
import socket
import tempfile
import time
from multiprocessing import Process, Value

import numpy as np
# import yappi
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.controller.MainController import MainController
from urh.dev.BackendHandler import BackendHandler
from urh.dev.EndlessSender import EndlessSender
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.signalprocessing.Signal import Signal
from urh.simulator.ActionItem import TriggerCommandActionItem, SleepActionItem, CounterActionItem
from urh.simulator.Simulator import Simulator
from urh.simulator.SimulatorMessage import SimulatorMessage
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.util.Logger import logger
from urh.util.SettingsProxy import SettingsProxy


def receive(port, current_index, target_index, elapsed):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.bind(("", port))
    s.listen(1)

    conn, addr = s.accept()
    logger.debug('Receiver got connection from address:'.format(addr))

    start = False
    while True:
        data = conn.recv(65536 * 8)
        if not start:
            start = True
            t = time.time()

        if len(data) > 0:
            while len(data) % 8 != 0:
                data += conn.recv(len(data) % 8)

            arr = np.frombuffer(data, dtype=np.complex64)
            current_index.value += len(arr)

        if current_index.value == target_index:
            break

    conn.close()
    elapsed.value = 1000 * (time.time() - t)
    s.close()


class TestSimulator(QtTestCase):
    def setUp(self):
        super().setUp()
        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = 100 * 10 ** 6

    def test_performance(self):
        self.form = MainController()
        self.cfc = self.form.compare_frame_controller
        self.stc = self.form.simulator_tab_controller
        self.gtc = self.form.generator_tab_controller

        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.sim_frame = self.form.simulator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(3)
        self.cfc.proto_analyzer.auto_assign_labels()

        self.network_sdr_plugin_sender = NetworkSDRInterfacePlugin(raw_mode=True)

        part_a = Participant("Device A", shortname="A", color_index=0)
        part_b = Participant("Device B", shortname="B", color_index=1)
        part_b.simulate = True

        self.form.project_manager.participants.append(part_a)
        self.form.project_manager.participants.append(part_b)
        self.form.project_manager.project_updated.emit()

        sniffer = ProtocolSniffer(100, 0.01, 0.1, 5, 1, NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, BackendHandler(),
                                  network_raw_mode=True)
        sender = EndlessSender(BackendHandler(), NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        simulator = Simulator(self.stc.simulator_config, self.gtc.modulators, self.stc.sim_expression_parser,
                              self.form.project_manager, sniffer=sniffer, sender=sender)

        pause = 100000
        msg_a = SimulatorMessage(part_b,
                                 [1, 0] * 16 + [1, 1, 0, 0] * 8 + [0, 0, 1, 1] * 8 + [1, 0, 1, 1, 1, 0, 0, 1, 1, 1] * 4,
                                 pause=pause, message_type=MessageType("empty_message_type"), source=part_a)

        msg_b = SimulatorMessage(part_a,
                                 [1, 0] * 16 + [1, 1, 0, 0] * 8 + [1, 1, 0, 0] * 8 + [1, 0, 1, 1, 1, 0, 0, 1, 1, 1] * 4,
                                 pause=pause, message_type=MessageType("empty_message_type"), source=part_b)

        self.stc.simulator_config.add_items([msg_a, msg_b], 0, None)
        self.stc.simulator_config.update_active_participants()

        port = self.get_free_port()
        sniffer = simulator.sniffer
        sniffer.rcv_device.set_server_port(port)

        self.network_sdr_plugin_sender.client_port = port

        sender = simulator.sender
        port = self.get_free_port()
        sender.device.set_client_port(port)
        sender.device._VirtualDevice__dev.name = "simulator_sender"

        current_index = Value("L")
        elapsed = Value("f")
        target_num_samples = 113600 - pause
        receive_process = Process(target=receive, args=(port, current_index, target_num_samples, elapsed))
        receive_process.daemon = True
        receive_process.start()

        # Ensure receiver is running
        time.sleep(2)

        # spy = QSignalSpy(self.network_sdr_plugin_receiver.rcv_index_changed)
        simulator.start()

        modulator = Modulator("test_modulator")
        modulator.samples_per_bit = 100
        modulator.carrier_freq_hz = 55e3

        # yappi.start()

        self.network_sdr_plugin_sender.send_raw_data(modulator.modulate(msg_a.encoded_bits), 1)
        QTest.qWait(10)
        # send some zeros to simulate the end of a message
        self.network_sdr_plugin_sender.send_raw_data(np.zeros(100000, dtype=np.complex64), 1)
        QTest.qWait(100)
        receive_process.join(10)

        logger.info("PROCESS TIME: {0:.2f}ms".format(elapsed.value))

        self.assertEqual(current_index.value, target_num_samples)
        self.assertLess(elapsed.value, 200)

        # timeout = spy.wait(2000)
        # yappi.get_func_stats().print_all()
        # yappi.get_thread_stats().print_all()

    def test_simulation_flow(self):
        """
        test a simulation flow with an increasing sequence number

        :return:
        """
        profile = self.get_path_for_filename("testprofile.sim.xml")
        self.form.add_files([profile])
        self.assertEqual(len(self.form.simulator_tab_controller.simulator_scene.get_all_message_items()), 6)

        port = self.get_free_port()
        self.alice = NetworkSDRInterfacePlugin(raw_mode=True)
        self.alice.client_port = port

        dialog = self.form.simulator_tab_controller.get_simulator_dialog()
        name = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        dialog.device_settings_rx_widget.ui.cbDevice.setCurrentText(name)
        dialog.device_settings_tx_widget.ui.cbDevice.setCurrentText(name)
        QTest.qWait(10)
        simulator = dialog.simulator
        simulator.sniffer.rcv_device.set_server_port(port)

        port = self.get_free_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(("", port))
        s.listen(1)
        QTest.qWait(10)

        simulator.sender.device.set_client_port(port)
        dialog.ui.btnStartStop.click()
        QTest.qWait(1500)

        conn, addr = s.accept()

        msg = next(msg for msg in dialog.simulator_config.get_all_messages() if msg.source.name == "Alice")
        checksum_label = next(lbl for lbl in msg.message_type if lbl.is_checksum_label).label  # type: ChecksumLabel

        modulator = dialog.project_manager.modulators[0]  # type: Modulator
        preamble_str = "10101010"
        sync_str = "1001"
        preamble = list(map(int, preamble_str))
        sync = list(map(int, sync_str))
        seq = list(map(int, "00000010"))
        data = list(map(int, "11001101"))

        seq_num = int("".join(map(str, seq)), 2)

        checksum = list(checksum_label.calculate_checksum(seq + data))

        msg1 = preamble + sync + seq + data + checksum

        self.alice.send_raw_data(modulator.modulate(msg1), 1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(100000, dtype=np.complex64), 1)
        QTest.qWait(100)

        bits = self.__demodulate(conn)
        self.assertEqual(len(bits), 1)
        bits = bits[0]
        self.assertTrue(bits.startswith(preamble_str + sync_str))
        bits = bits.replace(preamble_str + sync_str, "")
        self.assertEqual(int(bits, 2), seq_num + 1)

        seq = list(map(int, "{0:08b}".format(seq_num + 2)))
        checksum = list(checksum_label.calculate_checksum(seq + data))
        msg2 = preamble + sync + seq + data + checksum

        self.alice.send_raw_data(modulator.modulate(msg2), 1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(100000, dtype=np.complex64), 1)
        QTest.qWait(100)

        bits = self.__demodulate(conn)
        self.assertEqual(len(bits), 1)
        bits = bits[0]
        self.assertTrue(bits.startswith(preamble_str + sync_str))
        bits = bits.replace(preamble_str + sync_str, "")
        self.assertEqual(int(bits, 2), seq_num + 3)

        seq = list(map(int, "{0:08b}".format(seq_num + 4)))
        checksum = list(checksum_label.calculate_checksum(seq + data))
        msg3 = preamble + sync + seq + data + checksum

        self.alice.send_raw_data(modulator.modulate(msg3), 1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(100000, dtype=np.complex64), 1)
        QTest.qWait(100)

        bits = self.__demodulate(conn)
        self.assertEqual(len(bits), 1)
        bits = bits[0]
        self.assertTrue(bits.startswith(preamble_str + sync_str))
        bits = bits.replace(preamble_str + sync_str, "")
        self.assertEqual(int(bits, 2), seq_num + 5)

        QTest.qWait(100)
        self.assertTrue(simulator.simulation_is_finished())

        conn.close()
        s.close()

        QTest.qWait(100)

    def test_external_program_simulator(self):
        stc = self.form.simulator_tab_controller
        stc.ui.btnAddParticipant.click()
        stc.ui.btnAddParticipant.click()

        stc.simulator_scene.add_counter_action(None, 0)
        action = next(item for item in stc.simulator_scene.items() if isinstance(item, CounterActionItem))
        action.model_item.start = 3
        action.model_item.step = 2
        counter_item_str = "item" + str(action.model_item.index()) + ".counter_value"

        stc.ui.gvSimulator.add_empty_message(42)
        stc.ui.gvSimulator.add_empty_message(42)

        stc.ui.cbViewType.setCurrentIndex(0)
        stc.create_simulator_label(0, 10, 20)
        stc.create_simulator_label(1, 10, 20)

        messages = stc.simulator_config.get_all_messages()
        messages[0].source = stc.project_manager.participants[0]
        messages[0].destination = stc.project_manager.participants[1]
        messages[0].destination.simulate = True
        messages[1].source = stc.project_manager.participants[1]
        messages[1].destination = stc.project_manager.participants[0]

        stc.simulator_scene.add_trigger_command_action(None, 200)
        stc.simulator_scene.add_sleep_action(None, 200)

        lbl1 = messages[0].message_type[0]  # type: SimulatorProtocolLabel
        lbl2 = messages[1].message_type[0]  # type: SimulatorProtocolLabel

        lbl1.value_type_index = 3
        lbl1.external_program = get_path_for_data_file("external_program_simulator.py") + " " + counter_item_str
        lbl2.value_type_index = 3
        lbl2.external_program = get_path_for_data_file("external_program_simulator.py") + " " + counter_item_str

        action = next(item for item in stc.simulator_scene.items() if isinstance(item, SleepActionItem))
        action.model_item.sleep_time = 0.001
        stc.simulator_scene.clearSelection()
        action = next(item for item in stc.simulator_scene.items() if isinstance(item, TriggerCommandActionItem))
        action.setSelected(True)
        self.assertEqual(stc.ui.detail_view_widget.currentIndex(), 4)
        fname = tempfile.mktemp()
        self.assertFalse(os.path.isfile(fname))
        external_command = "cmd.exe /C copy NUL {}".format(fname) if os.name == "nt" else "touch {}".format(fname)
        stc.ui.lineEditTriggerCommand.setText(external_command)
        self.assertEqual(action.model_item.command, external_command)

        port = self.get_free_port()
        self.alice = NetworkSDRInterfacePlugin(raw_mode=True)
        self.alice.client_port = port

        dialog = stc.get_simulator_dialog()
        name = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        dialog.device_settings_rx_widget.ui.cbDevice.setCurrentText(name)
        dialog.device_settings_tx_widget.ui.cbDevice.setCurrentText(name)
        QTest.qWait(10)
        simulator = dialog.simulator
        simulator.sniffer.rcv_device.set_server_port(port)

        port = self.get_free_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(("", port))
        s.listen(1)
        QTest.qWait(10)

        simulator.sender.device.set_client_port(port)
        dialog.ui.btnStartStop.click()
        QTest.qWait(1500)

        conn, addr = s.accept()

        modulator = dialog.project_manager.modulators[0]  # type: Modulator

        self.alice.send_raw_data(modulator.modulate("10" * 42), 1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(100000, dtype=np.complex64), 1)
        QTest.qWait(500)

        bits = self.__demodulate(conn)
        self.assertEqual(bits[0], "101010101")
        self.assertTrue(simulator.simulation_is_finished())

        conn.close()
        s.close()

        QTest.qWait(100)

        self.assertTrue(os.path.isfile(fname))

    def __demodulate(self, connection):
        data = connection.recv(65536)
        while len(data) % 8 != 0:
            data += connection.recv(65536)

        arr = np.array(np.frombuffer(data, dtype=np.complex64))
        signal = Signal("", "")
        signal._fulldata = arr
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        return pa.plain_bits_str
