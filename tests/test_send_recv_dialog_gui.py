import os
import socket

import numpy as np
import time
from PyQt5.QtCore import QDir, QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from multiprocessing import Process, Value, Array

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh.controller.MainController import MainController
from urh.controller.dialogs.ContinuousSendDialog import ContinuousSendDialog
from urh.controller.dialogs.ProtocolSniffDialog import ProtocolSniffDialog
from urh.controller.dialogs.ReceiveDialog import ReceiveDialog
from urh.controller.dialogs.SendDialog import SendDialog
from urh.controller.dialogs.SpectrumDialogController import SpectrumDialogController
from urh.dev.BackendHandler import BackendContainer, Backends
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.ContinuousModulator import ContinuousModulator
from urh.signalprocessing.Signal import Signal
from urh.util.Logger import logger
from urh.util.SettingsProxy import SettingsProxy


def receive(port, current_index, target_index, buffer):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.bind(("", port))
    s.listen(1)

    conn, addr = s.accept()

    while True:
        data = conn.recv(65536 * 8)

        if len(data) > 0:
            while len(data) % 8 != 0:
                data += conn.recv(len(data) % 8)

            arr = np.frombuffer(data, dtype=np.complex64)
            data = np.frombuffer(buffer.get_obj(), dtype=np.complex64)
            data[current_index.value:current_index.value+len(arr)] = arr
            current_index.value += len(arr)

        if current_index.value == target_index:
            break

    conn.close()
    s.close()


