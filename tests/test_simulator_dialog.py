from array import array

from tests.QtTestCase import QtTestCase
from urh.controller.dialogs.SimulatorDialog import SimulatorDialog
from urh.dev.BackendHandler import BackendContainer, Backends
from urh.signalprocessing.Participant import Participant
from urh.simulator.SimulatorMessage import SimulatorMessage


class TestSimulatorDialog(QtTestCase):
    def setUp(self):
        super().setUp()
        alice = Participant("Alice", "A")
        bob = Participant("Bob", "B")
        alice.simulate = True
        bob.simulate = True
        self.form.project_manager.participants.append(alice)
        self.form.project_manager.participants.append(bob)
        self.form.project_manager.project_updated.emit()

        mt = self.form.compare_frame_controller.proto_analyzer.default_message_type
        msg1 = SimulatorMessage(
            source=bob,
            destination=alice,
            plain_bits=array("B", [1, 0, 1, 1]),
            pause=100,
            message_type=mt,
        )
        msg2 = SimulatorMessage(
            source=alice,
            destination=bob,
            plain_bits=array("B", [1, 0, 1, 1]),
            pause=100,
            message_type=mt,
        )

        simulator_manager = self.form.simulator_tab_controller.simulator_config
        simulator_manager.add_items([msg1, msg2], 0, simulator_manager.rootItem)
        simulator_manager.add_label(
            5, 15, "test", parent_item=simulator_manager.rootItem.children[0]
        )

        self.dialog = SimulatorDialog(
            self.form.simulator_tab_controller.simulator_config,
            self.form.generator_tab_controller.modulators,
            self.form.simulator_tab_controller.sim_expression_parser,
            self.form.project_manager,
        )

        if self.SHOW:
            self.dialog.show()

    def test_set_rx_parameters(self):
        rx_settings_widget = self.dialog.device_settings_rx_widget
        bh = BackendContainer("test", {Backends.native}, True, True)
        self.assertTrue(bh.is_enabled)
        rx_settings_widget.backend_handler.device_backends["test"] = bh
        rx_settings_widget.ui.cbDevice.addItem("test")
        rx_settings_widget.ui.cbDevice.setCurrentText("test")
        self.assertEqual(rx_settings_widget.device.name, "test")
        self.assertEqual(rx_settings_widget.device.backend, Backends.native)

        simulator = self.dialog.simulator
        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxFreq, 500e6)
        self.assertEqual(simulator.sniffer.rcv_device.frequency, 500e6)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxSampleRate, 4e6)
        self.assertEqual(simulator.sniffer.rcv_device.sample_rate, 4e6)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxBandwidth, 5e6)
        self.assertEqual(simulator.sniffer.rcv_device.bandwidth, 5e6)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxGain, 15)
        self.assertEqual(simulator.sniffer.rcv_device.gain, 15)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxIFGain, 10)
        self.assertEqual(simulator.sniffer.rcv_device.if_gain, 10)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxBasebandGain, 11)
        self.assertEqual(simulator.sniffer.rcv_device.baseband_gain, 11)

        self.__edit_spinbox_value(rx_settings_widget.ui.spinBoxFreqCorrection, 22)
        self.assertEqual(simulator.sniffer.rcv_device.freq_correction, 22)

        rx_settings_widget.ui.lineEditIP.setText("4.4.4.4")
        rx_settings_widget.ui.lineEditIP.editingFinished.emit()
        self.assertEqual(simulator.sniffer.rcv_device.ip, "4.4.4.4")

    def test_set_sniff_parameters(self):
        sniff_settings_widget = self.dialog.sniff_settings_widget
        simulator = self.dialog.simulator
        self.__edit_spinbox_value(
            sniff_settings_widget.ui.spinbox_sniff_SamplesPerSymbol, 111
        )
        self.assertEqual(simulator.sniffer.signal.samples_per_symbol, 111)

        self.__edit_spinbox_value(sniff_settings_widget.ui.spinbox_sniff_Center, 0.1337)
        self.assertEqual(simulator.sniffer.signal.center, 0.1337)

        self.__edit_spinbox_value(sniff_settings_widget.ui.spinBoxCenterSpacing, 0.4)
        self.assertEqual(simulator.sniffer.signal.center_spacing, 0.4)

        self.__edit_spinbox_value(
            sniff_settings_widget.ui.spinbox_sniff_ErrorTolerance, 13
        )
        self.assertEqual(simulator.sniffer.signal.tolerance, 13)

        self.__edit_spinbox_value(sniff_settings_widget.ui.spinbox_sniff_Noise, 0.1234)
        self.assertEqual(simulator.sniffer.signal.noise_threshold_relative, 0.1234)

        sniff_settings_widget.ui.combox_sniff_Modulation.setCurrentText("PSK")
        self.assertEqual(simulator.sniffer.signal.modulation_type, "PSK")

        self.__edit_spinbox_value(sniff_settings_widget.ui.spinBoxBitsPerSymbol, 5)
        self.assertEqual(simulator.sniffer.signal.bits_per_symbol, 5)

        decodings = [
            sniff_settings_widget.ui.comboBox_sniff_encoding.itemText(i)
            for i in range(sniff_settings_widget.ui.comboBox_sniff_encoding.count())
        ]
        sniff_settings_widget.ui.comboBox_sniff_encoding.setCurrentIndex(2)
        self.assertEqual(simulator.sniffer.decoder.name, decodings[2])

    def test_set_tx_parameters(self):
        tx_settings_widget = self.dialog.device_settings_tx_widget
        simulator = self.dialog.simulator

        bh = BackendContainer("test", {Backends.native}, True, True)
        self.assertTrue(bh.is_enabled)
        tx_settings_widget.backend_handler.device_backends["test"] = bh
        tx_settings_widget.ui.cbDevice.addItem("test")
        tx_settings_widget.ui.cbDevice.setCurrentText("test")
        self.assertEqual(tx_settings_widget.device.name, "test")
        self.assertEqual(tx_settings_widget.device.backend, Backends.native)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxFreq, 300e6)
        self.assertEqual(simulator.sender.device.frequency, 300e6)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxSampleRate, 5e6)
        self.assertEqual(simulator.sender.device.sample_rate, 5e6)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxBandwidth, 3e6)
        self.assertEqual(simulator.sender.device.bandwidth, 3e6)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxGain, 16)
        self.assertEqual(simulator.sender.device.gain, 16)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxIFGain, 13)
        self.assertEqual(simulator.sender.device.if_gain, 13)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxBasebandGain, 10)
        self.assertEqual(simulator.sender.device.baseband_gain, 10)

        self.__edit_spinbox_value(tx_settings_widget.ui.spinBoxFreqCorrection, 33)
        self.assertEqual(simulator.sender.device.freq_correction, 33)

        tx_settings_widget.ui.lineEditIP.setText("1.2.6.2")
        tx_settings_widget.ui.lineEditIP.editingFinished.emit()
        self.assertEqual(simulator.sender.device.ip, "1.2.6.2")

    def __edit_spinbox_value(self, spinbox, value):
        spinbox.setValue(value)
        spinbox.editingFinished.emit()
