import threading
import time
from collections import defaultdict, deque

import sys
from PyQt5.QtTest import QSignalSpy

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import constants, SimulatorSettings
from urh.controller.MainController import MainController
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.MessageType import MessageType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.Participant import Participant
from urh.signalprocessing.SimulatorMessage import SimulatorMessage
from urh.util.SettingsProxy import SettingsProxy
from urh.util.Simulator import Simulator


try:
    from resource import getrusage, RUSAGE_SELF
except ImportError:
    RUSAGE_SELF = 0
    def getrusage(who=0):
        return [0.0, 0.0] # on non-UNIX platforms cpu_time always 0.0

p_stats = None
p_start_time = None

def profiler(frame, event, arg):
    if event not in ('call','return'): return profiler
    #### gather stats ####
    rusage = getrusage(RUSAGE_SELF)
    t_cpu = rusage[0] + rusage[1] # user time + system time
    code = frame.f_code
    fun = (code.co_name, code.co_filename, code.co_firstlineno)
    #### get stack with functions entry stats ####
    ct = threading.currentThread()
    try:
        p_stack = ct.p_stack
    except AttributeError:
        ct.p_stack = deque()
        p_stack = ct.p_stack
    #### handle call and return ####
    if event == 'call':
        p_stack.append((time.time(), t_cpu, fun))
    elif event == 'return':
        try:
            t,t_cpu_prev,f = p_stack.pop()
            assert f == fun
        except IndexError: # TODO investigate
            t,t_cpu_prev,f = p_start_time, 0.0, None
        call_cnt, t_sum, t_cpu_sum = p_stats.get(fun, (0, 0.0, 0.0))
        p_stats[fun] = (call_cnt+1, t_sum+time.time()-t, t_cpu_sum+t_cpu-t_cpu_prev)
    return profiler


def profile_on():
    global p_stats, p_start_time
    p_stats = {}
    p_start_time = time.time()
    threading.setprofile(profiler)
    sys.setprofile(profiler)


def profile_off():
    threading.setprofile(None)
    sys.setprofile(None)

def get_profile_stats():
    """
    returns dict[function_tuple] -> stats_tuple
    where
      function_tuple = (function_name, filename, lineno)
      stats_tuple = (call_cnt, real_time, cpu_time)
    """
    return p_stats


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

        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = 100 * 10**6

        self.network_sdr_plugin_sender = NetworkSDRInterfacePlugin(raw_mode=True)
        self.network_sdr_plugin_receiver = NetworkSDRInterfacePlugin(raw_mode=True)

    def tearDown(self):
        constants.SETTINGS.setValue('rel_symbol_length', self.old_sym_len)  # Restore Symbol Length

    def test_performance(self):
        part_a = Participant("Device A", shortname="A", color_index=0)
        part_b = Participant("Device B", shortname="B", color_index=1)
        part_b.simulate = True

        self.form.project_manager.participants.append(part_a)
        self.form.project_manager.participants.append(part_b)
        self.form.project_manager.project_updated.emit()

        profile = defaultdict(lambda: 0)
        profile["name"] = "Profile"
        profile["device"] = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        profile["bit_length"] = 100
        profile["noise"] = 0.0010
        profile["center"] = 0.0100
        profile["error_tolerance"] = 5
        profile['sample_rate'] = 10 ** 6
        SimulatorSettings.profiles.append(profile)
        self.stc.sim_proto_manager.participants[0].recv_profile = profile
        self.stc.sim_proto_manager.participants[1].send_profile = profile

        msg_a = SimulatorMessage(part_b,
                                 [1, 0] * 16 + [1, 1, 0, 0] * 8 + [0, 0, 1, 1] * 8 + [1, 0, 1, 1, 1, 0, 0, 1, 1, 1] * 4,
                                 100000, MessageType("empty_message_type"), source=part_a)

        msg_b = SimulatorMessage(part_a,
                                 [1, 0] * 16 + [1, 1, 0, 0] * 8 + [1, 1, 0, 0] * 8 + [1, 0, 1, 1, 1, 0, 0, 1, 1, 1] * 4,
                                 100000, MessageType("empty_message_type"), source=part_b)

        self.stc.sim_proto_manager.add_items([msg_a, msg_b], 0, None)
        self.stc.sim_proto_manager.update_active_participants()

        simulator = Simulator(self.stc.sim_proto_manager, self.gtc.modulators, self.stc.sim_expression_parser,
                              self.form.project_manager)

        port = self.__get_free_port()
        sniffer = next(iter(simulator.profile_sniffer_dict.values()))
        sniffer.rcv_device.set_server_port(port)

        self.network_sdr_plugin_sender.client_port = port

        sender = next(iter(simulator.profile_sender_dict.values()))
        sender.device.set_client_port(port + 1)
        sender.device._VirtualDevice__dev.name = "simulator_sender"
        self.network_sdr_plugin_receiver.server_port = port + 1

        self.network_sdr_plugin_receiver.start_tcp_server_for_receiving()
        self.network_sdr_plugin_receiver.server.name = "receiver"

        spy = QSignalSpy(self.network_sdr_plugin_receiver.rcv_index_changed)
        simulator.start()

        modulator = Modulator("test_modulator")
        modulator.samples_per_bit = 100
        modulator.carrier_freq_hz = 55e3
        modulator.modulate(msg_a.encoded_bits)

        t = time.time()
        profile_on()
        self.network_sdr_plugin_sender.send_raw_data(modulator.modulated_samples, 1)
        timeout = spy.wait(1000)
        elapsed = time.time() - t
        profile_off()
        from pprint import pprint
        pprint(get_profile_stats())
        self.assertTrue(timeout)
        self.assertGreater(self.network_sdr_plugin_receiver.current_receive_index, 0)
        self.assertLess(elapsed, 0.2)

    def __get_free_port(self):
        import socket
        s = socket.socket()
        s.bind(("", 0))
        port = s.getsockname()[1]
        s.close()
        return port
