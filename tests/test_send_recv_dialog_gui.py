import os
import socket
import unittest

import numpy as np
from PyQt5.QtCore import QDir
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.controller.ReceiveDialogController import ReceiveDialogController
from urh.controller.SendDialogController import SendDialogController
from urh.controller.SpectrumDialogController import SpectrumDialogController
from urh.dev.BackendHandler import BackendContainer, Backends
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.signalprocessing.Signal import Signal
from urh.util.Logger import logger

app = tests.utils_testing.get_app()


class TestSendRecvDialog(unittest.TestCase):
    SEND_RECV_TIMEOUT = 500
    CLOSE_TIMEOUT = 50

    def setUp(self):
        constants.SETTINGS.setValue("NetworkSDRInterface", True)

        self.form = MainController()
        self.signal = Signal(get_path_for_data_file("esaver.complex"), "testsignal")
        self.form.ui.tabWidget.setCurrentIndex(2)

    def __get_recv_dialog(self):
        receive_dialog = ReceiveDialogController(self.form.project_manager, testing_mode=True, parent=self.form)
        return receive_dialog

    def __get_send_dialog(self):
        send_dialog = SendDialogController(self.form.project_manager, modulated_data=self.signal.data,
                                           testing_mode=True, parent=self.form)
        app.processEvents()
        send_dialog.graphics_view.show_full_scene(reinitialize=True)
        return send_dialog

    def __get_spectrum_dialog(self):
        spectrum_dialog = SpectrumDialogController(self.form.project_manager, testing_mode=True, parent=self.form)
        return spectrum_dialog

    def __get_sniff_dialog(self):
        sniff_dialog = ProtocolSniffDialogController(self.form.project_manager, self.signal.noise_threshold,
                                                     self.signal.qad_center,
                                                     self.signal.bit_len, self.signal.tolerance,
                                                     self.signal.modulation_type,
                                                     testing_mode=True, parent=self.form)
        return sniff_dialog

    def __get_all_dialogs(self):
        yield self.__get_recv_dialog()
        yield self.__get_send_dialog()
        yield self.__get_spectrum_dialog()
        yield self.__get_sniff_dialog()

    def __close_dialog(self, dialog):
        dialog.close()
        tests.utils_testing.short_wait()

    def test_network_sdr_enabled(self):
        for dialog in self.__get_all_dialogs():
            items = [dialog.ui.cbDevice.itemText(i) for i in range(dialog.ui.cbDevice.count())]
            if isinstance(dialog, SpectrumDialogController):
                self.assertNotIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)
            else:
                self.assertIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)

            self.__close_dialog(dialog)

    def test_receive(self):
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(2222)
        receive_dialog.ui.btnStart.click()

        data = np.array([complex(1, 2), complex(3, 4), complex(5, 6)], dtype=np.complex64)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", 2222))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        app.processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

        self.assertEqual(receive_dialog.device.current_index, 3)
        self.assertTrue(np.array_equal(receive_dialog.device.data[:3], data))

        receive_dialog.ui.btnStop.click()
        receive_dialog.ui.btnClear.click()

        self.assertEqual(receive_dialog.device.current_index, 0)

        self.__close_dialog(receive_dialog)

    def test_send(self):
        receive_dialog = self.__get_recv_dialog()
        receive_dialog.device.set_server_port(3333)
        receive_dialog.ui.btnStart.click()

        send_dialog = self.__get_send_dialog()
        send_dialog.device.set_client_port(3333)
        send_dialog.ui.spinBoxNRepeat.setValue(2)
        send_dialog.ui.btnStart.click()
        app.processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

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

    def test_sniff(self):
        # add a signal so we can use it
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        logger.debug("Added signalfile")
        app.processEvents()

        # Move with encoding to generator
        generator_frame = self.form.generator_tab_controller
        generator_frame.ui.cbViewType.setCurrentIndex(0)
        item = generator_frame.tree_model.rootItem.children[0].children[0]
        index = generator_frame.tree_model.createIndex(0, 0, item)
        mimedata = generator_frame.tree_model.mimeData([index])
        generator_frame.table_model.dropMimeData(mimedata, 1, -1, -1, generator_frame.table_model.createIndex(0, 0))
        app.processEvents()
        self.assertEqual(generator_frame.table_model.rowCount(), 3)

        app.processEvents()
        sniff_dialog = self.__get_sniff_dialog()
        self.assertEqual(sniff_dialog.device.name, NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        sniff_dialog.device.set_server_port(4444)
        generator_frame.network_sdr_plugin.client_port = 4444
        sniff_dialog.ui.btnStart.click()
        app.processEvents()
        generator_frame.ui.btnNetworkSDRSend.click()
        app.processEvents()

        QTest.qWait(self.SEND_RECV_TIMEOUT)
        received_msgs = sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().split("\n")
        orig_msgs = generator_frame.table_model.protocol.plain_bits_str

        self.assertEqual(len(received_msgs), len(orig_msgs))
        for received, orig in zip(received_msgs, orig_msgs):
            pad = 0 if len(orig) % 8 == 0 else 8 - len(orig) % 8
            self.assertEqual(received, orig + "0" * pad)

        sniff_dialog.ui.btnStop.click()
        target_file = os.path.join(QDir.tempPath(), "sniff_file")
        self.assertFalse(os.path.isfile(target_file))

        sniff_dialog.ui.btnClear.click()
        app.processEvents()
        sniff_dialog.ui.lineEdit_sniff_OutputFile.setText(target_file)
        sniff_dialog.ui.btnStart.click()
        app.processEvents()
        self.assertFalse(sniff_dialog.ui.btnAccept.isEnabled())

        generator_frame.ui.btnNetworkSDRSend.click()
        app.processEvents()
        QTest.qWait(self.SEND_RECV_TIMEOUT)

        with open(target_file, "r") as f:
            for i, line in enumerate(f):
                pad = 0 if len(orig_msgs[i]) % 8 == 0 else 8 - len(orig_msgs[i]) % 8
                self.assertEqual(line.strip(), orig_msgs[i] + "0" * pad)

        os.remove(target_file)

        sniff_dialog.ui.btnStop.click()
        self.assertFalse(sniff_dialog.ui.btnStop.isEnabled())

        self.__close_dialog(sniff_dialog)

    def test_send_dialog_scene_zoom(self):
        send_dialog = self.__get_send_dialog()
        app.processEvents()
        self.assertEqual(send_dialog.graphics_view.sceneRect().width(), self.signal.num_samples)
        view_width = send_dialog.graphics_view.view_rect().width()
        send_dialog.graphics_view.zoom(1.1)
        app.processEvents()
        self.assertLess(send_dialog.graphics_view.view_rect().width(), view_width)
        send_dialog.graphics_view.zoom(0.8)
        app.processEvents()
        self.assertLessEqual(send_dialog.graphics_view.view_rect().width(), view_width)

        self.__close_dialog(send_dialog)

    def test_send_dialog_delete(self):
        num_samples = self.signal.num_samples
        send_dialog = self.__get_send_dialog()
        self.assertEqual(num_samples, send_dialog.scene_manager.signal.num_samples)
        self.assertEqual(num_samples, len(send_dialog.device.samples_to_send))
        send_dialog.graphics_view.set_selection_area(0, 1337)
        send_dialog.graphics_view.delete_action.trigger()
        self.assertEqual(send_dialog.scene_manager.signal.num_samples, num_samples - 1337)
        self.assertEqual(len(send_dialog.device.samples_to_send), num_samples - 1337)

        self.__close_dialog(send_dialog)

    def test_send_dialog_y_slider(self):
        send_dialog = self.__get_send_dialog()
        app.processEvents()
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
            dialog.ui.cbDevice.addItem("test")
            dialog.ui.cbDevice.setCurrentText("test")
            self.assertEqual(dialog.device.name, "test", msg=type(dialog))
            self.assertEqual(dialog.device.backend, Backends.native, msg=type(dialog))

            dialog.ui.lineEditIP.setText("1.3.3.7")
            dialog.ui.lineEditIP.editingFinished.emit()
            self.assertEqual(dialog.device.ip, "1.3.3.7", msg=type(dialog))

            dialog.ui.spinBoxFreq.setValue(2e9)
            dialog.ui.spinBoxFreq.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxFreq.text()[-1], "G")
            self.assertEqual(dialog.device.frequency, 2e9)

            dialog.ui.spinBoxSampleRate.setValue(10e6)
            dialog.ui.spinBoxSampleRate.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxSampleRate.text()[-1], "M")
            self.assertEqual(dialog.device.sample_rate, 10e6)

            dialog.ui.spinBoxBandwidth.setValue(3e6)
            dialog.ui.spinBoxBandwidth.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxBandwidth.text()[-1], "M")
            self.assertEqual(dialog.device.bandwidth, 3e6)

            dialog.ui.spinBoxGain.setValue(5)
            dialog.ui.spinBoxGain.editingFinished.emit()
            self.assertEqual(dialog.device.gain, 5)

            dialog.ui.spinBoxIFGain.setValue(10)
            dialog.ui.spinBoxIFGain.editingFinished.emit()
            self.assertEqual(dialog.device.if_gain, 10)

            dialog.ui.spinBoxBasebandGain.setValue(15)
            dialog.ui.spinBoxBasebandGain.editingFinished.emit()
            self.assertEqual(dialog.device.baseband_gain, 15)

            dialog.ui.spinBoxFreqCorrection.setValue(40)
            dialog.ui.spinBoxFreqCorrection.editingFinished.emit()
            self.assertEqual(dialog.device.freq_correction, 40)

            self.assertEqual(dialog.ui.comboBoxDirectSampling.count(), 0)
            dialog.ui.comboBoxDirectSampling.addItem("test")
            dialog.ui.comboBoxDirectSampling.addItem("test1")
            dialog.ui.comboBoxDirectSampling.setCurrentIndex(1)
            self.assertEqual(dialog.device.direct_sampling_mode, 1)

            dialog.ui.spinBoxNRepeat.setValue(10)
            dialog.ui.spinBoxNRepeat.editingFinished.emit()
            if isinstance(dialog, SendDialogController):
                self.assertEqual(dialog.device.num_sending_repeats, 10)
            else:
                self.assertEqual(dialog.device.num_sending_repeats, None)

            self.__close_dialog(dialog)
