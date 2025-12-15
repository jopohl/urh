#!/usr/bin/env python3
import argparse
import logging
import os
import sys
import time
from collections import defaultdict

import numpy as np

DEFAULT_CARRIER_FREQUENCY = 1e3
DEFAULT_CARRIER_AMPLITUDE = 1
DEFAULT_CARRIER_PHASE = 0

DEFAULT_SAMPLES_PER_SYMBOL = 100
DEFAULT_NOISE = 0.1
DEFAULT_CENTER = 0
DEFAULT_CENTER_SPACING = 0.1
DEFAULT_TOLERANCE = 5

cli_exe = sys.executable if hasattr(sys, "frozen") else sys.argv[0]
cur_dir = os.path.realpath(os.path.dirname(os.path.realpath(cli_exe)))
SRC_DIR = os.path.realpath(os.path.join(cur_dir, "..", ".."))

if os.path.isdir(SRC_DIR):
    sys.path.insert(0, SRC_DIR)

from urh.signalprocessing.IQArray import IQArray
from urh.util import util

util.set_shared_library_path()

try:
    import urh.cythonext.signal_functions
    import urh.cythonext.path_creator
    import urh.cythonext.util
except ImportError:
    if hasattr(sys, "frozen"):
        print("C++ Extensions not found. Exiting...")
        sys.exit(1)
    print("Could not find C++ extensions, trying to build them.")
    old_dir = os.path.realpath(os.curdir)
    os.chdir(os.path.join(SRC_DIR, "urh", "cythonext"))

    from urh.cythonext import build

    build.main()

    os.chdir(old_dir)

from urh.dev.BackendHandler import BackendHandler
from urh.signalprocessing.Modulator import Modulator
from urh.dev.VirtualDevice import VirtualDevice
from urh.signalprocessing.ProtocolSniffer import ProtocolSniffer
from urh.util import Logger
from urh.settings import PAUSE_SEP
from urh.util.Logger import logger
from urh.signalprocessing.Encoding import Encoding
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer

DEVICES = BackendHandler.DEVICE_NAMES
MODULATIONS = Modulator.MODULATION_TYPES


def cli_progress_bar(value, end_value, bar_length=20, title="Percent"):
    percent = value / end_value
    hashes = "#" * int(round(percent * bar_length))
    spaces = " " * (bar_length - len(hashes))
    sys.stdout.write(
        "\r{0}:\t[{1}] {2}%".format(title, hashes + spaces, int(round(percent * 100)))
    )
    sys.stdout.flush()


def on_fatal_device_error_occurred(error: str):
    logger.critical(error.strip())
    sys.exit(1)


def build_modulator_from_args(arguments: argparse.Namespace):
    if arguments.raw:
        return None
    if arguments.bits_per_symbol is None:
        arguments.bits_per_symbol = 1

    n = 2 ** int(arguments.bits_per_symbol)
    if arguments.parameters is None or len(arguments.parameters) != n:
        raise ValueError(
            "You need to give {} parameters for {} bits per symbol".format(
                n, int(arguments.bits_per_symbol)
            )
        )

    result = Modulator("CLI Modulator")
    result.carrier_freq_hz = float(arguments.carrier_frequency)
    result.carrier_amplitude = float(arguments.carrier_amplitude)
    result.carrier_phase_deg = float(arguments.carrier_phase)
    result.samples_per_symbol = int(arguments.samples_per_symbol)
    result.bits_per_symbol = int(arguments.bits_per_symbol)
    result.modulation_type = arguments.modulation_type
    result.sample_rate = arguments.sample_rate

    for i, param in enumerate(arguments.parameters):
        if result.is_amplitude_based and param.endswith("%"):
            result.parameters[i] = float(param[:-1])
        elif result.is_amplitude_based and not param.endswith("%"):
            result.parameters[i] = float(param) * 100
        else:
            result.parameters[i] = float(param)

    return result


def build_backend_handler_from_args(arguments: argparse.Namespace):
    from urh.dev.BackendHandler import Backends

    bh = BackendHandler()
    if arguments.device_backend == "native":
        bh.device_backends[arguments.device.lower()].selected_backend = Backends.native
    elif arguments.device_backend == "gnuradio":
        bh.device_backends[arguments.device.lower()].selected_backend = Backends.grc
    else:
        raise ValueError("Unsupported device backend")
    return bh