class TestSendRecvDialog(QtTestCase):
    SEND_RECV_TIMEOUT = 1000

    def setUp(self):
        super().setUp()
        SettingsProxy.OVERWRITE_RECEIVE_BUFFER_SIZE = 10 ** 6
        self.signal = Signal(get_path_for_data_file("esaver.complex"), "testsignal")
        self.form.ui.tabWidget.setCurrentIndex(2)

    def __get_recv_dialog(self):
        receive_dialog = ReceiveDialog(self.form.project_manager, testing_mode=True, parent=self.form)
        if self.SHOW:
            receive_dialog.show()

        return receive_dialog

    def __get_send_dialog(self):
        send_dialog = SendDialog(self.form.project_manager, modulated_data=self.signal.data,
                                 modulation_msg_indices=None,
                                 testing_mode=True, parent=self.form)
        if self.SHOW:
            send_dialog.show()

        QApplication.instance().processEvents()
        send_dialog.graphics_view.show_full_scene(reinitialize=True)
        return send_dialog

    def __get_continuous_send_dialog(self):
        gframe = self.form.generator_tab_controller
        continuous_send_dialog = ContinuousSendDialog(self.form.project_manager,
                                                      gframe.table_model.protocol.messages, gframe.modulators,
                                                      self.form.generator_tab_controller.total_modulated_samples,
                                                      parent=self.form, testing_mode=True)
        if self.SHOW:
            continuous_send_dialog.show()

        return continuous_send_dialog

    def __get_spectrum_dialog(self):
        spectrum_dialog = SpectrumDialogController(self.form.project_manager, testing_mode=True, parent=self.form)
        if self.SHOW:
            spectrum_dialog.show()

        return spectrum_dialog

    def __get_sniff_dialog(self):

        sniff_dialog = self.form.create_protocol_sniff_dialog(testing_mode=True)
        if self.SHOW:
            sniff_dialog.show()

        return sniff_dialog

    def __get_all_dialogs(self):
        yield self.__get_recv_dialog()
        yield self.__get_send_dialog()
        yield self.__get_continuous_send_dialog()
        yield self.__get_spectrum_dialog()
        yield self.__get_sniff_dialog()

    def __close_dialog(self, dialog):
        dialog.close()
        dialog.setParent(None)
        dialog.deleteLater()
        QApplication.instance().processEvents()
        QTest.qWait(self.CLOSE_TIMEOUT)

    def __add_first_signal_to_generator(self):
        generator_frame = self.form.generator_tab_controller
        generator_frame.ui.cbViewType.setCurrentIndex(0)
        item = generator_frame.tree_model.rootItem.children[0].children[0]
        index = generator_frame.tree_model.createIndex(0, 0, item)
        mimedata = generator_frame.tree_model.mimeData([index])
        generator_frame.table_model.dropMimeData(mimedata, 1, -1, -1, generator_frame.table_model.createIndex(0, 0))
        QApplication.instance().processEvents()

    def test_network_sdr_enabled(self):
        for dialog in self.__get_all_dialogs():
            items = [dialog.device_settings_widget.ui.cbDevice.itemText(i) for i in range(dialog.device_settings_widget.ui.cbDevice.count())]
            self.assertIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)

            self.__close_dialog(dialog)

    def test_receive(self):
        port = self.get_free_port()
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(port)
        receive_dialog.ui.btnStart.click()

        data = np.array([complex(1, 2), complex(3, 4), complex(5, 6)], dtype=np.complex64)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", port))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        QApplication.instance().processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

        self.assertEqual(receive_dialog.device.current_index, 3)
        self.assertTrue(np.array_equal(receive_dialog.device.data[:3], data))

        receive_dialog.ui.btnStop.click()
        receive_dialog.ui.btnClear.click()

        self.assertEqual(receive_dialog.device.current_index, 0)

        self.__close_dialog(receive_dialog)

    def test_spectrum(self):
        port = self.get_free_port()
        spectrum_dialog = self.__get_spectrum_dialog()
        spectrum_dialog.device.set_server_port(port)
        spectrum_dialog.ui.btnStart.click()
        self.assertEqual(len(spectrum_dialog.scene_manager.peak), 0)

        data = np.array([complex(1, 1), complex(2, 2), complex(3, 3)], dtype=np.complex64)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", port))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        QApplication.instance().processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

        self.assertGreater(len(spectrum_dialog.scene_manager.peak), 0)
        self.assertIsNone(spectrum_dialog.ui.graphicsViewFFT.scene().frequency_marker)
        w = spectrum_dialog.ui.graphicsViewFFT.viewport()

        # this actually gets the click to the view
        # QTest.mouseMove(w, QPoint(80,80))
        event = QMouseEvent(QEvent.MouseMove, QPoint(80, 80), w.mapToGlobal(QPoint(80, 80)), Qt.LeftButton,
                            Qt.LeftButton, Qt.NoModifier)
        QApplication.postEvent(w, event)
        QApplication.instance().processEvents()
        self.assertIsNotNone(spectrum_dialog.ui.graphicsViewFFT.scene().frequency_marker)

        spectrum_dialog.ui.btnStop.click()

        self.assertGreater(len(spectrum_dialog.ui.graphicsViewSpectrogram.items()), 0)
        spectrum_dialog.ui.btnClear.click()
        self.assertEqual(len(spectrum_dialog.ui.graphicsViewSpectrogram.items()), 0)

        self.__close_dialog(spectrum_dialog)

    def test_send(self):
        port = self.get_free_port()
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(port)
        receive_dialog.ui.btnStart.click()

        send_dialog = self.__get_send_dialog()
        send_dialog.device.set_client_port(port)
        send_dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(2)
        send_dialog.ui.btnStart.click()
        QApplication.instance().processEvents()
        QTest.qWait(5 * self.SEND_RECV_TIMEOUT)

        self.assertEqual(receive_dialog.device.current_index, 2 * self.signal.num_samples)
        self.assertTrue(np.array_equal(receive_dialog.device.data[:receive_dialog.device.current_index // 2],
                                       self.signal.data))

        self.assertEqual(send_dialog.send_indicator.rect().width(), self.signal.num_samples)
        self.assertFalse(send_dialog.ui.btnClear.isEnabled())

        send_dialog.on_clear_clicked()
        self.assertEqual(send_dialog.send_indicator.rect().width(), 0)
        send_dialog.ui.btnStop.click()
        self.assertFalse(send_dialog.ui.btnStop.isEnabled())
        receive_dialog.ui.btnStop.click()
        self.assertFalse(receive_dialog.ui.btnStop.isEnabled())

        self.__close_dialog(receive_dialog)
        self.__close_dialog(send_dialog)

    def test_continuous_send_dialog(self):
        self.add_signal_to_form("esaver.complex")
        self.__add_first_signal_to_generator()

        port = self.get_free_port()

        gframe = self.form.generator_tab_controller
        expected = np.zeros(gframe.total_modulated_samples, dtype=np.complex64)
        expected = gframe.modulate_data(expected)
        current_index = Value("L", 0)
        buffer = Array("f", 4 * len(expected))

        process = Process(target=receive, args=(port, current_index, 2*len(expected), buffer))
        process.daemon = True
        process.start()
        time.sleep(0.1)  # ensure server is up

        ContinuousModulator.BUFFER_SIZE_MB = 10

        continuous_send_dialog = self.__get_continuous_send_dialog()
        continuous_send_dialog.device.set_client_port(port)
        continuous_send_dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(2)
        continuous_send_dialog.ui.btnStart.click()
        QTest.qWait(100)
        time.sleep(1)
        process.join(1)

        # CI sometimes swallows a sample
        self.assertGreaterEqual(current_index.value, len(expected)  - 1)

        buffer = np.frombuffer(buffer.get_obj(), dtype=np.complex64)
        for i in range(len(expected)):
            self.assertEqual(buffer[i], expected[i], msg=str(i))

        continuous_send_dialog.ui.btnStop.click()
        continuous_send_dialog.ui.btnClear.click()
        QTest.qWait(1)

        self.__close_dialog(continuous_send_dialog)

    def test_sniff(self):
        # add a signal so we can use it
        self.add_signal_to_form("esaver.complex")
        logger.debug("Added signalfile")
        QApplication.instance().processEvents()

        self.__add_first_signal_to_generator()
        generator_frame = self.form.generator_tab_controller
        self.assertEqual(generator_frame.table_model.rowCount(), 3)

        QApplication.instance().processEvents()
        sniff_dialog = self.__get_sniff_dialog()
        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.setChecked(False)
        self.assertEqual(sniff_dialog.device.name, NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        sniff_dialog.sniff_settings_widget.ui.comboBox_sniff_viewtype.setCurrentIndex(0)

        port = self.get_free_port()

        sniff_dialog.device.set_server_port(port)
        generator_frame.network_sdr_plugin.client_port = port
        sniff_dialog.ui.btnStart.click()
        QApplication.instance().processEvents()
        generator_frame.ui.btnNetworkSDRSend.click()
        QApplication.instance().processEvents()

        QTest.qWait(self.SEND_RECV_TIMEOUT)
        received_msgs = sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().split("\n")
        orig_msgs = generator_frame.table_model.protocol.plain_bits_str

        self.assertEqual(len(received_msgs), len(orig_msgs))
        for received, orig in zip(received_msgs, orig_msgs):
            pad = 0 if len(orig) % 8 == 0 else 8 - len(orig) % 8
            self.assertEqual(received, orig + "0" * pad)

        sniff_dialog.ui.btnStop.click()
        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.click()
        self.assertTrue(sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().startswith("["))
        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.click()
        self.assertFalse(sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().startswith("["))

        n = self.form.compare_frame_controller.protocol_model.rowCount()
        sniff_dialog.protocol_accepted.emit(sniff_dialog.sniffer.messages)
        QTest.qWait(10)
        self.assertEqual(self.form.compare_frame_controller.protocol_model.rowCount(), n+3)

        target_file = os.path.join(QDir.tempPath(), "sniff_file.txt")
        if os.path.isfile(target_file):
            os.remove(target_file)

        sniff_dialog.ui.btnClear.click()
        QApplication.instance().processEvents()
        sniff_dialog.sniff_settings_widget.ui.lineEdit_sniff_OutputFile.setText(target_file)
        sniff_dialog.sniff_settings_widget.ui.lineEdit_sniff_OutputFile.editingFinished.emit()
        sniff_dialog.ui.btnStart.click()
        QApplication.instance().processEvents()
        self.assertFalse(sniff_dialog.ui.btnAccept.isEnabled())

        generator_frame.ui.btnNetworkSDRSend.click()
        QApplication.instance().processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

        with open(target_file, "r") as f:
            for i, line in enumerate(f):
                pad = 0 if len(orig_msgs[i]) % 8 == 0 else 8 - len(orig_msgs[i]) % 8
                self.assertEqual(line.strip(), orig_msgs[i] + "0" * pad)

        sniff_dialog.ui.btnStop.click()
        self.assertFalse(sniff_dialog.ui.btnStop.isEnabled())

        self.__close_dialog(sniff_dialog)

    def test_send_dialog_scene_zoom(self):
        send_dialog = self.__get_send_dialog()
        QApplication.instance().processEvents()
        self.assertEqual(send_dialog.graphics_view.sceneRect().width(), self.signal.num_samples)
        view_width = send_dialog.graphics_view.view_rect().width()
        send_dialog.graphics_view.zoom(1.1)
        QApplication.instance().processEvents()
        QTest.qWait(50)
        self.assertLess(send_dialog.graphics_view.view_rect().width(), view_width)
        send_dialog.graphics_view.zoom(0.8)
        QApplication.instance().processEvents()
        QTest.qWait(50)
        self.assertLessEqual(int(send_dialog.graphics_view.view_rect().width()), int(view_width))

        self.__close_dialog(send_dialog)

    def test_send_dialog_delete(self):
        num_samples = self.signal.num_samples
        send_dialog = self.__get_send_dialog()
        self.assertEqual(num_samples, send_dialog.scene_manager.signal.num_samples)
        self.assertEqual(num_samples, len(send_dialog.device.samples_to_send))
        send_dialog.graphics_view.set_horizontal_selection(0, 1337)
        send_dialog.graphics_view.delete_action.trigger()
        self.assertEqual(send_dialog.scene_manager.signal.num_samples, num_samples - 1337)
        self.assertEqual(len(send_dialog.device.samples_to_send), num_samples - 1337)

        self.__close_dialog(send_dialog)

    def test_send_dialog_y_slider(self):
        send_dialog = self.__get_send_dialog()
        QApplication.instance().processEvents()
        y, h = send_dialog.graphics_view.view_rect().y(), send_dialog.graphics_view.view_rect().height()

        send_dialog.ui.sliderYscale.setValue(send_dialog.ui.sliderYscale.value() +
                                             send_dialog.ui.sliderYscale.singleStep())
        self.assertNotEqual(y, send_dialog.graphics_view.view_rect().y())
        self.assertNotEqual(h, send_dialog.graphics_view.view_rect().height())

        self.__close_dialog(send_dialog)

    def test_change_device_parameters(self):
        for dialog in self.__get_all_dialogs():
            bh = BackendContainer("test", {Backends.native}, True, True)
            self.assertTrue(bh.is_enabled)
            dialog.backend_handler.device_backends["test"] = bh
            dialog.device_settings_widget.ui.cbDevice.addItem("test")
            dialog.device_settings_widget.ui.cbDevice.setCurrentText("test")
            self.assertEqual(dialog.device.name, "test", msg=type(dialog))
            self.assertEqual(dialog.device.backend, Backends.native, msg=type(dialog))

            dialog.device_settings_widget.ui.lineEditIP.setText("1.3.3.7")
            dialog.device_settings_widget.ui.lineEditIP.editingFinished.emit()
            self.assertEqual(dialog.device.ip, "1.3.3.7", msg=type(dialog))

            dialog.device_settings_widget.ui.spinBoxFreq.setValue(2e9)
            dialog.device_settings_widget.ui.spinBoxFreq.editingFinished.emit()
            self.assertEqual(dialog.device_settings_widget.ui.spinBoxFreq.text()[-1], "G")
            self.assertEqual(dialog.device.frequency, 2e9)

            dialog.device_settings_widget.ui.spinBoxSampleRate.setValue(10e6)
            dialog.device_settings_widget.ui.spinBoxSampleRate.editingFinished.emit()
            self.assertEqual(dialog.device_settings_widget.ui.spinBoxSampleRate.text()[-1], "M")
            self.assertEqual(dialog.device.sample_rate, 10e6)

            dialog.device_settings_widget.ui.spinBoxBandwidth.setValue(3e6)
            dialog.device_settings_widget.ui.spinBoxBandwidth.editingFinished.emit()
            self.assertEqual(dialog.device_settings_widget.ui.spinBoxBandwidth.text()[-1], "M")
            self.assertEqual(dialog.device.bandwidth, 3e6)

            dialog.device_settings_widget.ui.spinBoxGain.setValue(5)
            dialog.device_settings_widget.ui.spinBoxGain.editingFinished.emit()
            self.assertEqual(dialog.device.gain, 5)

            dialog.device_settings_widget.ui.spinBoxIFGain.setValue(10)
            dialog.device_settings_widget.ui.spinBoxIFGain.editingFinished.emit()
            self.assertEqual(dialog.device.if_gain, 10)

            dialog.device_settings_widget.ui.spinBoxBasebandGain.setValue(15)
            dialog.device_settings_widget.ui.spinBoxBasebandGain.editingFinished.emit()
            self.assertEqual(dialog.device.baseband_gain, 15)

            dialog.device_settings_widget.ui.spinBoxFreqCorrection.setValue(40)
            dialog.device_settings_widget.ui.spinBoxFreqCorrection.editingFinished.emit()
            self.assertEqual(dialog.device.freq_correction, 40)
            
            dialog.device_settings_widget.ui.comboBoxDirectSampling.clear()
            self.assertEqual(dialog.device_settings_widget.ui.comboBoxDirectSampling.count(), 0)
            dialog.device_settings_widget.ui.comboBoxDirectSampling.addItem("test")
            dialog.device_settings_widget.ui.comboBoxDirectSampling.addItem("test1")
            dialog.device_settings_widget.ui.comboBoxDirectSampling.setCurrentIndex(1)
            self.assertEqual(dialog.device.direct_sampling_mode, 1)

            dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(10)
            dialog.device_settings_widget.ui.spinBoxNRepeat.editingFinished.emit()
            if dialog.is_tx:
                self.assertEqual(dialog.device.num_sending_repeats, 10)
            else:
                self.assertEqual(dialog.device.num_sending_repeats, None)

            self.__close_dialog(dialog)

