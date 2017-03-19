import os
import socket
import unittest

import numpy as np
from PyQt5.QtCore import QDir
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.controller.ReceiveDialogController import ReceiveDialogController
from urh.controller.SendDialogController import SendDialogController
from urh.controller.SpectrumDialogController import SpectrumDialogController
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.util.Logger import logger

global app
app = tests.utils_testing.get_app()


class TestSendRecvDialog(unittest.TestCase):
    def setUp(self):
        constants.SETTINGS.setValue("NetworkSDRInterface", True)

        QTest.qWait(50)
        logger.debug("init form")
        self.form = MainController()
        logger.debug("initalized form")
        app.processEvents()
        QTest.qWait(100)
        logger.debug("Adding signalfile")
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        logger.debug("Added signalfile")
        app.processEvents()
        self.signal = self.form.signal_tab_controller.signal_frames[0].signal
        self.gframe = self.form.generator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(2)
        app.processEvents()
        QTest.qWait(150)

        project_manager = self.form.project_manager

        logger.debug("Creating Receive Dialog")
        self.receive_dialog = ReceiveDialogController(project_manager, testing_mode=True, parent=self.form)
        app.processEvents()
        QTest.qWait(100)

        logger.debug("Creating Send Dialog")
        self.send_dialog = SendDialogController(project_manager, modulated_data=self.signal.data, testing_mode=True,
                                                parent=self.form)
        self.send_dialog.graphics_view.show_full_scene(reinitialize=True)
        app.processEvents()
        QTest.qWait(100)

        logger.debug("Creating Spectrum Dialog")
        self.spectrum_dialog = SpectrumDialogController(project_manager, testing_mode=True, parent=self.form)
        app.processEvents()
        QTest.qWait(100)

        logger.debug("Creating Sniff Dialog")
        self.sniff_dialog = ProtocolSniffDialogController(project_manager, self.signal.noise_threshold,
                                                          self.signal.qad_center,
                                                          self.signal.bit_len, self.signal.tolerance,
                                                          self.signal.modulation_type,
                                                          testing_mode=True, parent=self.form)
        app.processEvents()
        QTest.qWait(50)

        logger.debug("Created Dialogs")

        self.dialogs = [self.receive_dialog, self.send_dialog, self.spectrum_dialog, self.sniff_dialog]

    def tearDown(self):
        for dialog in self.dialogs:
            dialog.close()
            dialog.setParent(None)
            dialog.deleteLater()
            app.processEvents()
            QTest.qWait(10)
        app.processEvents()
        QTest.qWait(10)
        self.form.close()
        self.form.setParent(None)
        app.processEvents()
        QTest.qWait(10)

    def test_network_sdr_enabled(self):
        for dialog in self.dialogs:
            items = [dialog.ui.cbDevice.itemText(i) for i in range(dialog.ui.cbDevice.count())]
            if isinstance(dialog, SpectrumDialogController):
                self.assertNotIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)
            else:
                self.assertIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)

    def test_receive(self):
        self.receive_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.receive_dialog.device.set_server_port(2222)
        self.receive_dialog.ui.btnStart.click()

        data = np.array([complex(1, 2), complex(3, 4), complex(5, 6)], dtype=np.complex64)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.connect(("127.0.0.1", 2222))
        sock.sendall(data.tostring())
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()

        app.processEvents()
        QTest.qWait(500)

        self.assertEqual(self.receive_dialog.device.current_index, 3)
        self.assertTrue(np.array_equal(self.receive_dialog.device.data[:3], data))

        self.receive_dialog.ui.btnStop.click()
        self.receive_dialog.ui.btnClear.click()

        self.assertEqual(self.receive_dialog.device.current_index, 0)

    def test_send(self):
        self.receive_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.receive_dialog.device.set_server_port(3333)
        self.receive_dialog.ui.btnStart.click()

        self.send_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.send_dialog.device.set_client_port(3333)
        self.send_dialog.ui.spinBoxNRepeat.setValue(2)
        self.send_dialog.ui.btnStart.click()
        app.processEvents()
        QTest.qWait(500)

        self.assertEqual(self.receive_dialog.device.current_index, 2 * self.signal.num_samples)
        self.assertTrue(np.array_equal(self.receive_dialog.device.data[:self.receive_dialog.device.current_index // 2],
                                       self.signal.data))

        self.assertEqual(self.send_dialog.send_indicator.rect().width(), self.signal.num_samples)
        self.assertFalse(self.send_dialog.ui.btnClear.isEnabled())

        self.send_dialog.on_clear_clicked()
        self.assertEqual(self.send_dialog.send_indicator.rect().width(), 0)

    def test_sniff(self):
        # Move with encoding to generator
        gframe = self.form.generator_tab_controller
        gframe.ui.cbViewType.setCurrentIndex(0)
        item = gframe.tree_model.rootItem.children[0].children[0]
        index = gframe.tree_model.createIndex(0, 0, item)
        rect = gframe.ui.treeProtocols.visualRect(index)
        QTest.mousePress(gframe.ui.treeProtocols.viewport(), Qt.LeftButton, pos=rect.center())
        self.assertEqual(gframe.ui.treeProtocols.selectedIndexes()[0], index)
        mimedata = gframe.tree_model.mimeData(gframe.ui.treeProtocols.selectedIndexes())
        gframe.table_model.dropMimeData(mimedata, 1, -1, -1, gframe.table_model.createIndex(0, 0))
        self.assertEqual(gframe.table_model.rowCount(), 3)

        self.sniff_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.assertEqual(self.sniff_dialog.device.name, NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        self.sniff_dialog.device.set_server_port(4444)
        gframe.network_sdr_plugin.client_port = 4444
        self.sniff_dialog.ui.btnStart.click()
        app.processEvents()
        gframe.ui.btnNetworkSDRSend.click()
        app.processEvents()

        QTest.qWait(500)
        received_msgs = self.sniff_dialog.ui.txtEd_sniff_Preview.toPlainText().split("\n")
        orig_msgs = gframe.table_model.protocol.plain_bits_str

        self.assertEqual(len(received_msgs), len(orig_msgs))
        for received, orig in zip(received_msgs, orig_msgs):
            pad = 0 if len(orig) % 8 == 0 else 8 - len(orig) % 8
            self.assertEqual(received, orig + "0" * pad)

        self.sniff_dialog.ui.btnStop.click()
        target_file = os.path.join(QDir.tempPath(), "sniff_file")
        self.assertFalse(os.path.isfile(target_file))

        self.sniff_dialog.ui.btnClear.click()
        app.processEvents()
        self.sniff_dialog.ui.lineEdit_sniff_OutputFile.setText(target_file)
        self.sniff_dialog.ui.btnStart.click()
        app.processEvents()
        self.assertFalse(self.sniff_dialog.ui.btnAccept.isEnabled())

        gframe.ui.btnNetworkSDRSend.click()
        app.processEvents()
        QTest.qWait(500)

        with open(target_file, "r") as f:
            for i, line in enumerate(f):
                pad = 0 if len(orig_msgs[i]) % 8 == 0 else 8 - len(orig_msgs[i]) % 8
                self.assertEqual(line.strip(), orig_msgs[i] + "0" * pad)

        os.remove(target_file)

    def test_send_dialog_scene_zoom(self):
        app.processEvents()
        self.assertEqual(self.send_dialog.graphics_view.sceneRect().width(), self.signal.num_samples)
        view_width = self.send_dialog.graphics_view.view_rect().width()
        self.send_dialog.graphics_view.zoom(1.1)
        app.processEvents()
        self.assertLess(self.send_dialog.graphics_view.view_rect().width(), view_width)
        self.send_dialog.graphics_view.zoom(0.8)
        app.processEvents()
        self.assertLessEqual(self.send_dialog.graphics_view.view_rect().width(), view_width)

    def test_send_dialog_delete(self):
        num_samples = self.signal.num_samples
        self.assertEqual(num_samples, self.send_dialog.scene_manager.signal.num_samples)
        self.assertEqual(num_samples, len(self.send_dialog.device.samples_to_send))
        self.send_dialog.graphics_view.set_selection_area(0, 1337)
        self.send_dialog.graphics_view.delete_action.trigger()
        self.assertEqual(self.send_dialog.scene_manager.signal.num_samples, num_samples - 1337)
        self.assertEqual(len(self.send_dialog.device.samples_to_send), num_samples - 1337)

    def test_send_dialog_y_slider(self):
        y, h = self.send_dialog.graphics_view.view_rect().y(), self.send_dialog.graphics_view.view_rect().height()

        self.send_dialog.ui.sliderYscale.setValue(self.send_dialog.ui.sliderYscale.value() +
                                                  self.send_dialog.ui.sliderYscale.singleStep())
        self.assertNotEqual(y, self.send_dialog.graphics_view.view_rect().y())
        self.assertNotEqual(h, self.send_dialog.graphics_view.view_rect().height())

    def test_change_device_parameters(self):
        for dialog in self.dialogs:
            dialog.ui.cbDevice.setCurrentText("HackRF")
            self.assertEqual(dialog.device.name, "HackRF", msg=type(dialog))

            dialog.ui.cbDevice.setCurrentText("USRP")
            self.assertEqual(dialog.device.name, "USRP", msg=type(dialog))

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

            dialog.ui.spinBoxBandwidth.setValue(1e3)
            dialog.ui.spinBoxBandwidth.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxBandwidth.text()[-1], "K")
            self.assertEqual(dialog.device.bandwidth, 1e3)

            dialog.ui.spinBoxGain.setValue(5)
            dialog.ui.spinBoxGain.editingFinished.emit()
            self.assertEqual(dialog.device.gain, 5)

            dialog.ui.spinBoxNRepeat.setValue(10)
            dialog.ui.spinBoxNRepeat.editingFinished.emit()
            if isinstance(dialog, SendDialogController):
                self.assertEqual(dialog.device.num_sending_repeats, 10)
            else:
                self.assertEqual(dialog.device.num_sending_repeats, None)

            app.processEvents()