def build_device_from_args(arguments: argparse.Namespace):
    from urh.dev.VirtualDevice import Mode

    bh = build_backend_handler_from_args(arguments)

    bandwidth = (
        arguments.sample_rate if arguments.bandwidth is None else arguments.bandwidth
    )
    result = VirtualDevice(
        bh,
        name=arguments.device,
        mode=Mode.receive if arguments.receive else Mode.send,
        freq=arguments.frequency,
        sample_rate=arguments.sample_rate,
        bandwidth=bandwidth,
        gain=arguments.gain,
        if_gain=arguments.if_gain,
        baseband_gain=arguments.baseband_gain,
    )

    result.freq_correction = arguments.frequency_correction
    if arguments.device_identifier is not None:
        try:
            result.device_number = int(arguments.device_identifier)
        except ValueError:
            result.device_serial = arguments.device_identifier

    result.fatal_error_occurred.connect(on_fatal_device_error_occurred)

    return result


def build_protocol_sniffer_from_args(arguments: argparse.Namespace):
    bh = build_backend_handler_from_args(arguments)

    result = ProtocolSniffer(
        arguments.samples_per_symbol,
        arguments.center,
        arguments.center_spacing,
        arguments.noise,
        arguments.tolerance,
        arguments.modulation_type,
        arguments.bits_per_symbol,
        arguments.device.lower(),
        bh,
    )
    result.rcv_device.frequency = arguments.frequency
    result.rcv_device.sample_rate = arguments.sample_rate
    result.rcv_device.bandwidth = (
        arguments.sample_rate if arguments.bandwidth is None else arguments.bandwidth
    )
    result.rcv_device.freq_correction = arguments.frequency_correction
    if arguments.gain is not None:
        result.rcv_device.gain = arguments.gain
    if arguments.if_gain is not None:
        result.rcv_device.if_gain = arguments.if_gain
    if arguments.baseband_gain is not None:
        result.rcv_device.baseband_gain = arguments.baseband_gain

    if arguments.device_identifier is not None:
        try:
            result.rcv_device.device_number = int(arguments.device_identifier)
        except ValueError:
            result.rcv_device.device_serial = arguments.device_identifier

    if arguments.encoding:
        result.decoder = build_encoding_from_args(arguments)

    result.rcv_device.fatal_error_occurred.connect(on_fatal_device_error_occurred)
    result.adaptive_noise = arguments.adaptive_noise
    return result


def build_encoding_from_args(arguments: argparse.Namespace):
    if arguments.encoding is None:
        return None

    primitives = arguments.encoding.split(",")
    return Encoding(list(filter(None, map(str.strip, primitives))))


def read_messages_to_send(arguments: argparse.Namespace):
    if not arguments.transmit:
        return None

    if arguments.messages is not None and arguments.filename is not None:
        print("Either give messages (-m) or a file to read from (-file) not both.")
        sys.exit(1)
    elif arguments.messages is not None:
        # support for calls from external tools e.g. metasploit
        if len(arguments.messages) == 1:
            message_strings = arguments.messages[0].split(" ")
        else:
            message_strings = arguments.messages
    elif arguments.filename is not None:
        with open(arguments.filename) as f:
            message_strings = list(map(str.strip, f.readlines()))
    else:
        print(
            "You need to give messages to send either with (-m) or a file (-file) to read them from."
        )
        sys.exit(1)

    encoding = build_encoding_from_args(arguments)

    result = ProtocolAnalyzer.get_protocol_from_string(
        message_strings,
        is_hex=arguments.hex,
        default_pause=arguments.pause,
        sample_rate=arguments.sample_rate,
    ).messages
    if encoding:
        for msg in result:
            msg.decoder = encoding

    return result


def modulate_messages(messages, modulator):
    if len(messages) == 0:
        return None

    cli_progress_bar(0, len(messages), title="Modulating")
    nsamples = sum(
        int(len(msg.encoded_bits) * modulator.samples_per_symbol + msg.pause)
        for msg in messages
    )
    buffer = IQArray(None, dtype=np.float32, n=nsamples)
    pos = 0
    for i, msg in enumerate(messages):
        # We do not need to modulate the pause extra, as result is already initialized with zeros
        modulated = modulator.modulate(start=0, data=msg.encoded_bits, pause=0)
        buffer[pos : pos + len(modulated)] = modulated
        pos += len(modulated) + msg.pause
        cli_progress_bar(i + 1, len(messages), title="Modulating")
    print("\nSuccessfully modulated {} messages".format(len(messages)))
    return buffer


