import numpy as np
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from urh.dev.BackendHandler import BackendHandler
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.signalprocessing.Signal import Signal
from urh.util.SettingsProxy import SettingsProxy


class TestProtocolSniffer(QtTestCase):
    def setUp(self):
        super().setUp()
        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = 100 * 10 ** 6

    def test_protocol_sniffer(self):
        bit_len = 100
        center = 0.0942
        noise = 0.1
        tolerance = 2
        modulation_type = 1
        sample_rate = 1e6
        device_name = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        sniffer = ProtocolSniffer(bit_len=bit_len, center=center, noise=noise, tolerance=tolerance,
                                  modulation_type=modulation_type, device=device_name, backend_handler=BackendHandler(),
                                  network_raw_mode=True)

        port = self.get_free_port()
        sniffer.rcv_device.set_server_port(port)

        self.network_sdr_plugin_sender = NetworkSDRInterfacePlugin(raw_mode=True)
        self.network_sdr_plugin_sender.client_port = port

        sniffer.sniff()
        QTest.qWait(10)

        data = ["101010", "000111", "1111000"]
        pause = 10 * bit_len
        modulator = Modulator("test")
        modulator.samples_per_bit = bit_len
        modulator.sample_rate = sample_rate
        modulator.modulation_type = modulation_type
        modulator.param_for_one = 20e3
        modulator.param_for_zero = 10e3

        packages = []
        for d in data:
            packages.append(modulator.modulate(list(map(int, d)), pause))

        # verify modulation was correct
        pa = ProtocolAnalyzer(None)
        signal = Signal("", "", sample_rate=sample_rate)
        signal._fulldata = np.concatenate(packages)
        signal.modulation_type = modulation_type
        signal.bit_len = bit_len
        signal.tolerance = tolerance
        signal.noise_threshold = noise
        signal.qad_center = center
        pa.signal = signal
        pa.get_protocol_from_signal()
        self.assertEqual(pa.plain_bits_str, data)

        # send data
        send_data = np.concatenate(packages)
        chunk_size = 128
        for i in range(0, len(send_data), chunk_size):
            self.network_sdr_plugin_sender.send_raw_data(send_data[i:i + chunk_size], 1)
            QTest.qWait(10)

        # Send enough pauses to end sniffing
        for i in range(10):
            self.network_sdr_plugin_sender.send_raw_data(np.zeros(bit_len, dtype=np.complex64), 1)
            QTest.qWait(10)

        sniffer.stop()
        self.assertEqual(sniffer.plain_bits_str, data)

        # needed to prevent crash on windows
        QTest.qWait(10)
