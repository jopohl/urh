import time

import numpy as np
from PyQt5.QtTest import QTest

from tests.QtTestCase import QtTestCase
from urh import settings
from urh.dev.BackendHandler import BackendHandler
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import (
    NetworkSDRInterfacePlugin,
)
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.signalprocessing.Signal import Signal
from urh.util import util


class TestProtocolSniffer(QtTestCase):
    def setUp(self):
        super().setUp()
        settings.OVERWRITE_RECEIVE_BUFFER_SIZE = 50000

    def test_protocol_sniffer(self):
        samples_per_symbol = 100
        center = 0.0942
        noise = 0.1
        tolerance = 2
        modulation_type = "FSK"
        sample_rate = 1e6
        device_name = NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        sniffer = ProtocolSniffer(
            samples_per_symbol=samples_per_symbol,
            center=center,
            center_spacing=0.1,
            noise=noise,
            tolerance=tolerance,
            modulation_type=modulation_type,
            bits_per_symbol=1,
            device=device_name,
            backend_handler=BackendHandler(),
            network_raw_mode=True,
        )

        port = util.get_free_port()
        sniffer.rcv_device.set_server_port(port)

        self.network_sdr_plugin_sender = NetworkSDRInterfacePlugin(raw_mode=True)
        self.network_sdr_plugin_sender.client_port = port

        sniffer.sniff()
        QTest.qWait(10)

        data = ["101010", "000111", "1111000"]
        pause = 10 * samples_per_symbol
        modulator = Modulator("test")
        modulator.samples_per_symbol = samples_per_symbol
        modulator.sample_rate = sample_rate
        modulator.modulation_type = modulation_type
        modulator.parameters[1] = 20e3
        modulator.parameters[0] = 10e3

        packages = []
        for d in data:
            packages.append(modulator.modulate(list(map(int, d)), pause))

        # verify modulation was correct
        pa = ProtocolAnalyzer(None)
        signal = Signal("", "", sample_rate=sample_rate)
        signal.iq_array = IQArray.concatenate(packages)
        signal.modulation_type = modulation_type
        signal.samples_per_symbol = samples_per_symbol
        signal.tolerance = tolerance
        signal.noise_threshold = noise
        signal.center = center
        pa.signal = signal
        pa.get_protocol_from_signal()
        self.assertEqual(pa.plain_bits_str, data)

        # send data
        send_data = IQArray.concatenate(packages)
        self.network_sdr_plugin_sender.send_raw_data(send_data, 1)
        time.sleep(1)

        # Send enough pauses to end sniffing
        self.network_sdr_plugin_sender.send_raw_data(
            IQArray(None, np.float32, 10 * 2 * samples_per_symbol), 1
        )
        time.sleep(1)

        sniffer.stop()
        self.assertEqual(sniffer.plain_bits_str, data)
