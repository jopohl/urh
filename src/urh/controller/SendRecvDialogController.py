import locale
import random
import time
import gc

import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication

from urh.util.Formatter import Formatter
from urh.util.Logger import logger

from urh.dev.BackendHandler import BackendHandler, Backends

from urh import constants
from urh.FFTSceneManager import FFTSceneManager
from urh.LiveSceneManager import LiveSceneManager
from urh.dev.VirtualDevice import Mode, VirtualDevice
from urh.ui.ui_send_recv import Ui_SendRecvDialog
from urh.util import FileOperator
from urh.util.Errors import Errors





class SendRecvDialogController(QDialog):
    files_recorded = pyqtSignal(list)
    recording_parameters = pyqtSignal(str, str, str, str, str)

    def __init__(self, freq, samp_rate, bw, gain, device: str, mode: Mode, modulated_data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_SendRecvDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.backend_handler = BackendHandler()
        if mode == Mode.spectrum:
            self.update_interval = 1
        else:
            self.update_interval = 50

        if mode == Mode.send and modulated_data is None:
            raise ValueError("I need modulated data to send!")

        if mode == Mode.receive or mode == Mode.spectrum:
            self.ui.spinBoxNRepeat.hide()
            self.ui.labelNRepeat.hide()
            self.ui.lblCurrentRepeatValue.hide()
            self.ui.lblRepeatText.hide()
            self.ui.lSamplesSentText.hide()
            self.ui.progressBar.hide()

        if mode == Mode.send or mode == Mode.spectrum:
            self.ui.lSamplesCaptured.hide()
            self.ui.lSamplesCapturedText.hide()
            self.ui.lSignalSize.hide()
            self.ui.lSignalSizeText.hide()
            self.ui.lTime.hide()
            self.ui.lTimeText.hide()
            self.ui.btnSave.hide()

        if mode == Mode.spectrum:
            self.setWindowTitle("Spectrum analyzer")

        if mode == Mode.send:
            self.ui.btnStart.setIcon(QIcon.fromTheme("media-playback-start"))
            self.setWindowTitle("Send signal")
            self.ui.btnStart.setToolTip("Send data")
            self.ui.btnStop.setToolTip("Stop sending")
            self.ui.progressBar.setMaximum(len(modulated_data))

        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)
        self.start = 0
        self.already_saved = True
        self.bw_sr_are_locked = constants.SETTINGS.value("lock_bandwidth_sample_rate", True, bool)

        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxSampleRate.setValue(samp_rate)
        self.ui.spinBoxBandwidth.setValue(bw)
        self.ui.spinBoxGain.setValue(gain)
        self.ui.spinBoxNRepeat.setValue(constants.SETTINGS.value('num_sending_repeats', 1, type=int))

        self.ui.cbDevice.clear()
        items = []
        for device_name in self.backend_handler.DEVICE_NAMES:
            dev = self.backend_handler.device_backends[device_name.lower()]
            if mode == Mode.send and dev.is_enabled and dev.supports_tx:
                items.append(device_name)
            elif mode in (Mode.receive, Mode.spectrum) and dev.is_enabled and dev.supports_rx:
                items.append(device_name)

        self.ui.cbDevice.addItems(items)
        if device in items:
            self.ui.cbDevice.setCurrentIndex(items.index(device))


        dev_name = self.ui.cbDevice.currentText()
        nrep = self.ui.spinBoxNRepeat.value()
        self.device = VirtualDevice(self.backend_handler, dev_name, mode, bw, freq, gain, samp_rate, samples_to_send=modulated_data,
                                    device_ip=self.ui.lineEditIP.text(), sending_repeats=nrep, parent=self)
        self.ui.lineEditIP.setVisible(dev_name == "USRP")
        self.ui.labelIP.setVisible(dev_name == "USRP")

        self.recorded_files = []

        self.timer = QTimer(self)

        if mode == Mode.receive or mode == Mode.send:
            self.scene_creator = LiveSceneManager(np.array([]), parent=self) # set really in on_device_started
        else:
            self.scene_creator = FFTSceneManager(parent=self, graphic_view=self.ui.graphicsView)

        self.ui.graphicsView.setScene(self.scene_creator.scene)

        ipRange = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ipRegex = QRegExp("^" + ipRange
                          + "\\." + ipRange
                          + "\\." + ipRange
                          + "\\." + ipRange + "$")
        self.ui.lineEditIP.setValidator(QRegExpValidator(ipRegex))
        self.create_connects()

        self.ui.btnLockBWSR.setChecked(self.bw_sr_are_locked)
        self.on_btn_lock_bw_sr_clicked()

    def create_connects(self):
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnStop.clicked.connect(self.on_stop_clicked)
        self.ui.btnClear.clicked.connect(self.on_clear_clicked)
        self.ui.btnSave.clicked.connect(self.on_save_clicked)

        self.__create_device_connects()

        self.timer.timeout.connect(self.update_view)
        self.ui.spinBoxSampleRate.editingFinished.connect(self.on_sample_rate_changed)
        self.ui.spinBoxGain.editingFinished.connect(self.on_gain_changed)
        self.ui.spinBoxFreq.editingFinished.connect(self.on_freq_changed)
        self.ui.spinBoxBandwidth.editingFinished.connect(self.on_bw_changed)
        self.ui.lineEditIP.editingFinished.connect(self.on_usrp_ip_changed)
        self.ui.cbDevice.currentIndexChanged.connect(self.on_selected_device_changed)
        self.ui.spinBoxNRepeat.editingFinished.connect(self.on_nrepeat_changed)
        self.ui.sliderYscale.valueChanged.connect(self.on_slideyscale_value_changed)
        self.ui.graphicsView.freq_clicked.connect(self.on_graphics_view_freq_clicked)
        self.ui.btnLockBWSR.clicked.connect(self.on_btn_lock_bw_sr_clicked)

        self.ui.graphicsView.zoomed.connect(self.handle_signal_zoomed_or_scrolled)
        self.ui.graphicsView.horizontalScrollBar().valueChanged.connect(self.handle_signal_zoomed_or_scrolled)

    def __create_device_connects(self):
        self.device.stopped.connect(self.on_device_stopped)
        self.device.started.connect(self.on_device_started)
        self.device.sender_needs_restart.connect(self.__restart_device_thread)

    @property
    def mode(self):
        return self.device.mode

    @property
    def has_empty_device_list(self):
        return self.ui.cbDevice.count() == 0

    @pyqtSlot()
    def on_sample_rate_changed(self):
        self.device.sample_rate = self.ui.spinBoxSampleRate.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxBandwidth.setValue(self.ui.spinBoxSampleRate.value())
            self.device.bandwidth = self.ui.spinBoxBandwidth.value()

    @pyqtSlot()
    def on_freq_changed(self):
        self.device.frequency = self.ui.spinBoxFreq.value()
        if self.mode == Mode.spectrum:
            self.scene_creator.scene.center_freq = self.ui.spinBoxFreq.value()
            self.scene_creator.clear_path()
            self.scene_creator.clear_peak()

    @pyqtSlot()
    def on_bw_changed(self):
        self.device.bandwidth = self.ui.spinBoxBandwidth.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxSampleRate.setValue(self.ui.spinBoxBandwidth.value())
            self.device.sample_rate = self.ui.spinBoxSampleRate.value()

    @pyqtSlot()
    def on_usrp_ip_changed(self):
        self.device.ip = self.ui.lineEditIP.text()

    @pyqtSlot()
    def on_gain_changed(self):
        self.device.gain = self.ui.spinBoxGain.value()

    @pyqtSlot()
    def on_selected_device_changed(self):
        dev_name = self.ui.cbDevice.currentText()
        nrep = self.ui.spinBoxNRepeat.value()
        sts = self.device.samples_to_send
        self.device.free_data()
        # gc.collect() # Cant do GC here, because the SencRecvDialog itself would be deleted (see https://github.com/jopohl/urh/issues/83)
        self.device = VirtualDevice(self.backend_handler, dev_name, self.device.mode, self.device.bandwidth, self.device.frequency, self.device.gain,
                                    self.device.sample_rate, sts, self.device.ip, nrep, self)
        self.__create_device_connects()
        del self.scene_creator.plot_data
        if self.mode == Mode.receive or self.mode == Mode.send:
            self.scene_creator = LiveSceneManager(np.array([]), parent=self)
        self.ui.graphicsView.setScene(self.scene_creator.scene)
        self.ui.lineEditIP.setVisible(dev_name == "USRP")
        self.ui.labelIP.setVisible(dev_name == "USRP")

    @pyqtSlot()
    def on_start_clicked(self):
        if self.mode == Mode.send and self.ui.progressBar.value() >= self.ui.progressBar.maximum() - 1:
            self.on_clear_clicked()


        self.ui.spinBoxFreq.editingFinished.emit()
        self.ui.lineEditIP.editingFinished.emit()
        self.ui.spinBoxBandwidth.editingFinished.emit()
        self.ui.spinBoxSampleRate.editingFinished.emit()
        self.ui.spinBoxNRepeat.editingFinished.emit()

        self.device.start()

    @pyqtSlot()
    def on_nrepeat_changed(self):
        if not self.ui.spinBoxNRepeat.isVisible():
            return

        self.device.num_sending_repeats = self.ui.spinBoxNRepeat.value()

    @pyqtSlot()
    def on_stop_clicked(self):
        self.device.stop("Stopped receiving: Stop button clicked")

    @pyqtSlot()
    def on_device_stopped(self):
        self.ui.graphicsView.capturing_data = False
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(True)
        self.ui.btnSave.setEnabled(self.device.current_index > 0)
        self.ui.spinBoxSampleRate.setEnabled(True)
        self.ui.spinBoxFreq.setEnabled(True)
        self.ui.lineEditIP.setEnabled(True)
        self.ui.spinBoxBandwidth.setEnabled(True)
        self.ui.spinBoxGain.setEnabled(True)
        self.ui.cbDevice.setEnabled(True)
        self.ui.spinBoxNRepeat.setEnabled(True)
        self.timer.stop()
        self.scene_creator.set_text("")
        self.update_view()

    @pyqtSlot()
    def on_device_started(self):
        if self.mode == Mode.receive or self.mode == Mode.send:
            self.scene_creator.plot_data = self.device.data.real if self.device.data is not None else None

        self.ui.txtEditErrors.clear()
        self.scene_creator.set_text("Waiting for device..")
        self.ui.graphicsView.capturing_data = True
        self.ui.btnSave.setEnabled(False)
        self.ui.btnStart.setEnabled(False)
        self.ui.btnClear.setEnabled(self.mode == Mode.spectrum)
        self.ui.spinBoxNRepeat.setEnabled(False)
        self.ui.btnStop.setEnabled(True)

        if self.mode != Mode.spectrum:
            self.ui.spinBoxSampleRate.setDisabled(True)
            self.ui.spinBoxFreq.setDisabled(True)
            self.ui.spinBoxGain.setDisabled(True)
            self.ui.spinBoxBandwidth.setDisabled(True)

        self.ui.lineEditIP.setDisabled(True)
        self.ui.cbDevice.setDisabled(True)
        self.timer.start(self.update_interval)
        self.already_saved = False

    def update_view(self):
        txt = self.ui.txtEditErrors.toPlainText()
        new_errors = self.device.read_errors()

        if "No devices found for" in new_errors:
            self.device.stop_on_error("Could not establish connection to USRP")
            Errors.usrp_ip_not_found()

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

        elif "Address already in use" in new_errors:
            self.__restart_device_thread()

        if len(new_errors) > 1:
            self.ui.txtEditErrors.setPlainText(txt + new_errors)

        self.ui.progressBar.setValue(self.device.current_index)

        self.ui.lSamplesCaptured.setText("{0:n}".format(self.device.current_index))
        self.ui.lSignalSize.setText("{0:n}".format((8 * self.device.current_index) / (1024 ** 2)))
        self.ui.lTime.setText(locale.format_string("%.2f", self.device.current_index / self.device.sample_rate))
        if not self.device.sending_finished:
            self.ui.lblCurrentRepeatValue.setText(str(self.device.current_iteration + 1))
        else:
            self.ui.lblCurrentRepeatValue.setText("Done")

        if self.device.current_index == 0:
            return

        if self.mode == Mode.send or self.mode == Mode.receive:
            self.ui.graphicsView.horizontalScrollBar().blockSignals(True)
            self.scene_creator.end = self.device.current_index
        elif self.mode == Mode.spectrum:
            x, y = self.device.spectrum
            if x is None or y is None:
                return
            self.scene_creator.scene.frequencies = x
            self.scene_creator.plot_data = y


        self.scene_creator.init_scene()
        self.scene_creator.show_full_scene()
        self.ui.graphicsView.update()

    def __restart_device_thread(self):
        self.device.stop("Restarting with new port")
        QApplication.processEvents()

        self.device.port = random.randint(1024, 65536)
        logger.info("Retry with port " + str(self.device.port))

        self.device.start()
        QApplication.processEvents()

    @pyqtSlot()
    def on_clear_clicked(self):
        if self.mode != Mode.spectrum:
            self.ui.txtEditErrors.clear()
            self.device.current_index = 0
            self.scene_creator.clear_path()
            self.device.current_iteration = 0
            self.ui.graphicsView.repaint()
            self.ui.lSamplesCaptured.setText("0")
            self.ui.lSignalSize.setText("0")
            self.ui.lTime.setText("0")
            self.ui.lblCurrentRepeatValue.setText("-")
            self.scene_creator.set_text("")
            self.ui.progressBar.setValue(0)
            self.ui.btnClear.setEnabled(False)
            self.ui.btnSave.setEnabled(False)
        else:
            self.scene_creator.clear_path()
            self.scene_creator.clear_peak()

    def on_save_clicked(self):
        data = self.device.data[:self.device.current_index]

        dev = self.device
        big_val = Formatter.big_value_with_suffix
        inital_name = "{0} {1}Hz {2}Sps {3}Hz.complex".format(dev.name, big_val(dev.frequency),
                                                      big_val(dev.sample_rate),
                                                      big_val(dev.bandwidth)).replace(Formatter.local_decimal_seperator(), "_").replace("_000","")

        filename = FileOperator.save_data_dialog(inital_name, data, parent=self)
        self.already_saved = True
        if filename is not None and filename not in self.recorded_files:
            self.recorded_files.append(filename)


    def closeEvent(self, QCloseEvent):
        self.device.stop("Dialog closed. Killing recording process.")
        if self.mode == Mode.receive and not self.already_saved and self.device.current_index > 0:
            reply = QMessageBox.question(self, self.tr("Save data?"),
                                         self.tr("Do you want to save the data you have captured so far?"),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
            if reply == QMessageBox.Yes:
                self.on_save_clicked()
            elif reply == QMessageBox.Abort:
                QCloseEvent.ignore()
                return

        time.sleep(0.1)
        if self.device.backend != Backends.none:
            self.device.cleanup()
            self.files_recorded.emit(self.recorded_files)
            self.recording_parameters.emit(str(self.device.frequency),
                                           str(self.device.sample_rate),
                                           str(self.device.bandwidth),
                                           str(self.device.gain),
                                           str(self.device.name))

        QCloseEvent.accept()

    def handle_signal_zoomed_or_scrolled(self):
        if not self.ui.graphicsView.capturing_data:
            x1 = self.ui.graphicsView.view_rect().x()
            x2 = x1 + self.ui.graphicsView.view_rect().width()
            self.scene_creator.show_scene_section(x1, x2)

    def on_btn_lock_bw_sr_clicked(self):
        self.bw_sr_are_locked = self.ui.btnLockBWSR.isChecked()
        constants.SETTINGS.setValue("lock_bandwidth_sample_rate", self.bw_sr_are_locked)
        if self.bw_sr_are_locked:
            self.ui.btnLockBWSR.setIcon(QIcon(":/icons/data/icons/lock.svg"))
        else:
             self.ui.btnLockBWSR.setIcon(QIcon(":/icons/data/icons/unlock.svg"))


    @pyqtSlot(int)
    def on_slideyscale_value_changed(self, new_value: int):
        # Scale Up = Top Half, Scale Down = Lower Half
        middle = int((self.ui.sliderYscale.maximum() + 1 - self.ui.sliderYscale.minimum()) / 2)
        scale_up = new_value >= middle
        current_factor = self.ui.graphicsView.sceneRect().height() / self.ui.graphicsView.view_rect().height()
        scale_factor = (new_value + 1 - middle) / current_factor if scale_up else current_factor / new_value
        if scale_factor > 0:
            self.ui.graphicsView.scale(1, scale_factor)

    @pyqtSlot(float)
    def on_graphics_view_freq_clicked(self, freq: float):
        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxFreq.editingFinished.emit()