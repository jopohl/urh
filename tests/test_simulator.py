import os
import socket
import sys
import tempfile
import time

import numpy as np
# import yappi
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file, wait_for_sniffer_message_received
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.ChecksumLabel import ChecksumLabel
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal
from urh.simulator.ActionItem import TriggerCommandActionItem, SleepActionItem, CounterActionItem
from urh.simulator.SimulatorProtocolLabel import SimulatorProtocolLabel
from urh.util.SettingsProxy import SettingsProxy


class TestSimulator(QtTestCase):
    TIMEOUT = 1.0

    def setUp(self):
        super().setUp()
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
        simulator = dialog.simulator
        simulator.sniffer.rcv_device.set_server_port(port)

        port = self.get_free_port()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.bind(("", port))
        s.listen(1)

        simulator.sender.device.set_client_port(port)
        dialog.ui.btnStartStop.click()

        QTest.qWait(500)

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
        time.sleep(self.TIMEOUT)
        current_item = simulator.current_item
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)

        if wait_for_sniffer_message_received(simulator.sniffer, timeout_ms=10e3):
            while current_item == simulator.current_item:
                time.sleep(self.TIMEOUT)  # wait till simulator processes message
        else:
            return

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
        time.sleep(self.TIMEOUT)
        current_item = simulator.current_item
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)
        if wait_for_sniffer_message_received(simulator.sniffer, timeout_ms=10e3):
            while current_item == simulator.current_item:
                time.sleep(self.TIMEOUT)  # wait till simulator processes message
        else:
            return

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
        time.sleep(self.TIMEOUT)
        current_item = simulator.current_item
        self.alice.send_raw_data(np.zeros(self.num_zeros_for_pause, dtype=np.complex64), 1)
        if wait_for_sniffer_message_received(simulator.sniffer, timeout_ms=10e3):
            while current_item == simulator.current_item:
                time.sleep(self.TIMEOUT)  # wait till simulator processes message
        else:
            return

        bits = self.__demodulate(conn)
        self.assertEqual(len(bits), 1)
        bits = bits[0]
        self.assertTrue(bits.startswith(preamble_str + sync_str))
        bits = bits.replace(preamble_str + sync_str, "")
        self.assertEqual(int(bits, 2), seq_num + 5)

        conn.close()
        s.close()

    def __demodulate(self, connection):
        data = connection.recv(65536)
        if len(data) % 8 != 0:
            data += connection.recv(65536)

        arr = np.array(np.frombuffer(data, dtype=np.complex64))
        signal = Signal("", "")
        signal._fulldata = arr
        pa = ProtocolAnalyzer(signal)
        pa.get_protocol_from_signal()
        return pa.plain_bits_str
