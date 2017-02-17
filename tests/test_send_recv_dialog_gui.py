import socket
import unittest

import numpy as np
from PyQt5.QtTest import QTest

import tests.utils_testing
from tests.utils_testing import get_path_for_data_file
from urh import constants
from urh.controller.MainController import MainController
from urh.controller.ReceiveDialogController import ReceiveDialogController
from urh.controller.SendDialogController import SendDialogController
from urh.controller.SpectrumDialogController import SpectrumDialogController
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin

app = tests.utils_testing.app


class TestSendRecvDialog(unittest.TestCase):
    def setUp(self):
        constants.SETTINGS.setValue("NetworkSDRInterface", True)
        network_sdr_plugin = NetworkSDRInterfacePlugin()
        network_sdr_plugin.qsettings.setValue("client_port", 2222)
        network_sdr_plugin.qsettings.setValue("server_port", 2222)

        self.form = MainController()
        self.form.add_signalfile(get_path_for_data_file("esaver.complex"))
        self.signal = self.form.signal_tab_controller.signal_frames[0].signal
        self.gframe = self.form.generator_tab_controller
        self.form.ui.tabWidget.setCurrentIndex(2)

        project_manager = self.form.project_manager
        self.receive_dialog = ReceiveDialogController(project_manager.frequency, project_manager.sample_rate,
                                                      project_manager.bandwidth, project_manager.gain,
                                                      project_manager.device, testing_mode=True)

        self.send_dialog = SendDialogController(project_manager.frequency, project_manager.sample_rate,
                                                project_manager.bandwidth, project_manager.gain,
                                                project_manager.device,
                                                modulated_data=self.signal.data, testing_mode=True)
        self.send_dialog.graphics_view.show_full_scene(reinitialize=True)

        self.spectrum_dialog = SpectrumDialogController(project_manager.frequency, project_manager.sample_rate,
                                                        project_manager.bandwidth, project_manager.gain,
                                                        project_manager.device, testing_mode=True)

        self.dialogs = [self.receive_dialog, self.send_dialog, self.spectrum_dialog]

    def test_network_sdr_enabled(self):
        for dialog in self.dialogs:
            items = [dialog.ui.cbDevice.itemText(i) for i in range(dialog.ui.cbDevice.count())]
            if isinstance(dialog, SpectrumDialogController):
                self.assertNotIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)
            else:
                self.assertIn(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME, items)

    def test_receive(self):
        self.receive_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.receive_dialog.ui.btnStart.click()
        network_sdr_plugin = NetworkSDRInterfacePlugin()
        data = np.array([complex(1, 2), complex(3, 4), complex(5, 6)], dtype=np.complex64)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(("127.0.0.1", network_sdr_plugin.server_port))
        sock.sendall(data.tostring())
        sock.close()

        QTest.qWait(100)

        self.assertEqual(self.receive_dialog.device.current_index, 3)
        self.assertEqual(self.receive_dialog.device.data[:3].all(), data.all())

        self.receive_dialog.ui.btnStop.click()

    def test_send(self):
        self.receive_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.receive_dialog.ui.btnStart.click()

        self.send_dialog.ui.cbDevice.setCurrentText(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)
        self.send_dialog.ui.spinBoxNRepeat.setValue(2)
        self.send_dialog.ui.btnStart.click()
        QTest.qWait(500)

        self.assertEqual(self.receive_dialog.device.current_index, 2 * self.signal.num_samples)
        self.assertEqual(self.receive_dialog.device.data.all(), self.signal.data.all())

    def test_send_dialog_scene_zoom(self):
        self.assertEqual(self.send_dialog.graphics_view.sceneRect().width(), self.signal.num_samples)
        view_width = self.send_dialog.graphics_view.view_rect().width()
        self.send_dialog.graphics_view.zoom(1.1)
        self.assertLess(self.send_dialog.graphics_view.view_rect().width(), view_width)
        self.send_dialog.graphics_view.zoom(0.5)
        self.assertGreater(self.send_dialog.graphics_view.view_rect().width(), view_width)

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
            self.assertEqual(dialog.device.ip, "1.3.3.7")

            dialog.ui.spinBoxFreq.setValue(10e9)
            dialog.ui.spinBoxFreq.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxFreq.text()[-1], "G")
            self.assertEqual(dialog.device.frequency, 10e9)

            dialog.ui.spinBoxSampleRate.setValue(10e9)
            dialog.ui.spinBoxSampleRate.editingFinished.emit()
            self.assertEqual(dialog.ui.spinBoxSampleRate.text()[-1], "G")
            self.assertEqual(dialog.device.sample_rate, 10e9)

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
