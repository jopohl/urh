import os
import socket
import sys
import tempfile
import time

import numpy as np
# import yappi
from PyQt5.QtTest import QTest
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.simulator.ActionItem import TriggerCommandActionItem, SleepActionItem, CounterActionItem
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.util.SettingsProxy import SettingsProxy


class TestSimulator(QtTestCase):
    def setUp(self):
        super().setUp()
        ProtocolSniffer.BUFFER_SIZE_MB = 1
        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = 50000

        self.num_zeros_for_pause = 1000

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
        QTest.qWait(100)
        simulator = dialog.simulator
        simulator.sniffer.rcv_device.set_server_port(port)

        port = self.get_free_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(("", port))
        s.listen(1)
        QTest.qWait(100)

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
        time.sleep(1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)

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
        time.sleep(1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)

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
        time.sleep(1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)

        bits = self.__demodulate(conn)
        self.assertEqual(len(bits), 1)
        bits = bits[0]
        self.assertTrue(bits.startswith(preamble_str + sync_str))
        bits = bits.replace(preamble_str + sync_str, "")
        self.assertEqual(int(bits, 2), seq_num + 5)

        time.sleep(1)

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

        ext_program = get_path_for_data_file("external_program_simulator.py") + " " + counter_item_str
        if sys.platform == "win32":
            ext_program = sys.executable + " " + ext_program

        lbl1.value_type_index = 3
        lbl1.external_program = ext_program
        lbl2.value_type_index = 3
        lbl2.external_program = ext_program

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
        QTest.qWait(100)
        simulator = dialog.simulator
        simulator.sniffer.rcv_device.set_server_port(port)

        port = self.get_free_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(("", port))
        s.listen(1)
        QTest.qWait(100)

        simulator.sender.device.set_client_port(port)
        dialog.ui.btnStartStop.click()
        QTest.qWait(1500)

        conn, addr = s.accept()

        modulator = dialog.project_manager.modulators[0]  # type: Modulator

        self.alice.send_raw_data(modulator.modulate("100"+"10101010"*42), 1)
        time.sleep(1)
        QTest.qWait(100)
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)

        bits = self.__demodulate(conn)
        self.assertEqual(bits[0].rstrip("0"), "101010101")

        time.sleep(1)
        conn.close()
        s.close()

        QTest.qWait(100)

        self.assertTrue(os.path.isfile(fname))

    def __demodulate(self, connection):
        QTest.qWait(100)
        data = connection.recv(65536)
        while len(data) % 8 != 0:
            data += connection.recv(65536)

        arr = np.array(np.frombuffer(data, dtype=np.complex64))
        signal = Signal("", "")
        signal._fulldata = arr
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        return pa.plain_bits_str
