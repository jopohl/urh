import unittest
import time
import tests.utils_testing
from collections import defaultdict
from tests.QtTestCase import QtTestCase
from urh import constants
from urh.controller.MainController import MainController
from urh.ui.SimulatorScene import RuleItem
from urh.ui.SimulatorScene import ParticipantItem
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin

from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.Message import Message
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh import SimulatorSettings
from urh.util.Simulator import Simulator

from PyQt5.QtWidgets import QMenu
from PyQt5.QtTest import QSignalSpy

from tests.utils_testing import get_path_for_data_file


class TestSimulator(QtTestCase):
    def setUp(self):
        self.old_sym_len = constants.SETTINGS.value('rel_symbol_length', type=int)
        constants.SETTINGS.setValue('rel_symbol_length', 0)  # Disable Symbols for this Test

        self.form = MainController()
        self.cfc = self.form.compare_frame_controller
        self.stc = self.form.simulator_tab_controller
        self.gtc = self.form.generator_tab_controller

        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.sframe = self.form.signal_tab_controller.signal_frames[0]
        self.sim_frame = self.form.simulator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(3)
        self.cfc.proto_analyzer.auto_assign_labels()

        self.network_sdr_plugin_a = NetworkSDRInterfacePlugin(raw_mode=True)
        self.network_sdr_plugin_b = NetworkSDRInterfacePlugin(raw_mode=True)

    def tearDown(self):
        constants.SETTINGS.setValue('rel_symbol_length', self.old_sym_len) # Restore Symbol Length

    def test_performance(self):
        part_a = Participant("Device ABBA", shortname="A", color_index=0)
        part_b = Participant("Device B", shortname="B", color_index=1)
        part_b.simulate = True

        self.form.project_manager.participants.append(part_a)
        self.form.project_manager.participants.append(part_b)
        self.form.project_manager.project_updated.emit()

        profile = defaultdict(lambda: 0)
        profile["name"] = "Profile"
        profile["device"] = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        SimulatorSettings.profiles.append(profile)
        self.stc.sim_proto_manager.participants[0].recv_profile = profile
        self.stc.sim_proto_manager.participants[1].send_profile = profile

        msg_a = SimulatorMessage(part_b, [1, 0] * 16 + [1, 1, 0, 0] * 8 + [0,0,1,1]*8 + [1,0,1,1,1,0,0,1,1,1]*4,
                                   100000, MessageType("empty_message_type"), source=part_a)

        msg_b = SimulatorMessage(part_a, [1, 0] * 16 + [1, 1, 0, 0] * 8 + [1,1,0,0]*8 + [1,0,1,1,1,0,0,1,1,1]*4,
                                   100000, MessageType("empty_message_type"), source=part_b)

        self.stc.sim_proto_manager.add_items([msg_a, msg_b], 0, None)
        self.stc.sim_proto_manager.update_active_participants()

        simulator = Simulator(self.stc.sim_proto_manager, self.gtc.modulators, self.stc.sim_expression_parser,
                                self.form.project_manager)

        port = self.__get_free_port()
        sniffer = next (iter (simulator.profile_sniffer_dict.values()))
        sniffer.rcv_device.set_server_port(port)

        self.network_sdr_plugin_a.client_port = port

        sender = next (iter (simulator.profile_sender_dict.values()))
        sender.device.set_client_port(port + 1)
        self.network_sdr_plugin_b.server_port = port + 1

        spy = QSignalSpy(self.network_sdr_plugin_b.rcv_index_changed)
        simulator.start()

        modulator = Modulator("test_modulator")
        modulator.samples_per_bit = 100
        modulator.carrier_freq_hz = 55e3
        modulator.modulate(msg_a.encoded_bits)

        t = time.time()
        self.network_sdr_plugin_a.send_raw_data(modulator.modulated_samples, 1)
        #self.network_sdr_plugin_a.start_message_sending_thread([msg_a], [1e6])
        timeout = spy.wait(SimulatorSettings.timeout * 1000)
        elapsed = time.time() - t
        self.assertFalse(timeout)
        self.assertLess(elapsed, 0.2)

    def __get_free_port(self):
        import socket
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
