from urh.SimulatorProtocolManager import SimulatorProtocolManager
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.util.ProjectManager import ProjectManager
from urh.dev.BackendHandler import BackendHandler
from urh.dev.EndlessSender import EndlessSender

from urh import SettingsSimulator

class Simulator(object):
    def __init__(self, protocol_manager: SimulatorProtocolManager, project_manager: ProjectManager):
        self.protocol_manager = protocol_manager
        self.project_manager = project_manager
        self.backend_handler = BackendHandler()

        self.profile_sniffer_dict = {}
        self.profile_sender_dict = {}

        self.init_devices()

    def init_devices(self):
        for participant in project_manager.participants:
            if not participant.simulate:
                continue

            recv_profile = participant.recv_profile

            if recv_profile not in self.profile_sniffer_dict:
                bit_length = recv_profile['bit_length']
                center = recv_profile['center']
                noise = recv_profile['noise']
                tolerance = recv_profile['error_tolerance']
                modulation = recv_profile['modulation']
                device = recv_profile['device']

                sniffer = ProtocolSniffer(bit_length, center, noise, tolerance,
                                          modulation, device, self.backend_handler)

                self.load_device_parameter(sniffer.rcv_device, recv_profile, is_rx=True)
                self.profile_sniffer_dict[recv_profile] = sniffer

            send_profile = participant.send_profile

            if send_profile not in self.profile_sender_dict:
                device = send_profile['device']

                sender = EndlessSender(self.backend_handler, device)

                self.load_device_parameter(sender.device, send_profile, is_rx=False)
                self.profile_sender_dict[send_profile]

    def load_device_parameter(device, profile, is_rx):
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