def parse_project_file(file_path: str):
    import xml.etree.ElementTree as ET
    from urh.util.ProjectManager import ProjectManager

    result = defaultdict(lambda: None)
    if not file_path or not os.path.isfile(file_path):
        return result

    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
    except Exception as e:
        logger.error("Could not read project file {}: {}".format(file_path, e))
        return result

    ProjectManager.read_device_conf_dict(root.find("device_conf"), target_dict=result)
    result["device"] = result["name"]

    modulators = Modulator.modulators_from_xml_tag(root)
    if len(modulators) > 0:
        modulator = modulators[0]
        result["carrier_frequency"] = modulator.carrier_freq_hz
        result["carrier_amplitude"] = modulator.carrier_amplitude
        result["carrier_phase"] = modulator.carrier_phase_deg
        result["parameters"] = " ".join(map(str, modulator.parameters))
        result["modulation_type"] = modulator.modulation_type

    return result


def create_parser():
    parser = argparse.ArgumentParser(
        description="This is the Command Line Interface for the Universal Radio Hacker.",
        add_help=False,
    )
    parser.add_argument("project_file", nargs="?", default=None)

    group1 = parser.add_argument_group(
        "Software Defined Radio Settings", "Configure Software Defined Radio options"
    )
    group1.add_argument(
        "-d",
        "--device",
        choices=DEVICES,
        metavar="DEVICE",
        help="Choose a Software Defined Radio. Allowed values are "
        + ", ".join(DEVICES),
    )
    group1.add_argument("-di", "--device-identifier")
    group1.add_argument(
        "-db", "--device-backend", choices=["native", "gnuradio"], default="native"
    )
    group1.add_argument(
        "-f",
        "--frequency",
        type=float,
        help="Center frequency the SDR shall be tuned to",
    )
    group1.add_argument("-s", "--sample-rate", type=float, help="Sample rate to use")
    group1.add_argument(
        "-b",
        "--bandwidth",
        type=float,
        help="Bandwidth to use (defaults to sample rate)",
    )
    group1.add_argument("-g", "--gain", type=int, help="RF gain the SDR shall use")
    group1.add_argument(
        "-if",
        "--if-gain",
        type=int,
        help="IF gain to use (only supported for some SDRs)",
    )
    group1.add_argument(
        "-bb",
        "--baseband-gain",
        type=int,
        help="Baseband gain to use (only supported for some SDRs)",
    )
    group1.add_argument(
        "-a",
        "--adaptive-noise",
        action="store_true",
        help="Use adaptive noise when receiving.",
    )
    group1.add_argument(
        "-fcorr",
        "--frequency-correction",
        default=1,
        type=int,
        help="Set the frequency correction for SDR (if supported)",
    )

    group2 = parser.add_argument_group(
        "Modulation/Demodulation settings",
        "Configure the Modulator/Demodulator. Not required in raw mode."
        "In case of RX there are additional demodulation options.",
    )
    group2.add_argument(
        "-cf",
        "--carrier-frequency",
        type=float,
        help="Carrier frequency in Hertz (default: {})".format(
            DEFAULT_CARRIER_FREQUENCY
        ),
    )
    group2.add_argument(
        "-ca",
        "--carrier-amplitude",
        type=float,
        help="Carrier amplitude (default: {})".format(DEFAULT_CARRIER_AMPLITUDE),
    )
    group2.add_argument(
        "-cp",
        "--carrier-phase",
        type=float,
        help="Carrier phase in degree (default: {})".format(DEFAULT_CARRIER_PHASE),
    )
    group2.add_argument(
        "-mo",
        "--modulation-type",
        choices=MODULATIONS,
        metavar="MOD_TYPE",
        default="FSK",
        help="Modulation type must be one of "
        + ", ".join(MODULATIONS)
        + " (default: %(default)s)",
    )
    group2.add_argument(
        "-bps",
        "--bits-per-symbol",
        type=int,
        help="Bits per symbol e.g. 1 means binary modulation (default: 1).",
    )
    group2.add_argument(
        "-pm",
        "--parameters",
        nargs="+",
        help="Parameters for modulation. Separate with spaces",
    )

    # Legacy
    group2.add_argument("-p0", "--parameter-zero", help=argparse.SUPPRESS)
    group2.add_argument("-p1", "--parameter-one", help=argparse.SUPPRESS)

    group2.add_argument(
        "-sps",
        "--samples-per-symbol",
        type=int,
        help="Length of a symbol in samples (default: {}).".format(
            DEFAULT_SAMPLES_PER_SYMBOL
        ),
    )
    group2.add_argument(
        "-bl",
        "--bit-length",
        type=int,
        help="Same as samples per symbol, just there for legacy support (default: {}).".format(
            DEFAULT_SAMPLES_PER_SYMBOL
        ),
    )

    group2.add_argument(
        "-n",
        "--noise",
        type=float,
        help="Noise threshold (default: {}). Used for RX only.".format(DEFAULT_NOISE),
    )
    group2.add_argument(
        "-c",
        "--center",
        type=float,
        help="Center between symbols for demodulation (default: {}). "
        "Used for RX only.".format(DEFAULT_CENTER),
    )
    group2.add_argument(
        "-cs",
        "--center-spacing",
        type=float,
        help="Center spacing between symbols for demodulation (default: {}). "
        "Value has only effect for modulations with more than 1 bit per symbol. "
        "Used only for RX.".format(DEFAULT_CENTER_SPACING),
    )
    group2.add_argument(
        "-t",
        "--tolerance",
        type=float,
        help="Tolerance for demodulation in samples (default: {}). "
        "Used for RX only.".format(DEFAULT_TOLERANCE),
    )

    group3 = parser.add_argument_group(
        "Data configuration", "Configure which data to send or where to receive it."
    )
    group3.add_argument(
        "--hex", action="store_true", help="Give messages as hex instead of bits"
    )
    group3.add_argument("-e", "--encoding", help="Specify encoding")
    group3.add_argument(
        "-m",
        "--messages",
        nargs="+",
        help="Messages to send. Give pauses after with a {0}. "
        "Separate with spaces e.g. "
        "1001{0}42ms 1100{0}3ns 0001 1111{0}200. "
        "If you give no time suffix after a pause "
        "it is assumed to be in samples. ".format(PAUSE_SEP),
    )

    group3.add_argument(
        "-file",
        "--filename",
        help="Filename to read messages from in send mode. "
        "In receive mode messages will be written to this file "
        "instead to STDOUT.",
    )
    group3.add_argument(
        "-p",
        "--pause",
        default="250ms",
        help="The default pause which is inserted after a every message "
        "which does not have a pause configured. (default: %(default)s) "
        "Supported time units: s (second), ms (millisecond), µs (microsecond), ns (nanosecond) "
        "If you do not give a time suffix the pause is assumed to be in samples.",
    )
    group3.add_argument("-rx", "--receive", action="store_true", help="Enter RX mode")
    group3.add_argument("-tx", "--transmit", action="store_true", help="Enter TX mode")
    group3.add_argument(
        "-rt",
        "--receive-time",
        default="3.0",
        type=float,
        help="How long to receive messages. (default: %(default)s) "
        "Any negative value means infinite.",
    )
    group3.add_argument(
        "-r",
        "--raw",
        action="store_true",
        help="Use raw mode i.e. send/receive IQ data instead of bits.",
    )

    group4 = parser.add_argument_group("Miscellaneous options")
    group4.add_argument(
        "-h", "--help", action="help", help="show this help message and exit"
    )
    group4.add_argument("-v", "--verbose", action="count")

    return parser


