import os
import socket
import time
from multiprocessing import Process, Value, Array

import numpy as np
from PyQt5.QtCore import QDir, QEvent, QPoint, Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication

from tests.QtTestCase import QtTestCase
from tests.utils_testing import get_path_for_data_file
from urh import settings
from urh.controller.GeneratorTabController import GeneratorTabController
from urh.controller.MainController import MainController
from urh.controller.dialogs.ContinuousSendDialog import ContinuousSendDialog
from urh.controller.dialogs.ReceiveDialog import ReceiveDialog
from urh.controller.dialogs.SendDialog import SendDialog
from urh.controller.dialogs.SpectrumDialogController import SpectrumDialogController
from urh.dev.BackendHandler import BackendContainer, Backends
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import (
    NetworkSDRInterfacePlugin,
)
from urh.signalprocessing.ContinuousModulator import ContinuousModulator
from urh.signalprocessing.IQArray import IQArray
from urh.signalprocessing.Signal import Signal
from urh.util import util
from urh.util.Logger import logger


def receive(port, current_index, target_index, buffer, ready):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    s.bind(("", port))
    s.listen(1)

    ready.value = 1
    conn, addr = s.accept()

    while True:
        data = conn.recv(65536 * 8)

        if len(data) > 0:
            while len(data) % 8 != 0:
                data += conn.recv(len(data) % 8)

            arr = np.frombuffer(data, dtype=np.complex64)
            data = np.frombuffer(buffer.get_obj(), dtype=np.complex64)
            data[current_index.value : current_index.value + len(arr)] = arr
            current_index.value += len(arr)

        if current_index.value >= target_index - 1:
            break

    conn.close()
    s.close()


