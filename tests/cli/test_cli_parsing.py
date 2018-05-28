import platform
import sys
import unittest
from urh.dev.VirtualDevice import Mode
from urh.dev.BackendHandler import Backends

from urh.cli import urh_cli


class TestCLIParsing(unittest.TestCase):
    def setUp(self):
        self.parser = urh_cli.parser

    def test_build_modulator_from_args(self):
        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6 --raw".split())
        self.assertIsNone(urh_cli.build_modulator_from_args(args))

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6".split())
        with self.assertRaises(ValueError):
            urh_cli.build_modulator_from_args(args)

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6 -p0 0".split())
        with self.assertRaises(ValueError):
            urh_cli.build_modulator_from_args(args)

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6"
                                      " -p0 0 -p1 1 -mo ASK -cf 1337e3 -ca 0.9 -bl 24 -cp 30".split())
        modulator = urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.modulation_type_str, "ASK")
        self.assertEqual(modulator.sample_rate, 2e6)
        self.assertEqual(modulator.samples_per_bit, 24)
        self.assertEqual(modulator.param_for_zero, 0)
        self.assertEqual(modulator.param_for_one, 100)
        self.assertEqual(modulator.carrier_freq_hz, 1337e3)
        self.assertEqual(modulator.carrier_amplitude, 0.9)
        self.assertEqual(modulator.carrier_phase_deg, 30)


        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6"
                                      " -p0 10% -p1 20% -mo ASK -cf 1337e3 -ca 0.9 -bl 24 -cp 30".split())
        modulator = urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.param_for_zero, 10)
        self.assertEqual(modulator.param_for_one, 20)

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6"
                                      " -p0 20e3 -p1=-20e3 -mo FSK -cf 1337e3 -ca 0.9 -bl 24 -cp 30".split())
        modulator =  urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.modulation_type_str, "FSK")
        self.assertEqual(modulator.param_for_zero, 20e3)
        self.assertEqual(modulator.param_for_one, -20e3)

    def test_build_backend_handler_from_args(self):
        args = self.parser.parse_args("--device USRP --frequency 433.92e6 --sample-rate 2e6".split())
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["usrp"].selected_backend, Backends.native)

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6"
                                      " --device-backend native".split())
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["hackrf"].selected_backend, Backends.native)

        args = self.parser.parse_args("--device RTL-SDR --frequency 433.92e6 --sample-rate 2e6"
                                      " --device-backend gnuradio".split())
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["rtl-sdr"].selected_backend, Backends.grc)


    def test_build_device_from_args(self):
        if sys.platform == "win32" and platform.architecture()[0] == "32bit":
            # no device extensions on 32 bit windows
            return 

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6".split())
        with self.assertRaises(ValueError):
            urh_cli.build_device_from_args(args)

        args = self.parser.parse_args("--device HackRF --frequency 433.92e6 --sample-rate 2e6 -rx -tx".split())
        with self.assertRaises(ValueError):
            urh_cli.build_device_from_args(args)

        args = self.parser.parse_args("--device HackRF --frequency 133.7e6 --sample-rate 2.5e6 -rx "
                                      "-if 24 -bb 30 -g 0 --device-identifier abcde".split())
        device = urh_cli.build_device_from_args(args)
        self.assertEqual(device.sample_rate, 2.5e6)
        self.assertEqual(device.bandwidth, 2.5e6)
        self.assertEqual(device.name, "HackRF")
        self.assertEqual(device.backend, Backends.native)
        self.assertEqual(device.frequency, 133.7e6)
        self.assertEqual(device.mode, Mode.receive)
        self.assertEqual(device.if_gain, 24)
        self.assertEqual(device.gain, 0)
        self.assertEqual(device.baseband_gain, 30)
        self.assertEqual(device.device_serial, "abcde")

        args = self.parser.parse_args("--device RTL-SDR --frequency 133.7e6 --sample-rate 1e6 "
                                      "-rx -db native --device-identifier 42".split())
        device = urh_cli.build_device_from_args(args)
        self.assertEqual(device.sample_rate, 1e6)
        self.assertEqual(device.name, "RTL-SDR")
        self.assertEqual(device.backend, Backends.native)
        self.assertEqual(device.frequency, 133.7e6)
        self.assertEqual(device.mode, Mode.receive)
        self.assertEqual(device.device_number, 42)

        args = self.parser.parse_args("--device HackRF --frequency 133.7e6 --sample-rate 2.5e6 --bandwidth 5e6 "
                                      "-tx -db gnuradio".split())
        device = urh_cli.build_device_from_args(args)
        self.assertEqual(device.sample_rate, 2.5e6)
        self.assertEqual(device.bandwidth, 5e6)
        self.assertEqual(device.name, "HackRF")
        self.assertEqual(device.backend, Backends.grc)
        self.assertEqual(device.frequency, 133.7e6)
        self.assertEqual(device.mode, Mode.send)

    def test_build_protocol_sniffer_from_args(self):
        if sys.platform == "win32" and platform.architecture()[0] == "32bit":
            # no device extensions on 32 bit windows
            return

        args = self.parser.parse_args("--device HackRF --frequency 50e3 --sample-rate 2.5e6 -rx "
                                      "-if 24 -bb 30 -g 0 --device-identifier abcde "
                                      "-bl 1337 --center 0.5 --noise 0.1234 --tolerance 42".split())
        sniffer = urh_cli.build_protocol_sniffer_from_args(args)
        self.assertEqual(sniffer.rcv_device.frequency, 50e3)
        self.assertEqual(sniffer.rcv_device.sample_rate, 2.5e6)
        self.assertEqual(sniffer.rcv_device.bandwidth, 2.5e6)
        self.assertEqual(sniffer.rcv_device.name, "hackrf")
        self.assertEqual(sniffer.rcv_device.backend, Backends.native)
        self.assertEqual(sniffer.rcv_device.mode, Mode.receive)
        self.assertEqual(sniffer.rcv_device.if_gain, 24)
        self.assertEqual(sniffer.rcv_device.gain, 0)
        self.assertEqual(sniffer.rcv_device.baseband_gain, 30)
        self.assertEqual(sniffer.rcv_device.device_serial, "abcde")
        self.assertEqual(sniffer.signal.bit_len, 1337)
        self.assertEqual(sniffer.signal.noise_threshold, 0.1234)
        self.assertEqual(sniffer.signal.qad_center, 0.5)
        self.assertEqual(sniffer.signal.tolerance, 42)


    def test_build_encoding_from_args(self):
        args = self.parser.parse_args('--device HackRF --frequency 50e3 --sample-rate 2.5e6 -e "Test,Invert"'.split())
        encoding = urh_cli.build_encoding_from_args(args)
        self.assertEqual(len(encoding.chain), 2)