def main():
    def get_val(value, project_params: dict, project_param_key: str, default):
        if value is not None:
            return value
        elif project_param_key in project_params:
            return project_params[project_param_key]
        else:
            return default

    import multiprocessing as mp

    mp.set_start_method("spawn")  # allow usage of prange (OpenMP) in Processes
    mp.freeze_support()

    parser = create_parser()
    args = parser.parse_args()
    if args.parameter_zero is not None or args.parameter_one is not None:
        print(
            "Options -p0 (--parameter-zero) and -p1 (--parameter-one) are not supported anymore.\n"
            "Use --parameters instead e.g. --parameters 20K 40K for a binary FSK."
        )
        sys.exit(1)

    project_params = parse_project_file(args.project_file)
    for argument in ("device", "frequency", "sample_rate"):
        if getattr(args, argument):
            continue

        if project_params[argument] is not None:
            setattr(args, argument, project_params[argument])
        else:
            print("You must specify a {}.".format(argument))
            sys.exit(1)

    if args.receive and args.transmit:
        print("You cannot use receive and transmit mode at the same time.")
        sys.exit(1)
    if not args.receive and not args.transmit:
        print(
            "You must choose a mode either RX (-rx, --receive) or TX (-tx, --transmit)"
        )
        sys.exit(1)

    args.bandwidth = get_val(args.bandwidth, project_params, "bandwidth", None)
    rx_tx_prefix = "rx_" if args.receive else "tx_"
    args.gain = get_val(args.gain, project_params, rx_tx_prefix + "gain", None)
    args.if_gain = get_val(args.if_gain, project_params, rx_tx_prefix + "if_gain", None)
    args.baseband_gain = get_val(
        args.baseband_gain, project_params, rx_tx_prefix + "baseband_gain", None
    )

    if args.modulation_type is None:
        try:
            if project_params["modulation_type"] is None:
                args.modulation_type = MODULATIONS[
                    int(project_params["modulation_index"])
                ]
            else:
                args.modulation_type = project_params["modulation_type"]
        except:
            pass

    if args.bit_length is not None and args.samples_per_symbol is None:
        args.samples_per_symbol = args.bit_length  # legacy
    else:
        args.samples_per_symbol = get_val(
            args.samples_per_symbol,
            project_params,
            "samples_per_symbol",
            DEFAULT_SAMPLES_PER_SYMBOL,
        )

    args.center = get_val(args.center, project_params, "center", DEFAULT_CENTER)
    args.center_spacing = get_val(
        args.center_spacing, project_params, "center_spacing", DEFAULT_CENTER_SPACING
    )
    args.noise = get_val(args.noise, project_params, "noise", DEFAULT_NOISE)
    args.tolerance = get_val(
        args.tolerance, project_params, "tolerance", DEFAULT_TOLERANCE
    )
    args.bits_per_symbol = get_val(
        args.bits_per_symbol, project_params, "bits_per_symbol", 1
    )

    args.carrier_frequency = get_val(
        args.carrier_frequency,
        project_params,
        "carrier_frequency",
        DEFAULT_CARRIER_FREQUENCY,
    )
    args.carrier_amplitude = get_val(
        args.carrier_amplitude,
        project_params,
        "carrier_amplitude",
        DEFAULT_CARRIER_AMPLITUDE,
    )
    args.carrier_phase = get_val(
        args.carrier_phase, project_params, "carrier_phase", DEFAULT_CARRIER_PHASE
    )
    args.parameters = get_val(args.parameters, project_params, "parameters", None)
    if args.parameters is None:
        print("You must give modulation parameters (--parameters)")
        sys.exit(0)

    if args.verbose is None:
        logger.setLevel(logging.ERROR)
    elif args.verbose == 1:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.DEBUG)
    Logger.save_log_level()

    argument_string = "\n".join(
        "{} {}".format(arg, getattr(args, arg)) for arg in vars(args)
    )
    logger.debug("Using these parameters\n" + argument_string)

    if args.transmit:
        device = build_device_from_args(args)
        if args.raw:
            if args.filename is None:
                print(
                    "You need to give a file (-file, --filename) where to read samples from."
                )
                sys.exit(1)
            samples_to_send = np.fromfile(args.filename, dtype=np.complex64)
        else:
            modulator = build_modulator_from_args(args)
            messages_to_send = read_messages_to_send(args)
            samples_to_send = modulate_messages(messages_to_send, modulator)
        device.samples_to_send = samples_to_send
        device.start()

        while not device.sending_finished:
            try:
                time.sleep(0.1)
                device.read_messages()
                if device.current_index > 0:
                    cli_progress_bar(
                        device.current_index,
                        len(device.samples_to_send),
                        title="Sending",
                    )
            except KeyboardInterrupt:
                break

        print()
        device.stop("Sending finished")
    elif args.receive:
        if args.raw:
            if args.filename is None:
                print(
                    "You need to give a file (-file, --filename) to receive into when using raw RX mode."
                )
                sys.exit(1)

            receiver = build_device_from_args(args)
            receiver.start()
        else:
            receiver = build_protocol_sniffer_from_args(args)
            receiver.sniff()

        total_time = 0

        if args.receive_time >= 0:
            print("Receiving for {} seconds...".format(args.receive_time))
        else:
            print("Receiving forever...")

        f = None if args.filename is None else open(args.filename, "w")
        kwargs = dict() if f is None else {"file": f}

        dev = receiver.rcv_device if hasattr(receiver, "rcv_device") else receiver

        while total_time < abs(args.receive_time):
            try:
                dev.read_messages()
                time.sleep(0.1)
                if args.receive_time >= 0:
                    # smaller zero means infinity
                    total_time += 0.1

                if not args.raw:
                    num_messages = len(receiver.messages)
                    for msg in receiver.messages[:num_messages]:
                        print(
                            msg.decoded_hex_str if args.hex else msg.decoded_bits_str,
                            **kwargs
                        )
                    del receiver.messages[:num_messages]
            except KeyboardInterrupt:
                break

        print("\nStopping receiving...")
        if args.raw:
            receiver.stop("Receiving finished")
            receiver.data[: receiver.current_index].tofile(f)
        else:
            receiver.stop()

        if f is not None:
            f.close()
            print("Received data written to {}".format(args.filename))


if __name__ == "__main__":
    main()
