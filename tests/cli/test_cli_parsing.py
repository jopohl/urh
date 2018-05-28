import argparse
import unittest

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
