import time
import unittest

from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from urh.signalprocessing.Signal import Signal


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.prefix = "[PERF] "

    # Testmethode muss immer mit Präfix test_* starten
    def test_fabema_autodetect(self):
        total = time.time()
        t = time.time()
        signal = Signal("../../noack/USRP/Fabema/Testdata/trafficlight_fhside_full.complex", "PerfTest",
                        modulation="ASK")
        # signal.noise_treshold = 0.2377
        print(self.prefix + "Signal creation: {0:.2f} ({1:.2f})".format(time.time() - t, time.time() - total))
        t = time.time()
        signal.qad_center = signal.estimate_qad_center()
        print(self.prefix + "Quad Center Estimation: {0:.2f} ({1:.2f})".format(time.time() - t, time.time() - total))

        t = time.time()
        signal.bit_len = signal.estimate_bitlen()
        print(self.prefix + "Bit Len Estimation: {0:.2f} ({1:.2f})".format(time.time() - t, time.time() - total))

    def test_fabema_get_proto(self):
        signal = Signal("../../noack/USRP/Fabema/Testdata/trafficlight_fhside_full.complex", "PerfTest",
                        modulation="ASK")
        signal.noise_treshold = 0.1
        signal.qad_center = 0.009
        signal.bit_len = 16
        proto_analyzer = ProtocolAnalyzer(signal)
        t = time.time()
        proto_analyzer.get_protocol_from_signal()
        dur = time.time() - t
        print(self.prefix + "Get Protocol: {0:.2f}s".format(dur))
        self.assertLess(dur, 2.85)

    def test_fabema_many_messages(self):
        signal = Signal("../../noack/USRP/Fabema/Testdata/trafficlight_fhside_full.complex", "PerfTest",
                        modulation="ASK")
        signal.noise_treshold = 0.1
        signal.qad_center = -0.0249
        signal.bit_len = 1
        proto_analyzer = ProtocolAnalyzer(signal)
        t = time.time()
        proto_analyzer.get_protocol_from_signal()
        print("Got protocol", time.time() - t)

        t = time.time()
        proto_analyzer.plain_to_string(0)
        total = time.time() - t
        print("First run", total)

        t = time.time()
        proto_analyzer.plain_to_string(0)
        total = time.time() - t
        print("With cached", total)

        print("Num Messages", proto_analyzer.num_messages)
