import os
import shutil
import tempfile

from tests.QtTestCase import QtTestCase
from urh.cli import urh_cli
from urh.dev.BackendHandler import Backends
from urh.dev.VirtualDevice import Mode


class TestCLIParsing(QtTestCase):
    def setUp(self):
        self.parser = urh_cli.create_parser()

    def test_build_modulator_from_args(self):
        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6 --raw".split()
        )
        self.assertIsNone(urh_cli.build_modulator_from_args(args))

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6".split()
        )
        with self.assertRaises(ValueError):
            urh_cli.build_modulator_from_args(args)

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6 -p0 0".split()
        )
        with self.assertRaises(ValueError):
            urh_cli.build_modulator_from_args(args)

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6"
            " -pm 0 1 -mo ASK -cf 1337e3 -ca 0.9 -sps 24 -cp 30".split()
        )
        modulator = urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.modulation_type, "ASK")
        self.assertEqual(modulator.sample_rate, 2e6)
        self.assertEqual(modulator.samples_per_symbol, 24)
        self.assertEqual(modulator.parameters[0], 0)
        self.assertEqual(modulator.parameters[1], 100)
        self.assertEqual(modulator.carrier_freq_hz, 1337e3)
        self.assertEqual(modulator.carrier_amplitude, 0.9)
        self.assertEqual(modulator.carrier_phase_deg, 30)

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6"
            " -pm 10% 20% -mo ASK -cf 1337e3 -ca 0.9 -sps 24 -cp 30".split()
        )
        modulator = urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.parameters[0], 10)
        self.assertEqual(modulator.parameters[1], 20)

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6"
            " -pm 20e3 -20000 -mo FSK -cf 1337e3 -ca 0.9 -sps 24 -cp 30".split()
        )
        modulator = urh_cli.build_modulator_from_args(args)
        self.assertEqual(modulator.modulation_type, "FSK")
        self.assertEqual(modulator.parameters[0], 20e3)
        self.assertEqual(modulator.parameters[1], -20e3)

    def test_build_backend_handler_from_args(self):
        args = self.parser.parse_args(
            "--device USRP --frequency 433.92e6 --sample-rate 2e6".split()
        )
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["usrp"].selected_backend, Backends.native)

        args = self.parser.parse_args(
            "--device HackRF --frequency 433.92e6 --sample-rate 2e6"
            " --device-backend native".split()
        )
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["hackrf"].selected_backend, Backends.native)

        args = self.parser.parse_args(
            "--device RTL-SDR --frequency 433.92e6 --sample-rate 2e6"
            " --device-backend gnuradio".split()
        )
        bh = urh_cli.build_backend_handler_from_args(args)
        self.assertEqual(bh.device_backends["rtl-sdr"].selected_backend, Backends.grc)

    def test_build_device_from_args(self):
        args = self.parser.parse_args(
            "--device HackRF --frequency 133.7e6 --sample-rate 2.5e6 -rx "
            "-if 24 -bb 30 -g 0 --device-identifier abcde".split()
        )
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

        args = self.parser.parse_args(
            "--device RTL-SDR --frequency 133.7e6 --sample-rate 1e6 "
            "-rx -db native --device-identifier 42".split()
        )
        device = urh_cli.build_device_from_args(args)
        self.assertEqual(device.sample_rate, 1e6)
        self.assertEqual(device.name, "RTL-SDR")
        self.assertEqual(device.backend, Backends.native)
        self.assertEqual(device.frequency, 133.7e6)
        self.assertEqual(device.mode, Mode.receive)
        self.assertEqual(device.device_number, 42)

        args = self.parser.parse_args(
            "--device HackRF --frequency 133.7e6 --sample-rate 2.5e6 --bandwidth 5e6 "
            "-tx -db native".split()
        )
        device = urh_cli.build_device_from_args(args)
        self.assertEqual(device.sample_rate, 2.5e6)
        self.assertEqual(device.bandwidth, 5e6)
        self.assertEqual(device.name, "HackRF")
        self.assertEqual(device.backend, Backends.native)
        self.assertEqual(device.frequency, 133.7e6)
        self.assertEqual(device.mode, Mode.send)

    def test_build_protocol_sniffer_from_args(self):
        args = self.parser.parse_args(
            "--device HackRF --frequency 50e3 --sample-rate 2.5e6 -rx "
            "-if 24 -bb 30 -g 0 --device-identifier abcde "
            "-sps 1337 --center 0.5 --noise 0.1234 --tolerance 42 "
            "-cs 0.42 -bps 4".split()
        )
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
        self.assertEqual(sniffer.signal.samples_per_symbol, 1337)
        self.assertEqual(sniffer.signal.bits_per_symbol, 4)
        self.assertEqual(sniffer.signal.center_spacing, 0.42)
        self.assertEqual(sniffer.signal.noise_threshold, 0.1234)
        self.assertEqual(sniffer.signal.center, 0.5)
        self.assertEqual(sniffer.signal.tolerance, 42)

    def test_build_encoding_from_args(self):
        args = self.parser.parse_args(
            '--device HackRF --frequency 50e3 --sample-rate 2.5e6 -e "Test,Invert"'.split()
        )
        encoding = urh_cli.build_encoding_from_args(args)
        self.assertEqual(len(encoding.chain), 2)

    def test_read_messages_to_send(self):
        args = self.parser.parse_args(
            "--device HackRF --frequency 50e3 --sample-rate 2e6 -rx".split()
        )
        self.assertIsNone(urh_cli.read_messages_to_send(args))

        args = self.parser.parse_args(
            "--device HackRF --frequency 50e3 --sample-rate 2e6 -tx".split()
        )
        with self.assertRaises(SystemExit):
            urh_cli.read_messages_to_send(args)

        args = self.parser.parse_args(
            "--device HackRF --frequency 50e3 --sample-rate 2e6 -tx "
            "-file /tmp/test -m 1111".split()
        )
        with self.assertRaises(SystemExit):
            urh_cli.read_messages_to_send(args)

        test_messages = [
            "101010/1s",
            "10000/50ms",
            "00001111/100.5µs",
            "111010101/500ns",
            "1111001",
            "111110000/2000",
        ]
        args = self.parser.parse_args(
            (
                "--device HackRF --frequency 50e3 --sample-rate 2e6 -tx --pause 1337 "
                "-m " + " ".join(test_messages)
            ).split()
        )
        messages = urh_cli.read_messages_to_send(args)
        self.assertEqual(len(messages), len(test_messages))
        self.assertEqual(messages[0].decoded_bits_str, "101010")
        self.assertEqual(messages[0].pause, 2e6)

        self.assertEqual(messages[1].decoded_bits_str, "10000")
        self.assertEqual(messages[1].pause, 100e3)

        self.assertEqual(messages[2].decoded_bits_str, "00001111")
        self.assertEqual(messages[2].pause, 201)

        self.assertEqual(messages[3].decoded_bits_str, "111010101")
        self.assertEqual(messages[3].pause, 1)

        self.assertEqual(messages[4].decoded_bits_str, "1111001")
        self.assertEqual(messages[4].pause, 1337)

        self.assertEqual(messages[5].decoded_bits_str, "111110000")
        self.assertEqual(messages[5].pause, 2000)

        test_messages = ["aabb/2s"]
        filepath = tempfile.mktemp()
        with open(filepath, "w") as f:
            f.write("\n".join(test_messages))

        args = self.parser.parse_args(
            (
                "--device HackRF --frequency 50e3 --sample-rate 2e6 -tx --pause 1337 --hex "
                "-file " + filepath
            ).split()
        )
        messages = urh_cli.read_messages_to_send(args)
        self.assertEqual(len(messages), len(test_messages))
        self.assertEqual(messages[0].decoded_bits_str, "1010101010111011")
        self.assertEqual(messages[0].pause, 4e6)

    def test_parse_project_file(self):
        f = os.readlink(__file__) if os.path.islink(__file__) else __file__
        path = os.path.realpath(os.path.join(f, ".."))

        project_file = os.path.realpath(
            os.path.join(path, "..", "data", "TestProjectForCLI.xml")
        )
        tmp_project_file = os.path.join(tempfile.mkdtemp(), "URHProject.xml")
        shutil.copy(project_file, tmp_project_file)

        project_params = urh_cli.parse_project_file(tmp_project_file)
        self.assertGreater(len(project_params), 0)
