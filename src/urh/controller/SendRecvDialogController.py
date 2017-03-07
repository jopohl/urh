import locale
import random
import time

from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QRegExp, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtWidgets import QGraphicsView

from urh import constants
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.PluginManager import PluginManager
from urh.ui.ui_send_recv import Ui_SendRecvDialog
from urh.util.Errors import Errors
from urh.util.Logger import logger


class SendRecvDialogController(QDialog):
    recording_parameters = pyqtSignal(str, str, str, str, str)

    def __init__(self, freq, samp_rate, bw, gain, device: str, parent=None, testing_mode=False):
        super().__init__(parent)
        self.ui = Ui_SendRecvDialog()
        self.ui.setupUi(self)

        self.set_sniff_ui_items_visible(False)

        self.graphics_view = None  # type: QGraphicsView
        self.__device = None  # type: VirtualDevice

        self.backend_handler = BackendHandler(testing_mode=testing_mode)

        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

        self.start = 0

        self.bw_sr_are_locked = constants.SETTINGS.value("lock_bandwidth_sample_rate", True, bool)

        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxSampleRate.setValue(samp_rate)
        self.ui.spinBoxBandwidth.setValue(bw)
        self.ui.spinBoxGain.setValue(gain)
        self.ui.spinBoxNRepeat.setValue(constants.SETTINGS.value('num_sending_repeats', 1, type=int))

        self.ui.cbDevice.clear()
        items = self.get_devices_for_combobox()
        self.ui.cbDevice.addItems(items)

        if device in items:
            self.ui.cbDevice.setCurrentIndex(items.index(device))

        self.timer = QTimer(self)

        dev_name = self.ui.cbDevice.currentText()
        self.set_device_ui_items_visible(dev_name != NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.ui.lineEditIP.setVisible(dev_name == "USRP" or dev_name == "RTL-TCP")
        self.ui.labelIP.setVisible(dev_name == "USRP" or dev_name == "RTL-TCP")
        self.ui.spinBoxPort.setVisible(dev_name == "RTL-TCP")
        self.ui.labelPort.setVisible(dev_name == "RTL-TCP")

        self.ui.btnLockBWSR.setChecked(self.bw_sr_are_locked)
        self.on_btn_lock_bw_sr_clicked()

    @property
    def has_empty_device_list(self):
        return self.ui.cbDevice.count() == 0

    @property
    def device(self) -> VirtualDevice:
        return self.__device

    @device.setter
    def device(self, value):
        self.__device = value

    def hide_send_ui_items(self):
        for item in ("spinBoxNRepeat", "labelNRepeat", "lblCurrentRepeatValue",
                     "lblRepeatText", "lSamplesSentText", "progressBar"):
            getattr(self.ui, item).hide()

    def hide_receive_ui_items(self):
        for item in ("lSamplesCaptured", "lSamplesCapturedText", "lSignalSize", "lSignalSizeText",
                     "lTime", "lTimeText", "btnSave"):
            getattr(self.ui, item).hide()

    def set_sniff_ui_items_visible(self, visible: bool):
        for item in self.ui.__dict__:
            if "_sniff_" in item:
                getattr(self.ui, item).setVisible(visible)

    def set_device_ui_items_visible(self, visible: bool):
        for object in ("spinBoxFreq", "spinBoxSampleRate", "spinBoxBandwidth", "spinBoxGain",
                       "btnLockBWSR", "labelFreq", "labelSampleRate", "labelBandWidth", "labelGain"):
            getattr(self.ui, object).setVisible(visible)

    def set_device_ui_items_enabled(self, enabled: bool):
        self.ui.spinBoxFreq.setEnabled(enabled)
        self.ui.spinBoxGain.setEnabled(enabled)
        self.ui.spinBoxBandwidth.setEnabled(enabled)
        self.ui.spinBoxSampleRate.setEnabled(enabled)

    def get_devices_for_combobox(self):
        items = []
        for device_name in self.backend_handler.DEVICE_NAMES:
            dev = self.backend_handler.device_backends[device_name.lower()]
            if hasattr(self, "is_tx") and dev.is_enabled and dev.supports_tx:
                items.append(device_name)
            elif hasattr(self, "is_rx") and dev.is_enabled and dev.supports_rx:
                items.append(device_name)

        if PluginManager().is_plugin_enabled("NetworkSDRInterface"):
            items.append(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        return items

    def set_bandwidth_status(self):
        if self.device is not None:
            self.ui.spinBoxBandwidth.setEnabled(self.device.bandwidth_is_adjustable)
            self.ui.btnLockBWSR.setEnabled(self.device.bandwidth_is_adjustable)

            if not self.device.bandwidth_is_adjustable:
                self.bw_sr_are_locked = False
                self.ui.spinBoxBandwidth.setToolTip(self.tr("Your driver of RTL-SDR does not support "
                                                            "setting the bandwidth. "
                                                            "If you need this feature, install a recent version."))
            else:
                self.ui.spinBoxBandwidth.setToolTip("")
                self.bw_sr_are_locked = self.ui.btnLockBWSR.isChecked()

    def create_connects(self):
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnStop.clicked.connect(self.on_stop_clicked)
        self.ui.btnClear.clicked.connect(self.on_clear_clicked)

        self.timer.timeout.connect(self.update_view)
        self.ui.spinBoxSampleRate.editingFinished.connect(self.on_sample_rate_changed)
        self.ui.spinBoxGain.editingFinished.connect(self.on_gain_changed)
        self.ui.spinBoxFreq.editingFinished.connect(self.on_freq_changed)
        self.ui.spinBoxBandwidth.editingFinished.connect(self.on_bw_changed)
        self.ui.spinBoxPort.editingFinished.connect(self.on_port_changed)
        self.ui.lineEditIP.editingFinished.connect(self.on_ip_changed)
        self.ui.cbDevice.currentIndexChanged.connect(self.on_selected_device_changed)
        self.ui.sliderYscale.valueChanged.connect(self.on_slider_y_scale_value_changed)

        self.ui.btnLockBWSR.clicked.connect(self.on_btn_lock_bw_sr_clicked)

    def _create_device_connects(self):
        self.device.stopped.connect(self.on_device_stopped)
        self.device.started.connect(self.on_device_started)
        self.device.sender_needs_restart.connect(self._restart_device_thread)

    def reset(self):
        self.ui.txtEditErrors.clear()
        self.device.current_index = 0
        self.device.current_iteration = 0
        self.ui.lSamplesCaptured.setText("0")
        self.ui.lSignalSize.setText("0")
        self.ui.lTime.setText("0")
        self.ui.lblCurrentRepeatValue.setText("-")
        self.scene_manager.set_text("")
        self.ui.progressBar.setValue(0)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)

    def init_device(self):
        pass

    def save_before_close(self):
        return True

    @pyqtSlot()
    def on_sample_rate_changed(self):
        self.device.sample_rate = self.ui.spinBoxSampleRate.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxBandwidth.setValue(self.ui.spinBoxSampleRate.value())
            self.device.bandwidth = self.ui.spinBoxBandwidth.value()

    @pyqtSlot()
    def on_freq_changed(self):
        self.device.frequency = self.ui.spinBoxFreq.value()

    @pyqtSlot()
    def on_bw_changed(self):
        self.device.bandwidth = self.ui.spinBoxBandwidth.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxSampleRate.setValue(self.ui.spinBoxBandwidth.value())
            self.device.sample_rate = self.ui.spinBoxSampleRate.value()

    @pyqtSlot()
    def on_ip_changed(self):
        self.device.ip = self.ui.lineEditIP.text()

    @pyqtSlot()
    def on_port_changed(self):
        self.device.port = self.ui.spinBoxPort.value()

    @pyqtSlot()
    def on_gain_changed(self):
        self.device.gain = self.ui.spinBoxGain.value()

    @pyqtSlot()
    def on_selected_device_changed(self):
        dev_name = self.ui.cbDevice.currentText()

        self.init_device()

        self.graphics_view.scene_manager = self.scene_manager
        self.graphics_view.setScene(self.scene_manager.scene)
        self.set_device_ui_items_visible(dev_name != NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.ui.lineEditIP.setVisible(dev_name == "USRP" or dev_name == "RTL-TCP")
        self.ui.labelIP.setVisible(dev_name == "USRP" or dev_name == "RTL-TCP")
        self.ui.labelPort.setVisible(dev_name == "RTL-TCP")
        self.ui.spinBoxPort.setVisible(dev_name == "RTL-TCP")

        # Set default IPs for USRP and RTLSDRTCP
        if dev_name == "USRP":
            if self.ui.lineEditIP.text() == constants.DEFAULT_IP_RTLSDRTCP:
                self.ui.lineEditIP.setText(constants.DEFAULT_IP_USRP)
        elif dev_name == "RTL-TCP":
            if self.ui.lineEditIP.text() == constants.DEFAULT_IP_USRP:
                self.ui.lineEditIP.setText(constants.DEFAULT_IP_RTLSDRTCP)

        self.set_bandwidth_status()

    @pyqtSlot()
    def on_start_clicked(self):
        self.ui.spinBoxFreq.editingFinished.emit()
        self.ui.spinBoxBandwidth.editingFinished.emit()
        self.ui.spinBoxGain.editingFinished.emit()
        self.ui.spinBoxNRepeat.editingFinished.emit()
        self.ui.spinBoxSampleRate.editingFinished.emit()
        if self.ui.cbDevice.currentText() in ("USRP", "RTL-TCP"):
            self.ui.lineEditIP.editingFinished.emit()
        if self.ui.cbDevice.currentText() == "RTL-TCP":
            self.ui.spinBoxPort.editingFinished.emit()

    @pyqtSlot()
    def on_stop_clicked(self):
        self.device.stop("Stopped receiving: Stop button clicked")

    @pyqtSlot()
    def on_device_stopped(self):
        self.graphics_view.capturing_data = False
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(True)
        self.ui.btnSave.setEnabled(self.device.current_index > 0)
        self.ui.spinBoxSampleRate.setEnabled(True)
        self.ui.spinBoxFreq.setEnabled(True)
        self.ui.lineEditIP.setEnabled(True)
        self.ui.spinBoxBandwidth.setEnabled(True)
        self.ui.spinBoxGain.setEnabled(True)
        self.ui.spinBoxPort.setEnabled(True)
        self.ui.cbDevice.setEnabled(True)
        self.ui.spinBoxNRepeat.setEnabled(True)
        self.timer.stop()
        self.scene_manager.set_text("")
        self.update_view()

    @pyqtSlot()
    def on_device_started(self):
        self.ui.txtEditErrors.clear()
        self.scene_manager.set_text("Waiting for device..")
        self.graphics_view.capturing_data = True
        self.ui.btnSave.setEnabled(False)
        self.ui.btnStart.setEnabled(False)

        self.ui.btnClear.setEnabled(False)
        self.ui.spinBoxNRepeat.setEnabled(False)
        self.ui.btnStop.setEnabled(True)

        self.ui.lineEditIP.setDisabled(True)
        self.ui.spinBoxPort.setDisabled(True)
        self.ui.cbDevice.setDisabled(True)
        self.timer.start(self.update_interval)

    def update_view(self):
        self.ui.sliderYscale.setValue(int(self.graphics_view.transform().m22()))

        txt = self.ui.txtEditErrors.toPlainText()
        new_errors = self.device.read_errors()

        if "No devices found for" in new_errors:
            self.device.stop_on_error("Could not establish connection to USRP")
            Errors.usrp_ip_not_found()

            self.on_clear_clicked()

        elif "OSError" in new_errors:
            self.device.stop_on_error("OSError")
            self.on_clear_clicked()

        elif "FATAL: No supported devices found" in new_errors or \
                        "HACKRF_ERROR_NOT_FOUND" in new_errors or \
                        "HACKRF_ERROR_LIBUSB" in new_errors:
            self.device.stop_on_error("Could not establish connection to HackRF")
            Errors.hackrf_not_found()
            self.on_clear_clicked()

        elif "No module named gnuradio" in new_errors:
            self.device.stop_on_error("Did not find gnuradio.")
            Errors.gnuradio_not_installed()
            self.on_clear_clicked()

        elif "RTLSDR-open: Error Code: -1" in new_errors:
            self.device.stop_on_error("Could not open a RTL-SDR device.")
            self.on_clear_clicked()

        elif "Address already in use" in new_errors:
            self._restart_device_thread()

        if len(new_errors) > 1:
            self.ui.txtEditErrors.setPlainText(txt + new_errors)

        self.ui.progressBar.setValue(self.device.current_index)

        self.ui.lSamplesCaptured.setText("{0:n}".format(self.device.current_index))
        self.ui.lSignalSize.setText(locale.format_string("%.2f", (8 * self.device.current_index) / (1024 ** 2)))
        self.ui.lTime.setText(locale.format_string("%.2f", self.device.current_index / self.device.sample_rate))

        if self.device.current_index == 0:
            return False

        return True

    def _restart_device_thread(self):
        self.device.stop("Restarting with new port")
        QApplication.processEvents()

        self.device.port = random.randint(1024, 65536)
        logger.info("Retry with port " + str(self.device.port))

        self.device.start()
        QApplication.processEvents()

    @pyqtSlot()
    def on_clear_clicked(self):
        pass

    def closeEvent(self, event: QCloseEvent):
        if self.device.backend == Backends.network:
            event.accept()
            return

        self.device.stop("Dialog closed. Killing recording process.")
        logger.debug("Device stopped successfully.")
        if not self.save_before_close():
            event.ignore()
            return

        time.sleep(0.1)
        if self.device.backend != Backends.none:
            # Backend none is selected, when no device is available
            logger.debug("Cleaning up device")
            self.device.cleanup()
            logger.debug("Successfully cleaned up device")
            self.recording_parameters.emit(str(self.device.frequency),
                                           str(self.device.sample_rate),
                                           str(self.device.bandwidth),
                                           str(self.device.gain),
                                           str(self.device.name))

        event.accept()

    @pyqtSlot()
    def on_btn_lock_bw_sr_clicked(self):
        self.bw_sr_are_locked = self.ui.btnLockBWSR.isChecked()
        constants.SETTINGS.setValue("lock_bandwidth_sample_rate", self.bw_sr_are_locked)
        if self.bw_sr_are_locked:
            self.ui.btnLockBWSR.setIcon(QIcon(":/icons/data/icons/lock.svg"))
            self.ui.spinBoxBandwidth.setValue(self.ui.spinBoxSampleRate.value())
            self.ui.spinBoxBandwidth.editingFinished.emit()
        else:
            self.ui.btnLockBWSR.setIcon(QIcon(":/icons/data/icons/unlock.svg"))

    @pyqtSlot(int)
    def on_slider_y_scale_value_changed(self, new_value: int):
        # Scale Up = Top Half, Scale Down = Lower Half
        transform = self.graphics_view.transform()
        self.graphics_view.setTransform(QTransform(transform.m11(), transform.m12(), transform.m13(),
                                                   transform.m21(), new_value, transform.m23(),
                                                   transform.m31(), transform.m32(), transform.m33()))
