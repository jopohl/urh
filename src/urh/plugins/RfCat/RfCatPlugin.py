import os
from subprocess import PIPE, Popen
from threading import Thread
import time
import numpy as np
from PyQt5.QtCore import pyqtSignal
from urh.plugins.Plugin import SDRPlugin
from urh.signalprocessing.Message import Message
from urh.util.Errors import Errors
from urh.util.Logger import logger
from urh import constants

## rfcat commands
# freq = 433920000
# mod = "MOD_ASK_OOK"
# pktlen = 10
# syncmode = 0
# syncbytes = "\xCA\xFE\xAF\xFE"
# baud = 4800
# sendbytes = "\xCA\xFE\xAF\xFE"
# num_preamble = 0
#
# cmd_ping = "d.ping()"
# cmd_freq = "d.setFreq({})".format(freq)
# cmd_mod = "d.setMdmModulation({})".format(mod)
# cmd_pktlen = "d.makePktFLEN({})".format(pktlen)
# cmd_syncmode = "d.setMdmSyncMode({})".format(syncmode)
# cmd_syncbytes = "d.setMdmSyncWord({})".format(syncbytes)
# cmd_baud = "d.setMdmDRate({})".format(baud)
# cmd_sendbytes = "d.RFxmit('{}')".format(sendbytes)
# cmd_maxpower = "d.setMaxPower()"
# cmd_recvbytes = "d.RFrecv()[0]"
# cmd_preamble = "d.setMdmNumPreamble({})".format(num_preamble)
# cmd_showconfig = "print d.reprRadioConfig()"

