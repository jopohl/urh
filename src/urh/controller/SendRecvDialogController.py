import locale
import random
import time
from enum import Enum

from PyQt5.QtCore import Qt, pyqtSlot, QTimer, QRegExp, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtWidgets import QDialog, QMessageBox, QApplication

from urh import constants
from urh.FFTSceneManager import FFTSceneManager
from urh.LiveSceneManager import LiveSceneManager
from urh.dev.ReceiverThread import ReceiverThread
from urh.dev.SenderThread import SenderThread
from urh.dev.SpectrumThread import SpectrumThread
from urh.ui.ui_send_recv import Ui_SendRecvDialog
from urh.util import FileOperator
from urh.util.Errors import Errors


class Mode(Enum):
    receive = 1
    send = 2
    spectrum = 3


class SendRecvDialogController(QDialog):
    files_recorded = pyqtSignal(list)
    recording_parameters = pyqtSignal(str, str, str, str, str)

    def __init__(self, freq, samp_rate, bw, gain, device, mode: Mode, modulated_data=None, parent=None):
        super().__init__(parent)
        self.ui = Ui_SendRecvDialog()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.update_interval = 125

        self.mode = mode  # recv, send, or spectrum
        if self.mode == Mode.send and modulated_data is None:
            raise ValueError("I need modulated data to send!")

        if self.mode == Mode.receive or self.mode == Mode.spectrum:
            self.ui.spinBoxNRepeat.hide()
            self.ui.labelNRepeat.hide()
            self.ui.lblCurrentRepeatValue.hide()
            self.ui.lblRepeatText.hide()
            self.ui.lSamplesSentText.hide()
            self.ui.progressBar.hide()

        if self.mode == Mode.send or self.mode == Mode.spectrum:
            self.ui.lSamplesCaptured.hide()
            self.ui.lSamplesCapturedText.hide()
            self.ui.lSignalSize.hide()
            self.ui.lSignalSizeText.hide()
            self.ui.lTime.hide()
            self.ui.lTimeText.hide()
            self.ui.btnSave.hide()

        if self.mode == Mode.spectrum:
            self.setWindowTitle("Spectrum analyzer")

        if self.mode == Mode.send:
            self.ui.btnStart.setIcon(QIcon.fromTheme("media-playback-start"))
            self.setWindowTitle("Send signal")
            self.ui.btnStart.setToolTip("Send data")

        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(False)
        self.ui.btnSave.setEnabled(False)
        self.start = 0
        self.already_saved = True

        self.ui.spinBoxFreq.setValue(freq)
        self.ui.spinBoxSampleRate.setValue(samp_rate)
        self.ui.spinBoxBandwidth.setValue(bw)
        self.ui.spinBoxGain.setValue(gain)
        self.ui.spinBoxNRepeat.setValue(constants.SETTINGS.value('num_sending_repeats', type=int))

        if self.mode == Mode.receive:
            self.device_thread = ReceiverThread(samp_rate, freq, gain, bw, parent=self)
        elif self.mode == Mode.send:
            self.device_thread = SenderThread(samp_rate, freq, gain, bw, parent=self)
            self.device_thread.data = modulated_data
            self.device_thread.samples_per_transmission = len(modulated_data)

            self.ui.progressBar.setMaximum(len(modulated_data))
        elif self.mode == Mode.spectrum:
            self.device_thread = SpectrumThread(samp_rate, freq, gain, bw, parent=self)

        self.device_thread.usrp_ip = self.ui.lineEditIP.text()

        self.ui.cbDevice.clear()
        items = []
        if constants.SETTINGS.value('usrp_available', type=bool):
            items.append("USRP")
        if constants.SETTINGS.value('hackrf_available', type=bool):
            items.append("HackRF")
        self.ui.cbDevice.addItems(items)
        if device in items:
            self.ui.cbDevice.setCurrentIndex(items.index(device))

        self.on_selected_device_changed()

        self.recorded_files = []

        self.timer = QTimer(self)

        if self.mode == Mode.receive or self.mode == Mode.send:
            self.scene_creator = LiveSceneManager(self.device_thread.data.real, parent=self)
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

    def create_connects(self):
        self.ui.btnStart.clicked.connect(self.on_start_clicked)
        self.ui.btnStop.clicked.connect(self.on_stop_clicked)
        self.ui.btnClear.clicked.connect(self.on_clear_clicked)
        self.ui.btnSave.clicked.connect(self.on_save_clicked)
        self.device_thread.stopped.connect(self.on_device_thread_stopped)
        self.device_thread.started.connect(self.on_device_thread_started)
        self.device_thread.sender_needs_restart.connect(
            self.__restart_device_thread)
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

        self.ui.graphicsView.zoomed.connect(self.handle_signal_zoomed_or_scrolled)
        self.ui.graphicsView.horizontalScrollBar().valueChanged.connect(self.handle_signal_zoomed_or_scrolled)

    @property
    def has_empty_device_list(self):
        return self.ui.cbDevice.count() == 0

    @pyqtSlot()
    def on_sample_rate_changed(self):
        self.device_thread.sample_rate = self.ui.spinBoxSampleRate.value()

    @pyqtSlot()
    def on_freq_changed(self):
        self.device_thread.freq = self.ui.spinBoxFreq.value()
        if self.mode == Mode.spectrum:
            self.scene_creator.scene.center_freq = self.ui.spinBoxFreq.value()
            self.scene_creator.clear_path()

    @pyqtSlot()
    def on_bw_changed(self):
        self.device_thread.bandwidth = self.ui.spinBoxBandwidth.value()

    @pyqtSlot()
    def on_usrp_ip_changed(self):
        self.device_thread.usrp_ip = self.ui.lineEditIP.text()

    @pyqtSlot()
    def on_gain_changed(self):
        self.device_thread.gain = self.ui.spinBoxGain.value()

    @pyqtSlot()
    def on_selected_device_changed(self):
        dev = self.ui.cbDevice.currentText()
        self.device_thread.device = dev
        self.ui.lineEditIP.setVisible(dev == "USRP")
        self.ui.labelIP.setVisible(dev == "USRP")

    @pyqtSlot()
    def on_start_clicked(self):
        if self.mode == Mode.send and self.ui.progressBar.value() >= self.ui.progressBar.maximum() - 1:
            self.on_clear_clicked()

        self.ui.spinBoxFreq.editingFinished.emit()
        self.ui.lineEditIP.editingFinished.emit()
        self.ui.spinBoxBandwidth.editingFinished.emit()
        self.ui.spinBoxSampleRate.editingFinished.emit()
        self.ui.spinBoxNRepeat.editingFinished.emit()

        self.device_thread.setTerminationEnabled(True)
        self.device_thread.terminate()
        time.sleep(0.1)

        self.device_thread.start()

    @pyqtSlot()
    def on_nrepeat_changed(self):
        if not self.ui.spinBoxNRepeat.isVisible():
            return

        if self.device_thread.max_repeats != self.ui.spinBoxNRepeat.value():
            self.device_thread.max_repeats = self.ui.spinBoxNRepeat.value()
            self.device_thread.current_iteration = 0
        self.device_thread.repeat_endless = self.ui.spinBoxNRepeat.value() == 0

    @pyqtSlot()
    def on_stop_clicked(self):
        self.device_thread.stop("Stopped receiving due to user interaction")

    @pyqtSlot()
    def on_device_thread_stopped(self):
        self.ui.graphicsView.capturing_data = False
        self.ui.btnStart.setEnabled(True)
        self.ui.btnStop.setEnabled(False)
        self.ui.btnClear.setEnabled(True)
        self.ui.btnSave.setEnabled(self.device_thread.current_index > 0)
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
    def on_device_thread_started(self):
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
        new_errors = self.device_thread.read_errors()

        if "No devices found for" in new_errors:
            self.device_thread.stop("Could not establish connection to USRP")
            Errors.usrp_ip_not_found()

            self.on_clear_clicked()

        elif "FATAL: No supported devices found" in new_errors or \
                        "HACKRF_ERROR_NOT_FOUND" in new_errors or \
                        "HACKRF_ERROR_LIBUSB" in new_errors:
            self.device_thread.stop("Could not establish connection to HackRF")
            Errors.hackrf_not_found()
            self.on_clear_clicked()

        elif "No module named gnuradio" in new_errors:
            self.device_thread.stop("Did not find gnuradio.")
            Errors.gnuradio_not_installed()
            self.on_clear_clicked()

        elif "Address already in use" in new_errors:
            self.__restart_device_thread()

        if len(new_errors) > 1:
            self.ui.txtEditErrors.setPlainText(txt + new_errors)

        self.ui.progressBar.setValue(self.device_thread.current_index)

        self.ui.lSamplesCaptured.setText("{0:n}".format(self.device_thread.current_index))
        self.ui.lSignalSize.setText("{0:n}".format((8 * self.device_thread.current_index) / (1024 ** 2)))
        self.ui.lTime.setText(locale.format_string("%.2f", self.device_thread.current_index / self.device_thread.sample_rate))
        if self.device_thread.current_iteration is not None:
            self.ui.lblCurrentRepeatValue.setText(str(self.device_thread.current_iteration + 1))
        else:
            self.ui.lblCurrentRepeatValue.setText("Done")

        if self.device_thread.current_index == 0:
            return

        if self.mode == Mode.send or self.mode == Mode.receive:
            self.ui.graphicsView.horizontalScrollBar().blockSignals(True)
            self.scene_creator.end = self.device_thread.current_index
        elif self.mode == Mode.spectrum:
            x, y = self.device_thread.x, self.device_thread.y
            self.scene_creator.scene.frequencies = x
            self.scene_creator.plot_data = y
            if x is None or y is None:
                return

        self.scene_creator.init_scene()
        self.scene_creator.show_full_scene()
        self.ui.graphicsView.update()

    def __restart_device_thread(self):
        self.device_thread.stop("Restarting thread with new port")
        QApplication.processEvents()

        self.device_thread.port = random.randint(1024, 65536)
        print("Retry with port " + str(self.device_thread.port))
        self.device_thread.setTerminationEnabled(True)
        self.device_thread.terminate()
        time.sleep(1)

        self.device_thread.start()
        QApplication.processEvents()

    @pyqtSlot()
    def on_clear_clicked(self):
        if self.mode != Mode.spectrum:
            self.ui.txtEditErrors.clear()
            self.device_thread.clear_data()
            self.scene_creator.clear_path()
            self.device_thread.current_iteration = 0
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

    def on_save_clicked(self):
        data = self.device_thread.data[:self.device_thread.current_index]
        filename = FileOperator.save_data_dialog("recorded", data, parent=self)
        self.already_saved = True
        if filename is not None and filename not in self.recorded_files:
            self.recorded_files.append(filename)


    def closeEvent(self, QCloseEvent):
        self.device_thread.stop("Dialog closed. Killing recording process.")
        if self.mode == Mode.receive and not self.already_saved and self.device_thread.current_index > 0:
            reply = QMessageBox.question(self, self.tr("Save data?"),
                                         self.tr("Do you want to save the data you have captured so far?"),
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Abort)
            if reply == QMessageBox.Yes:
                self.on_save_clicked()
            elif reply == QMessageBox.Abort:
                QCloseEvent.ignore()
                return

        time.sleep(0.1)
        if self.mode == Mode.send:
            self.device_thread.socket.close()

        self.device_thread.data = None

        self.files_recorded.emit(self.recorded_files)
        self.recording_parameters.emit(str(self.device_thread.freq),
                                       str(self.device_thread.sample_rate),
                                       str(self.device_thread.bandwidth),
                                       str(self.device_thread.gain),
                                       str(self.device_thread.device))
        self.device_thread.quit()
        self.device_thread.deleteLater()

        QCloseEvent.accept()

    def handle_signal_zoomed_or_scrolled(self):
        if not self.ui.graphicsView.capturing_data:
            x1 = self.ui.graphicsView.view_rect().x()
            x2 = x1 + self.ui.graphicsView.view_rect().width()
            self.scene_creator.show_scene_section(x1, x2)

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