class TestSendRecvDialog(QtTestCase):
    def setUp(self):
        super().setUp()
        settings.OVERWRITE_RECEIVE_BUFFER_SIZE = 600000
        self.signal = Signal(get_path_for_data_file("enocean.complex"), "testsignal")
        self.form.ui.tabWidget.setCurrentIndex(2)

    def __get_recv_dialog(self):
        receive_dialog = ReceiveDialog(
            self.form.project_manager, testing_mode=True, parent=self.form
        )
        if self.SHOW:
            receive_dialog.show()

        return receive_dialog

    def __get_send_dialog(self):
        send_dialog = SendDialog(
            self.form.project_manager,
            modulated_data=self.signal.iq_array,
            modulation_msg_indices=None,
            testing_mode=True,
            parent=self.form,
        )
        if self.SHOW:
            send_dialog.show()

        QApplication.instance().processEvents()
        send_dialog.graphics_view.show_full_scene(reinitialize=True)
        return send_dialog

    def __get_continuous_send_dialog(self):
        gframe = self.form.generator_tab_controller
        continuous_send_dialog = ContinuousSendDialog(
            self.form.project_manager,
            gframe.table_model.protocol.messages,
            gframe.modulators,
            self.form.generator_tab_controller.total_modulated_samples,
            parent=self.form,
            testing_mode=True,
        )
        if self.SHOW:
            continuous_send_dialog.show()

        return continuous_send_dialog

    def __get_spectrum_dialog(self):
        spectrum_dialog = SpectrumDialogController(
            self.form.project_manager, testing_mode=True, parent=self.form
        )
        if self.SHOW:
            spectrum_dialog.show()

        return spectrum_dialog

    def __get_sniff_dialog(self):
        assert isinstance(self.form, MainController)
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

    def __add_first_signal_to_generator(self):
        generator_frame = self.form.generator_tab_controller
        generator_frame.ui.cbViewType.setCurrentIndex(0)
        item = generator_frame.tree_model.rootItem.children[0].children[0]
        index = generator_frame.tree_model.createIndex(0, 0, item)
        mimedata = generator_frame.tree_model.mimeData([index])
        generator_frame.table_model.dropMimeData(
            mimedata, 1, -1, -1, generator_frame.table_model.createIndex(0, 0)
        )
        QApplication.instance().processEvents()

    def test_network_sdr_enabled(self):
        for dialog in self.__get_all_dialogs():
            items = [
                dialog.device_settings_widget.ui.cbDevice.itemText(i)
                for i in range(dialog.device_settings_widget.ui.cbDevice.count())
            ]
            self.assertIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)

            dialog.close()

    def test_receive(self):
        port = util.get_free_port()
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(port)
        receive_dialog.ui.btnStart.click()

        data = np.array(
            [complex(1, 2), complex(3, 4), complex(5, 6)], dtype=np.complex64
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", port))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        QTest.qWait(100)

        self.assertEqual(receive_dialog.device.current_index, 3)
        self.assertTrue(
            np.array_equal(
                receive_dialog.device.data[:3].flatten(), data.view(np.float32)
            )
        )

        receive_dialog.ui.btnStop.click()
        receive_dialog.ui.btnClear.click()

        self.assertEqual(receive_dialog.device.current_index, 0)

        receive_dialog.close()

    def test_spectrum(self):
        port = util.get_free_port()
        spectrum_dialog = self.__get_spectrum_dialog()
        spectrum_dialog.device.set_server_port(port)
        spectrum_dialog.ui.btnStart.click()
        self.assertEqual(len(spectrum_dialog.scene_manager.peak), 0)

        data = np.array(
            [complex(1, 1), complex(2, 2), complex(3, 3)], dtype=np.complex64
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", port))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        time.sleep(0.1)
        QTest.qWait(100)

        self.assertGreater(len(spectrum_dialog.scene_manager.peak), 0)
        self.assertIsNone(spectrum_dialog.ui.graphicsViewFFT.scene().frequency_marker)
        spectrum_dialog.ui.btnStop.click()

        self.assertGreater(len(spectrum_dialog.ui.graphicsViewSpectrogram.items()), 0)
        spectrum_dialog.ui.btnClear.click()
        self.assertEqual(len(spectrum_dialog.ui.graphicsViewSpectrogram.items()), 0)

        spectrum_dialog.close()

    def test_send(self):
        port = util.get_free_port()
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(port)
        receive_dialog.ui.btnStart.click()

        send_dialog = self.__get_send_dialog()
        send_dialog.device.set_client_port(port)
        send_dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(2)
        send_dialog.ui.btnStart.click()
        QTest.qWait(250)

        # self.assertEqual(receive_dialog.device.current_index, 2 * self.signal.num_samples)
        self.assertTrue(
            np.array_equal(
                receive_dialog.device.data[: receive_dialog.device.current_index // 2],
                self.signal.iq_array.data,
            )
        )

        self.assertEqual(
            send_dialog.ui.lblCurrentRepeatValue.text(), "Sending finished"
        )
        self.assertFalse(send_dialog.ui.btnStop.isEnabled())
        receive_dialog.ui.btnStop.click()
        self.assertFalse(receive_dialog.ui.btnStop.isEnabled())

        receive_dialog.close()
        send_dialog.close()

    def test_continuous_send_dialog(self):
        self.add_signal_to_form("esaver.complex16s")
        self.__add_first_signal_to_generator()

        port = util.get_free_port()

        gframe = self.form.generator_tab_controller  # type: GeneratorTabController
        for msg in gframe.table_model.protocol.messages:
            msg.pause = 5000

        expected = IQArray(None, np.float32, gframe.total_modulated_samples)
        expected = gframe.modulate_data(expected)
        current_index = Value("L", 0)
        buffer = Array("f", 4 * len(expected))
        ready = Value("i", 0)

        process = Process(
            target=receive, args=(port, current_index, len(expected), buffer, ready)
        )
        process.daemon = True
        process.start()
        n = 0
        while ready.value == 0 and n < 50:  # ensure server is up
            time.sleep(0.1)
            n += 1

        self.assertTrue(ready.value)

        ContinuousModulator.BUFFER_SIZE_MB = 10

        continuous_send_dialog = self.__get_continuous_send_dialog()
        continuous_send_dialog.device.set_client_port(port)
        continuous_send_dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(2)
        continuous_send_dialog.ui.btnStart.click()
        process.join(10)

        # CI sometimes swallows a sample
        self.assertGreaterEqual(current_index.value, len(expected) - 1)

        buffer = np.frombuffer(buffer.get_obj(), dtype=np.float32)
        buffer = buffer.reshape((len(buffer) // 2, 2))

        for i in range(len(expected)):
            self.assertEqual(buffer[i, 0], expected[i, 0], msg=str(i))
            self.assertEqual(buffer[i, 1], expected[i, 1], msg=str(i))

        continuous_send_dialog.ui.btnStop.click()
        continuous_send_dialog.ui.btnClear.click()
        QTest.qWait(1)

        continuous_send_dialog.close()

    def test_sniff(self):
        assert isinstance(self.form, MainController)
        # add a signal so we can use it
        self.add_signal_to_form("esaver.complex16s")
        logger.debug("Added signalfile")
        QApplication.instance().processEvents()

        self.__add_first_signal_to_generator()
        generator_frame = self.form.generator_tab_controller
        self.assertEqual(generator_frame.table_model.rowCount(), 3)

        QApplication.instance().processEvents()
        sniff_dialog = self.__get_sniff_dialog()

        sniff_dialog.sniff_settings_widget.ui.checkBoxAdaptiveNoise.click()
        self.assertTrue(sniff_dialog.sniffer.adaptive_noise)
        sniff_dialog.sniff_settings_widget.ui.btn_sniff_use_signal.click()
        self.assertEqual(
            sniff_dialog.sniff_settings_widget.ui.spinbox_sniff_SamplesPerSymbol.value(),
            self.form.signal_tab_controller.signal_frames[0].signal.samples_per_symbol,
        )

        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.setChecked(False)
        self.assertEqual(
            sniff_dialog.device.name, NetworkSDRInterfacePlugin.NETWORK_SDR_NAME
        )
        sniff_dialog.sniff_settings_widget.ui.comboBox_sniff_viewtype.setCurrentIndex(0)

        port = util.get_free_port()

        sniff_dialog.device.set_server_port(port)
        generator_frame.network_sdr_plugin.client_port = port
        sniff_dialog.ui.btnStart.click()

        for msg in generator_frame.table_model.protocol.messages:
            msg.pause = 100e3

        generator_frame.ui.btnNetworkSDRSend.click()

        n = 0
        while generator_frame.network_sdr_plugin.is_sending and n < 50:
            time.sleep(0.25)
            print("Waiting for messages")

        self.assertFalse(generator_frame.network_sdr_plugin.is_sending)

        QTest.qWait(250)
        received_msgs = sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().split("\n")
        orig_msgs = generator_frame.table_model.protocol.plain_bits_str

        self.assertEqual(len(received_msgs), len(orig_msgs))
        for received, orig in zip(received_msgs, orig_msgs):
            pad = 0 if len(orig) % 8 == 0 else 8 - len(orig) % 8
            self.assertEqual(received, orig + "0" * pad)

        sniff_dialog.ui.btnStop.click()
        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.click()
        self.assertTrue(
            sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().startswith("[")
        )
        sniff_dialog.sniff_settings_widget.ui.checkBox_sniff_Timestamp.click()
        self.assertFalse(
            sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().startswith("[")
        )

        n = self.form.compare_frame_controller.protocol_model.rowCount()
        sniff_dialog.protocol_accepted.emit(sniff_dialog.sniffer.messages)
        QTest.qWait(10)
        self.assertEqual(
            self.form.compare_frame_controller.protocol_model.rowCount(), n + 3
        )

        target_file = os.path.join(QDir.tempPath(), "sniff_file.txt")
        if os.path.isfile(target_file):
            os.remove(target_file)

        sniff_dialog.ui.btnClear.click()
        QApplication.instance().processEvents()
        sniff_dialog.sniff_settings_widget.ui.lineEdit_sniff_OutputFile.setText(
            target_file
        )
        sniff_dialog.sniff_settings_widget.ui.lineEdit_sniff_OutputFile.editingFinished.emit()
        sniff_dialog.ui.btnStart.click()
        QApplication.instance().processEvents()
        self.assertFalse(sniff_dialog.ui.btnAccept.isEnabled())

        generator_frame.ui.btnNetworkSDRSend.click()

        with open(target_file, "r") as f:
            for i, line in enumerate(f):
                pad = 0 if len(orig_msgs[i]) % 8 == 0 else 8 - len(orig_msgs[i]) % 8
                self.assertEqual(line.strip(), orig_msgs[i] + "0" * pad)

        sniff_dialog.ui.btnStop.click()
        self.assertFalse(sniff_dialog.ui.btnStop.isEnabled())

        sniff_dialog.close()

    def test_send_dialog_scene_zoom(self):
        send_dialog = self.__get_send_dialog()
        QApplication.instance().processEvents()
        self.assertEqual(
            send_dialog.graphics_view.sceneRect().width(), self.signal.num_samples
        )
        view_width = send_dialog.graphics_view.view_rect().width()
        send_dialog.graphics_view.zoom(1.1)
        self.assertLess(send_dialog.graphics_view.view_rect().width(), view_width)
        send_dialog.graphics_view.zoom(0.8)
        self.assertLessEqual(
            int(send_dialog.graphics_view.view_rect().width()), int(view_width)
        )

        send_dialog.close()

    def test_send_dialog_delete(self):
        num_samples = self.signal.num_samples
        send_dialog = self.__get_send_dialog()
        self.assertEqual(num_samples, send_dialog.scene_manager.signal.num_samples)
        self.assertEqual(num_samples, len(send_dialog.device.samples_to_send))
        send_dialog.graphics_view.set_horizontal_selection(0, 1337)
        send_dialog.graphics_view.delete_action.trigger()
        self.assertEqual(
            send_dialog.scene_manager.signal.num_samples, num_samples - 1337
        )
        self.assertEqual(len(send_dialog.device.samples_to_send), num_samples - 1337)

        send_dialog.close()

    def test_send_dialog_y_slider(self):
        send_dialog = self.__get_send_dialog()
        QApplication.instance().processEvents()
        y, h = (
            send_dialog.graphics_view.view_rect().y(),
            send_dialog.graphics_view.view_rect().height(),
        )

        send_dialog.ui.sliderYscale.setValue(
            send_dialog.ui.sliderYscale.value()
            + send_dialog.ui.sliderYscale.singleStep()
        )
        self.assertNotEqual(y, send_dialog.graphics_view.view_rect().y())
        self.assertNotEqual(h, send_dialog.graphics_view.view_rect().height())

        send_dialog.close()

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
            self.assertEqual(
                dialog.device_settings_widget.ui.spinBoxFreq.text()[-1], "G"
            )
            self.assertEqual(dialog.device.frequency, 2e9)

            dialog.device_settings_widget.ui.spinBoxSampleRate.setValue(10e6)
            dialog.device_settings_widget.ui.spinBoxSampleRate.editingFinished.emit()
            self.assertEqual(
                dialog.device_settings_widget.ui.spinBoxSampleRate.text()[-1], "M"
            )
            self.assertEqual(dialog.device.sample_rate, 10e6)

            dialog.device_settings_widget.ui.spinBoxBandwidth.setValue(3e6)
            dialog.device_settings_widget.ui.spinBoxBandwidth.editingFinished.emit()
            self.assertEqual(
                dialog.device_settings_widget.ui.spinBoxBandwidth.text()[-1], "M"
            )
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
            self.assertEqual(
                dialog.device_settings_widget.ui.comboBoxDirectSampling.count(), 0
            )
            dialog.device_settings_widget.ui.comboBoxDirectSampling.addItem("test")
            dialog.device_settings_widget.ui.comboBoxDirectSampling.addItem("test1")
            dialog.device_settings_widget.ui.comboBoxDirectSampling.setCurrentIndex(1)
            self.assertEqual(dialog.device.direct_sampling_mode, 1)

            dialog.device_settings_widget.ui.spinBoxNRepeat.setValue(10)
            dialog.device_settings_widget.ui.spinBoxNRepeat.editingFinished.emit()
            self.assertEqual(dialog.device.num_sending_repeats, 10)

            dialog.close()

    def test_device_discovery_button(self):
        dialog = self.__get_recv_dialog()
        dialog.device_settings_widget.ui.cbDevice.setCurrentText("HackRF")
        # Check for segfaults https://github.com/jopohl/urh/issues/758
        dialog.device_settings_widget.ui.btnRefreshDeviceIdentifier.click()

        QApplication.instance().processEvents()
        QTest.qWait(100)
        self.assertTrue(True)