class RfCatPlugin(SDRPlugin):
    rcv_index_changed = pyqtSignal(int, int) # int arguments are just for compatibility with native and grc backend
    show_proto_sniff_dialog_clicked = pyqtSignal()
    sending_status_changed = pyqtSignal(bool)
    sending_stop_requested = pyqtSignal()
    current_send_message_changed = pyqtSignal(int)

    def __init__(self):
        super().__init__(name="RfCat")
        self.rfcat_executable = self.qsettings.value("rfcat_executable", defaultValue="rfcat", type=str)
        self.rfcat_is_open = False
        self.initialized = False
        self.ready = True
        self.__is_sending = False
        self.__sending_interrupt_requested = False
        self.current_sent_sample = 0
        self.current_sending_repeat = 0
        self.modulators = 0

    def __del__(self):
        self.close_rfcat()

    @property
    def is_sending(self) -> bool:
        return self.__is_sending

    @is_sending.setter
    def is_sending(self, value: bool):
        if value != self.__is_sending:
            self.__is_sending = value
            self.sending_status_changed.emit(self.__is_sending)

    @property
    def rfcat_is_found(self):
        return self.is_rfcat_executable(self.rfcat_executable)

    def is_rfcat_executable(self, rfcat_executable):
        fpath, fname = os.path.split(rfcat_executable)
        if fpath:
            if os.path.isfile(rfcat_executable) and os.access(rfcat_executable, os.X_OK):
                return True
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, rfcat_executable)
                if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                    return True
        return False

    def enable_or_disable_send_button(self, rfcat_executable):
        if self.is_rfcat_executable(rfcat_executable):
            self.settings_frame.info.setText("Info: Executable can be opened.")
        else:
            self.settings_frame.info.setText("Info: Executable cannot be opened! Disabling send button.")
            logger.debug("RfCat executable cannot be opened! Disabling send button.")

    def create_connects(self):
        self.settings_frame.rfcat_executable.setText(self.rfcat_executable)
        self.settings_frame.rfcat_executable.editingFinished.connect(self.on_edit_rfcat_executable_editing_finished)
        self.enable_or_disable_send_button(self.rfcat_executable)

    def on_edit_rfcat_executable_editing_finished(self):
        rfcat_executable = self.settings_frame.rfcat_executable.text()
        self.enable_or_disable_send_button(rfcat_executable)
        self.rfcat_executable = rfcat_executable
        self.qsettings.setValue('rfcat_executable', self.rfcat_executable)

    def free_data(self):
        if self.raw_mode:
            self.receive_buffer = np.empty(0)
        else:
            self.received_bits[:] = []

    def write_to_rfcat(self, buf):
        self.process.stdin.write(buf.encode("utf-8") + b"\n")
        self.process.stdin.flush()

    def open_rfcat(self):
        if not self.rfcat_is_open:
            try:
                self.process = Popen([self.rfcat_executable, '-r'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                self.rfcat_is_open = True
                logger.debug("Successfully opened RfCat ({})".format(self.rfcat_executable))
                return True
            except Exception as e:
                logger.debug("Could not open RfCat! ({})".format(e))
                return False
        else:
            return True

    def close_rfcat(self):
        if self.rfcat_is_open:
            try:
                self.process.kill()
                self.rfcat_is_open = False
            except Exception as e:
                logger.debug("Could not close rfcat: {}".format(e))

    def set_parameter(self, param: str, log=True):  # returns error (True/False)
        try:
            self.write_to_rfcat(param)
            self.ready = False
            if log:
                  logger.debug(param)
        except OSError as e:
            logger.info("Could not set parameter {0}:{1} ({2})".format(param, e))
            return True
        return False

    def read_async(self):
        self.set_parameter("d.RFrecv({})[0]".format(500), log=False)

    def configure_rfcat(self, modulation = "MOD_ASK_OOK", freq = 433920000, sample_rate = 2000000, bit_len = 500):
        self.set_parameter("d.setMdmModulation({})".format(modulation), log=False)
        self.set_parameter("d.setFreq({})".format(int(freq)), log=False)
        self.set_parameter("d.setMdmSyncMode(0)", log=False)
        self.set_parameter("d.setMdmDRate({})".format(int(sample_rate // bit_len)), log=False)
        self.set_parameter("d.setMaxPower()", log=False)
        logger.info("Configured RfCat to Modulation={}, Freqency={} Hz, Datarate={} baud".format(modulation, int(freq), int(sample_rate // bit_len)))

    def send_data(self, data) -> str:
        prepared_data = "d.RFxmit({})".format(str(data)[11:-1]) #[11:-1] Removes "bytearray(b...)
        self.set_parameter(prepared_data, log=False)

    def __send_messages(self, messages, sample_rates):
        if len(messages):
            self.is_sending = True
        else:
            return False

        # Open and configure RfCat
        if not self.open_rfcat():
            return False
        modulation = self.modulators[messages[0].modulator_index].modulation_type
        if modulation == 0:     # ASK
            modulation = "MOD_ASK_OOK"
        elif modulation == 1:   # FSK
            modulation = "MOD_2FSK"
        elif modulation == 2:   # GFSK
            modulation = "MOD_GFSK"
        elif modulation == 3:   # PSK
            modulation = "MOD_MSK"
        else:                   # Fallback
            modulation = "MOD_ASK_OOK"
        self.configure_rfcat(modulation=modulation, freq=self.project_manager.device_conf["frequency"],
                             sample_rate=sample_rates[0], bit_len=messages[0].bit_len)

        repeats_from_settings = constants.SETTINGS.value('num_sending_repeats', type=int)
        repeats = repeats_from_settings if repeats_from_settings > 0 else -1
        while (repeats > 0 or repeats == -1) and self.__sending_interrupt_requested == False:
            logger.debug("Start iteration ({} left)".format(repeats if repeats > 0 else "infinite"))
            for i, msg in enumerate(messages):
                if self.__sending_interrupt_requested:
                    break
                assert isinstance(msg, Message)
                wait_time = msg.pause / sample_rates[i]

                self.current_send_message_changed.emit(i)
                error = self.send_data(self.bit_str_to_bytearray(msg.encoded_bits_str))
                if not error:
                    logger.debug("Sent message {0}/{1}".format(i+1, len(messages)))
                    logger.debug("Waiting message pause: {0:.2f}s".format(wait_time))
                    if self.__sending_interrupt_requested:
                        break
                    time.sleep(wait_time)
                else:
                    self.is_sending = False
                    Errors.generic_error("Could not connect to {0}:{1}".format(self.client_ip, self.client_port), msg=error)
                    break
            if repeats > 0:
                repeats -= 1
        logger.debug("Sending finished")
        self.is_sending = False

    def start_message_sending_thread(self, messages, sample_rates, modulators, project_manager):
        self.modulators = modulators
        self.project_manager = project_manager
        self.__sending_interrupt_requested = False
        self.sending_thread = Thread(target=self.__send_messages, args=(messages, sample_rates))
        self.sending_thread.daemon = True
        self.sending_thread.start()

    def stop_sending_thread(self):
        self.__sending_interrupt_requested = True
        self.sending_stop_requested.emit()

    @staticmethod
    def bytearray_to_bit_str(arr: bytearray) -> str:
        return "".join("{:08b}".format(a) for a in arr)

    @staticmethod
    def bit_str_to_bytearray(bits: str) -> bytearray:
        bits += "0" * ((8 - len(bits) % 8) % 8)
        return bytearray((int(bits[i:i+8], 2) for i in range(0, len(bits), 8)))
