import os
import sys
import time

# from subprocess import PIPE, Popen
# from threading import Thread

import numpy as np
from PyQt5.QtCore import pyqtSignal

from urh import settings
from urh.plugins.Plugin import SDRPlugin
from urh.signalprocessing.Message import Message
from urh.util.Errors import Errors
from urh.util.Logger import logger


class FlipperZeroSubPlugin(SDRPlugin):
    def __init__(self):
        super().__init__(name="FlipperZeroSub")
        self.filetype = "Flipper SubGhz RAW File"
        self.version = 1
        self.protocol = "RAW"
        self.max_values_per_line = 512

    def getFuriHalString(self, modulation_type, given_bandwidth_deviation=0):
        if modulation_type == "ASK":
            if given_bandwidth_deviation > 500:
                # OOK, bandwidth 650kHz, asynchronous
                FuriHalString = "FuriHalSubGhzPresetOok650Async"
                bandwidth_deviation = 650
            else:
                # OOK, bandwidth 270kHz, asynchronous
                FuriHalString = "FuriHalSubGhzPresetOok270Async"
                bandwidth_deviation = 270
        elif modulation_type == "FSK":
            if given_bandwidth_deviation > 20:
                # FM, deviation 47.60742 kHz, asynchronous
                FuriHalString = "FuriHalSubGhzPreset2FSKDev476Async"
                bandwidth_deviation = 47.6
            else:
                # FM, deviation 2.380371 kHz, asynchronous
                FuriHalString = "FuriHalSubGhzPreset2FSKDev238Async"
                bandwidth_deviation = 2.38
        elif modulation_type == "GFSK":
            # GFSK, deviation 19.042969 kHz, 9.996Kb/s, asynchronous
            FuriHalString = "FuriHalSubGhzPresetGFSK9_99KbAsync"
            bandwidth_deviation = 19.04
        elif modulation_type == "PSK":
            FuriHalString = "FuriHalSubGhzPresetCustom"
            bandwidth_deviation = 238
        else:  # Fallback is Flipper Zero SubGHz default
            # OOK, bandwidth 650kHz, asynchronous
            FuriHalString = "FuriHalSubGhzPresetOok650Async"
            bandwidth_deviation = 650
        return FuriHalString, bandwidth_deviation

    def write_sub_file(
        self, filename, messages, sample_rates, modulators, project_manager
    ):
        # Check whether the message != NULL
        if len(messages) == 0:
            logger.debug("Empty signal!")
            return False

        # Open file "filename" for write
        try:
            file = open(filename, "w")
        except OSError as e:
            logger.debug(f"Could not open {filename} for writing: {e}", file=sys.stderr)
            return False

        # Get Flipper Zero FuriHal Preset and its datarate
        frequency = int(project_manager.device_conf["frequency"])
        # samplerate = sample_rates[0]
        samples_per_symbol = messages[0].samples_per_symbol
        preset, bandwidth_deviation = self.getFuriHalString(
            modulators[messages[0].modulator_index].modulation_type, 1000
        )  # TODO: last parameter is bandwidth/deviation of preset profile. Hardcoded to 1000 until it becomes clear how to find the value from signal data properly

        # Write Flipper Zero SubGHz protocol header
        file.write(f"Filetype: {self.filetype}\n")
        file.write(f"Version: {self.version}\n")
        file.write(f"Frequency: {frequency}\n")
        file.write(f"Preset: {preset}\n")
        file.write(f"Protocol: {self.protocol}")

        # Create signal
        signal = []
        for msg in messages:
            current_value = msg[0]
            current_count = 0
            for bit in msg:
                if bit == current_value:
                    current_count += 1
                else:
                    # Append to signal when bit changes
                    signal.append(
                        current_count if current_value == 1 else -current_count
                    )
                    current_count = 1
                    current_value = bit
            # Last pulse
            signal.append(current_count if current_value == 1 else -current_count)

        # Write signal
        sps = messages[0].samples_per_symbol
        for i in range(len(signal)):
            if 0 == i % self.max_values_per_line:
                file.write("\nRAW_Data:")
            file.write(f" {signal[i] * samples_per_symbol}")

        # Close file
        file.close()
