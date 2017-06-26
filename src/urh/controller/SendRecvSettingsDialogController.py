from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.controller.ModulatorDialogController import ModulatorDialogController
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.PluginManager import PluginManager
from urh.signalprocessing.Message import Message
from urh.signalprocessing.MessageType import MessageType
from urh import SimulatorSettings
from urh.dev import config

from PyQt5.QtCore import pyqtSlot

TX_SUFFIX = "_tx"
TX_PREFIX = "tx_"
RX_PREFIX = "rx_"

class SendRecvSettingsDialogController(ProtocolSniffDialogController):
    def __init__(self, project_manager, noise, center, bit_length, tolerance, modulation_type_index,
                 generator_tab_controller, parent=None):
        super().__init__(project_manager, noise, center, bit_length,
                         tolerance, modulation_type_index, [], parent=parent)

        self.setWindowTitle("Receive/Send settings")

        self.move_widgets()

        self.ui.label_sniff_viewtype.hide()
        self.ui.comboBox_sniff_viewtype.hide()
        self.ui.label_sniff_encoding.hide()
        self.ui.comboBox_sniff_encoding.hide()
        self.ui.label_sniff_OutputFile.hide()
        self.ui.lineEdit_sniff_OutputFile.hide()
        self.ui.groupBox.hide()
        self.ui.txtEditErrors.hide()
        self.ui.widget.hide()

        self.generator_tab_controller = generator_tab_controller
        self.profiles = SimulatorSettings.profiles
        self.block_profile = False
        self.refresh_modulators()

        self.ui.spinBoxGain_tx.setValue(self.ui.spinBoxGain.value())
        self.ui.spinBoxIFGain_tx.setValue(self.ui.spinBoxIFGain.value())
        self.ui.spinBoxBasebandGain_tx.setValue(self.ui.spinBoxBasebandGain.value())
        self.ui.lineEditIP_tx.setValidator(self.ui.lineEditIP.validator())

        self.ui.comboBoxProfiles.clear()

        if len(self.profiles):
            for profile in self.profiles:
                self.ui.comboBoxProfiles.addItem(profile["name"])
        else:
            self.on_add_profile_clicked()

        if len(self.profiles) == 1:
            self.ui.btnRemoveProfile.setDisabled(True)

    def move_widgets(self):
        target_layout = self.ui.scrollAreaContents_rx.layout()

        target_layout.addWidget(self.ui.labelChannel, 0, 0)
        target_layout.addWidget(self.ui.comboBoxChannel, 0, 1)
        target_layout.addWidget(self.ui.labelAntenna, 1, 0)
        target_layout.addWidget(self.ui.comboBoxAntenna, 1, 1)
        target_layout.addWidget(self.ui.labelIP, 2, 0)
        target_layout.addWidget(self.ui.lineEditIP, 2, 1)
        target_layout.addWidget(self.ui.labelPort, 3, 0)
        target_layout.addWidget(self.ui.spinBoxPort, 3, 1)
        target_layout.addWidget(self.ui.labelGain, 4, 0)
        target_layout.addWidget(self.ui.sliderGain, 4, 1)
        target_layout.addWidget(self.ui.spinBoxGain, 4, 2)
        target_layout.addWidget(self.ui.labelIFGain, 5, 0)
        target_layout.addWidget(self.ui.sliderIFGain, 5, 1)
        target_layout.addWidget(self.ui.spinBoxIFGain, 5, 2)
        target_layout.addWidget(self.ui.labelBasebandGain, 6, 0)
        target_layout.addWidget(self.ui.sliderBasebandGain, 6, 1)
        target_layout.addWidget(self.ui.spinBoxBasebandGain, 6, 2)

        target_layout.addWidget(self.ui.label_sniff_Noise, 7, 0)
        target_layout.addWidget(self.ui.spinbox_sniff_Noise, 7, 1)
        target_layout.addWidget(self.ui.label_sniff_Center, 8, 0)
        target_layout.addWidget(self.ui.spinbox_sniff_Center, 8, 1)
        target_layout.addWidget(self.ui.label_sniff_BitLength, 9, 0)
        target_layout.addWidget(self.ui.spinbox_sniff_BitLen, 9, 1)
        target_layout.addWidget(self.ui.label_sniff_Tolerance, 10, 0)
        target_layout.addWidget(self.ui.spinbox_sniff_ErrorTolerance, 10, 1)
        target_layout.addWidget(self.ui.label_sniff_Modulation, 11, 0)
        target_layout.addWidget(self.ui.combox_sniff_Modulation, 11, 1)

    def sync_gain_sliders(self):
        super().sync_gain_sliders()

        conf = self.get_config_for_selected_device()
        prefix = TX_PREFIX

        if prefix + "rf_gain" in conf:
            gain = min(conf[prefix + "rf_gain"], key=lambda x: abs(x - self.ui.spinBoxGain_tx.value()))
            self.ui.spinBoxGain_tx.setValue(gain)
            self.ui.spinBoxGain_tx.valueChanged.emit(gain)
        if prefix + "if_gain" in conf:
            if_gain = min(conf[prefix + "if_gain"], key=lambda x: abs(x - self.ui.spinBoxIFGain_tx.value()))
            self.ui.spinBoxIFGain_tx.setValue(if_gain)
            self.ui.spinBoxIFGain_tx.valueChanged.emit(if_gain)
        if prefix + "baseband_gain" in conf:
            baseband_gain = min(conf[prefix + "baseband_gain"],
                                key=lambda x: abs(x - self.ui.spinBoxBasebandGain_tx.value()))
            self.ui.spinBoxBasebandGain_tx.setValue(baseband_gain)
            self.ui.spinBoxBasebandGain_tx.valueChanged.emit(baseband_gain)

    def set_device_ui_items_visibility(self, device_name: str, adjust_gains=True):
        super().set_device_ui_items_visibility(device_name, adjust_gains)

        key = device_name if device_name in config.DEVICE_CONFIG.keys() else "Fallback"
        conf = config.DEVICE_CONFIG[key]

        prefix = TX_PREFIX
        suffix = TX_SUFFIX
        key_ui_gain_map = {prefix + "rf_gain": "Gain", prefix + "if_gain": "IFGain",
                           prefix + "baseband_gain": "BasebandGain"}
        for conf_key, ui_element in key_ui_gain_map.items():
            getattr(self.ui, "label" + ui_element + suffix).setVisible(conf_key in conf)

            spinbox = getattr(self.ui, "spinBox" + ui_element + suffix)  # type: QSpinBox
            slider = getattr(self.ui, "slider" + ui_element + suffix)  # type: QSlider

            if conf_key in conf:
                gain_values = conf[conf_key]
                assert len(gain_values) >= 2
                spinbox.setMinimum(gain_values[0])
                spinbox.setMaximum(gain_values[-1])
                if adjust_gains:
                    spinbox.setValue(gain_values[len(gain_values) // 2])
                spinbox.setSingleStep(gain_values[1] - gain_values[0])
                spinbox.setVisible(True)

                slider.setMaximum(len(gain_values) - 1)
            else:
                spinbox.setVisible(False)
                slider.setVisible(False)
            getattr(self.ui, "slider" + ui_element + suffix).setVisible(conf_key in conf)

        key_ui_channel_ant_map = {prefix + "antenna": "Antenna", prefix + "channel": "Channel"}
        for conf_key, ui_element in key_ui_channel_ant_map.items():
            getattr(self.ui, "label" + ui_element + suffix).setVisible(conf_key in conf)
            combobox = getattr(self.ui, "comboBox" + ui_element + suffix)  # type: QComboBox
            if conf_key in conf:
                combobox.clear()
                combobox.addItems(conf[conf_key])
                if conf_key + "_default_index" in conf:
                    combobox.setCurrentIndex(conf[conf_key+"_default_index"])

                combobox.setVisible(True)
            else:
                combobox.setVisible(False)

        self.ui.lineEditIP_tx.setVisible("ip" in conf)
        self.ui.labelIP_tx.setVisible("ip" in conf)
        self.ui.spinBoxPort_tx.setVisible("port" in conf)
        self.ui.labelPort_tx.setVisible("port" in conf)

    def get_devices_for_combobox(self):
        items = []
        for device_name in self.backend_handler.DEVICE_NAMES:
            dev = self.backend_handler.device_backends[device_name.lower()]
            if dev.is_enabled and (dev.supports_rx or dev.suports_tx):
                items.append(device_name)

        if PluginManager().is_plugin_enabled("NetworkSDRInterface"):
            items.append(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        return items

    @property
    def current_profile(self):
        index = self.ui.comboBoxProfiles.currentIndex()
        return None if index == -1 else self.profiles[index]

    def create_connects(self):
        super().create_connects()

        self.ui.comboBoxProfiles.editTextChanged.connect(self.on_profile_name_edited)
        self.ui.comboBoxProfiles.currentIndexChanged.connect(self.on_profile_index_changed)
        self.ui.btnAddProfile.clicked.connect(self.on_add_profile_clicked)
        self.ui.btnRemoveProfile.clicked.connect(self.on_remove_profile_clicked)
        self.ui.btnEditModulation.clicked.connect(self.show_modulator_dialog)
        self.ui.cBoxModulations.currentIndexChanged.connect(self.on_selected_modulation_changed)

        self.ui.cbDevice.currentIndexChanged.connect(self.on_device_changed)
        self.ui.lineEditDeviceArgs.textChanged.connect(self.on_device_args_changed)
        self.ui.spinBoxFreq.valueChanged.connect(self.on_center_freq_changed)
        self.ui.spinBoxSampleRate.valueChanged.connect(self.on_sample_rate_changed)
        self.ui.spinBoxBandwidth.valueChanged.connect(self.on_bandwidth_changed)
        self.ui.spinBoxFreqCorrection.valueChanged.connect(self.on_freq_correction_changed)
        self.ui.comboBoxDirectSampling.currentIndexChanged.connect(self.on_direct_sampling_changed)
        self.ui.btnLockBWSR.clicked.connect(self.on_lock_bw_sr_changed)

        for func, suffix in [("on_rx_", ""), ("on_tx_", TX_SUFFIX)]:
            getattr(self.ui, "comboBoxChannel" + suffix).currentIndexChanged.connect(getattr(self, func + "channel_changed"))
            getattr(self.ui, "comboBoxAntenna" + suffix).currentIndexChanged.connect(getattr(self, func + "antenna_changed"))
            getattr(self.ui, "lineEditIP" + suffix).textChanged.connect(getattr(self, func + "ip_changed"))
            getattr(self.ui, "spinBoxPort" + suffix).valueChanged.connect(getattr(self, func + "port_changed"))
            getattr(self.ui, "spinBoxGain" + suffix).valueChanged.connect(getattr(self, func + "rf_gain_changed"))
            getattr(self.ui, "spinBoxIFGain" + suffix).valueChanged.connect(getattr(self, func + "if_gain_changed"))
            getattr(self.ui, "spinBoxBasebandGain" + suffix).valueChanged.connect(getattr(self, func + "baseband_gain_changed"))

        self.ui.spinbox_sniff_Noise.valueChanged.connect(self.on_noise_changed)
        self.ui.spinbox_sniff_Center.valueChanged.connect(self.on_center_changed)
        self.ui.spinbox_sniff_BitLen.valueChanged.connect(self.on_bit_length_changed)
        self.ui.spinbox_sniff_ErrorTolerance.valueChanged.connect(self.on_error_tolerance_changed)
        self.ui.combox_sniff_Modulation.currentIndexChanged.connect(self.on_modulation_changed)

        self.ui.sliderGain_tx.valueChanged.connect(self.on_slider_gain_tx_value_changed)
        self.ui.sliderIFGain_tx.valueChanged.connect(self.on_slider_if_gain_tx_value_changed)
        self.ui.sliderBasebandGain_tx.valueChanged.connect(self.on_slider_baseband_gain_tx_value_changed)

    def set_profile_value(self, key, value):
        if self.current_profile is not None and not self.block_profile:
            self.current_profile[key] = value

    def get_profile_value(self, key):
        if self.current_profile is not None:
            return self.current_profile[key]

    @pyqtSlot()
    def on_add_profile_clicked(self):
        names = [p['name'] for p in self.profiles]
        name = "Profile"
        number = 1

        while name in names:
            name = "Profile " + str(number)
            number += 1

        profile = {}
        profile['name'] = name

        self.profiles.append(profile)
        self.ui.comboBoxProfiles.blockSignals(True)
        self.ui.comboBoxProfiles.addItem(name)
        self.ui.comboBoxProfiles.setCurrentIndex(len(self.profiles) - 1)
        self.ui.comboBoxProfiles.blockSignals(False)
        self.ui.btnRemoveProfile.setEnabled(True)

        self.on_device_changed()
        self.on_device_args_changed(self.ui.lineEditDeviceArgs.text())
        self.on_center_freq_changed(self.ui.spinBoxFreq.value())
        self.on_sample_rate_changed(self.ui.spinBoxSampleRate.value())
        self.on_bandwidth_changed(self.ui.spinBoxBandwidth.value())
        self.on_freq_correction_changed(self.ui.spinBoxFreqCorrection.value())
        self.on_direct_sampling_changed(self.ui.comboBoxDirectSampling.currentIndex())
        self.on_lock_bw_sr_changed()

        for func, suffix in [("on_rx_", ""), ("on_tx_", TX_SUFFIX)]:
            getattr(self, func + "channel_changed")(getattr(self.ui, "comboBoxChannel" + suffix).currentIndex())
            getattr(self, func + "antenna_changed")(getattr(self.ui, "comboBoxAntenna" + suffix).currentIndex())
            getattr(self, func + "ip_changed")(getattr(self.ui, "lineEditIP" + suffix).text())
            getattr(self, func + "port_changed")(getattr(self.ui, "spinBoxPort" + suffix).value())
            getattr(self, func + "rf_gain_changed")(getattr(self.ui, "spinBoxGain" + suffix).value())
            getattr(self, func + "if_gain_changed")(getattr(self.ui, "spinBoxIFGain" + suffix).value())
            getattr(self, func + "baseband_gain_changed")(getattr(self.ui, "spinBoxBasebandGain" + suffix).value())

        self.ui.spinbox_sniff_Noise.valueChanged.emit(self.ui.spinbox_sniff_Noise.value())
        self.ui.spinbox_sniff_Center.valueChanged.emit(self.ui.spinbox_sniff_Center.value())
        self.ui.spinbox_sniff_BitLen.valueChanged.emit(self.ui.spinbox_sniff_BitLen.value())
        self.ui.spinbox_sniff_ErrorTolerance.valueChanged.emit(self.ui.spinbox_sniff_ErrorTolerance.value())
        self.ui.combox_sniff_Modulation.currentIndexChanged.emit(self.ui.combox_sniff_Modulation.currentIndex())

    def on_selected_modulation_changed(self):
        cur_ind = self.ui.cBoxModulations.currentIndex()
        cur_mod = self.generator_tab_controller.modulators[cur_ind]
        self.ui.lCarrierFreqValue.setText(cur_mod.carrier_frequency_str)
        self.ui.lCarrierPhaseValue.setText(cur_mod.carrier_phase_str)
        self.ui.lBitLenValue.setText(cur_mod.bit_len_str)
        self.ui.lSampleRateValue.setText(cur_mod.sample_rate_str)
        mod_type = cur_mod.modulation_type_str
        self.ui.lModTypeValue.setText(mod_type)
        if mod_type == "ASK":
            prefix = "Amplitude"
        elif mod_type == "PSK":
            prefix = "Phase"
        elif mod_type in ("FSK", "GFSK"):
            prefix = "Frequency"
        else:
            prefix = "Unknown Modulation Type (This should not happen...)"

        self.ui.lParamForZero.setText(prefix + " for 0:")
        self.ui.lParamForZeroValue.setText(cur_mod.param_for_zero_str)
        self.ui.lParamForOne.setText(prefix + " for 1:")
        self.ui.lParamForOneValue.setText(cur_mod.param_for_one_str)

    @pyqtSlot()
    def on_remove_profile_clicked(self):
        index = self.ui.comboBoxProfiles.currentIndex()
        self.ui.comboBoxProfiles.removeItem(index)
        self.profiles.remove(self.profiles[index])

        if len(self.profiles) == 1:
            self.ui.btnRemoveProfile.setDisabled(True)

    @pyqtSlot(str)
    def on_profile_name_edited(self, text):
        self.set_profile_value("name", text)

    @pyqtSlot()
    def on_profile_index_changed(self):
        self.block_profile = True

        self.ui.btnLockBWSR.setChecked(self.get_profile_value("bw_sr_locked"))
        self.on_lock_bw_sr_changed()
        self.ui.cbDevice.setCurrentText(self.get_profile_value("device"))
        self.ui.lineEditDeviceArgs.setText(self.get_profile_value("device_args"))
        self.ui.spinBoxFreq.setValue(self.get_profile_value("center_freq"))
        self.ui.spinBoxSampleRate.setValue(self.get_profile_value("sample_rate"))
        self.ui.spinBoxBandwidth.setValue(self.get_profile_value("bandwidth"))
        self.ui.spinBoxFreqCorrection.setValue(self.get_profile_value("freq_correction"))
        self.ui.comboBoxDirectSampling.setCurrentIndex(self.get_profile_value("direct_sampling"))

        for prefix, suffix in [(RX_PREFIX, ""), (TX_PREFIX, TX_SUFFIX)]:
            getattr(self.ui, "comboBoxChannel" + suffix).setCurrentIndex(self.get_profile_value(prefix + "channel"))
            getattr(self.ui, "comboBoxAntenna" + suffix).setCurrentIndex(self.get_profile_value(prefix + "antenna"))
            getattr(self.ui, "lineEditIP" + suffix).setText(self.get_profile_value(prefix + "ip"))
            getattr(self.ui, "spinBoxPort" + suffix).setValue(self.get_profile_value(prefix + "port"))
            getattr(self.ui, "spinBoxGain" + suffix).setValue(self.get_profile_value(prefix + "rf_gain"))
            getattr(self.ui, "spinBoxIFGain" + suffix).setValue(self.get_profile_value(prefix + "if_gain"))
            getattr(self.ui, "spinBoxBasebandGain" + suffix).setValue(self.get_profile_value(prefix + "baseband_gain"))

        self.ui.spinbox_sniff_Noise.setValue(self.get_profile_value("noise"))
        self.ui.spinbox_sniff_Center.setValue(self.get_profile_value("center"))
        self.ui.spinbox_sniff_BitLen.setValue(self.get_profile_value("bit_length"))
        self.ui.spinbox_sniff_ErrorTolerance.setValue(self.get_profile_value("error_tolerance"))
        self.ui.combox_sniff_Modulation.setCurrentIndex(self.get_profile_value("modulation"))

        self.block_profile = False

    def on_device_changed(self):
        device_name = self.ui.cbDevice.currentText()

        if device_name == NetworkSDRInterfacePlugin.NETWORK_SDR_NAME:
            supports_rx = True
            supports_tx = True
        else:
            dev = self.backend_handler.device_backends[device_name.lower()]
            supports_rx = dev.supports_rx
            supports_tx = dev.supports_tx

        self.ui.tabWidget.setTabEnabled(0, supports_rx)
        self.ui.tabWidget.setTabEnabled(1, supports_tx)

        self.set_profile_value("supports_rx", supports_rx)
        self.set_profile_value("supports_tx", supports_tx)
        self.set_profile_value("device", self.ui.cbDevice.currentText())

    def on_device_args_changed(self, text: str):
        self.set_profile_value("device_args", text)

    def on_rx_channel_changed(self, index: int):
        self.set_profile_value(RX_PREFIX + "channel", index)

    def on_rx_antenna_changed(self, index: int):
        self.set_profile_value(RX_PREFIX + "antenna", index)

    def on_rx_ip_changed(self, text: str):
        self.set_profile_value(RX_PREFIX + "ip", text)

    def on_rx_port_changed(self, value):
        self.set_profile_value(RX_PREFIX + "port", value)

    def on_center_freq_changed(self, value):
        self.set_profile_value("center_freq", value)

    def on_sample_rate_changed(self, value):
        self.set_profile_value("sample_rate", value)

    def on_bandwidth_changed(self, value):
        self.set_profile_value("bandwidth", value)

    def on_rx_rf_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "rf_gain", value)

    def on_rx_if_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "if_gain", value)

    def on_rx_baseband_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "baseband_gain", value)

    def on_freq_correction_changed(self, value):
        self.set_profile_value("freq_correction", value)

    def on_direct_sampling_changed(self, index: int):
        self.set_profile_value("direct_sampling", index)

    def on_lock_bw_sr_changed(self):
        self.set_profile_value("bw_sr_locked", self.ui.btnLockBWSR.isChecked())

    def on_noise_changed(self, value):
        self.set_profile_value("noise", value)

    def on_center_changed(self, value):
        self.set_profile_value("center", value)

    def on_bit_length_changed(self, value):
        self.set_profile_value("bit_length", value)

    def on_error_tolerance_changed(self, value):
        self.set_profile_value("error_tolerance", value)

    def on_modulation_changed(self, index: int):
        self.set_profile_value("modulation", index)

    def on_tx_channel_changed(self, index: int):
        self.set_profile_value(TX_PREFIX + "channel", index)

    def on_tx_antenna_changed(self, index: int):
        self.set_profile_value(TX_PREFIX + "antenna", index)

    def on_tx_ip_changed(self, text: str):
        self.set_profile_value(TX_PREFIX + "ip", text)

    def on_tx_port_changed(self, value):
        self.set_profile_value(TX_PREFIX + "port", value)

    def on_tx_rf_gain_changed(self, value):
        dev_conf = self.get_config_for_selected_device()
        try:
            self.ui.sliderGain_tx.setValue(dev_conf[TX_PREFIX + "rf_gain"].index(value))
        except (ValueError, KeyError):
            pass

        self.set_profile_value(TX_PREFIX + "rf_gain", value)

    def on_tx_if_gain_changed(self, value):
        dev_conf = self.get_config_for_selected_device()
        try:
            self.ui.sliderIFGain_tx.setValue(dev_conf[TX_PREFIX + "if_gain"].index(value))
        except (ValueError, KeyError):
            pass

        self.set_profile_value(TX_PREFIX + "if_gain", value)

    def on_tx_baseband_gain_changed(self, value):
        dev_conf = self.get_config_for_selected_device()
        try:
            self.ui.sliderBasebandGain_tx.setValue(dev_conf[TX_PREFIX + "baseband_gain"].index(value))
        except (ValueError, KeyError):
            pass

        self.set_profile_value(TX_PREFIX + "baseband_gain", value)

    @pyqtSlot()
    def show_modulator_dialog(self):
        selected_message = Message([True, False, True, False], 0, [], MessageType("empty"))
        preselected_index = self.ui.cBoxModulations.currentIndex()

        modulator_dialog = ModulatorDialogController(self.generator_tab_controller.modulators, parent=self)
        modulator_dialog.ui.treeViewSignals.setModel(self.generator_tab_controller.tree_model)
        modulator_dialog.ui.treeViewSignals.expandAll()
        modulator_dialog.ui.comboBoxCustomModulations.setCurrentIndex(preselected_index)
        modulator_dialog.showMaximized()

        self.generator_tab_controller.initialize_modulation_dialog(selected_message.encoded_bits_str[0:10], modulator_dialog)

        modulator_dialog.finished.connect(self.refresh_modulators)
        modulator_dialog.finished.connect(self.generator_tab_controller.refresh_pause_list)

    @pyqtSlot()
    def refresh_modulators(self):
        cBoxModulations_generator = self.generator_tab_controller.ui.cBoxModulations
        cBoxModulations_self = self.ui.cBoxModulations

        current_index_generator = cBoxModulations_generator.currentIndex()
        current_index_self = 0

        if type(self.sender()) == ModulatorDialogController:
            current_index_self = self.sender().ui.comboBoxCustomModulations.currentIndex()

        cBoxModulations_generator.clear()
        cBoxModulations_self.clear()

        for modulator in self.generator_tab_controller.modulators:
            cBoxModulations_generator.addItem(modulator.name)
            cBoxModulations_self.addItem(modulator.name)

        cBoxModulations_self.setCurrentIndex(current_index_self)
        cBoxModulations_generator.setCurrentIndex(current_index_generator)

    @pyqtSlot(int)
    def on_slider_gain_tx_value_changed(self, value: int):
        dev_conf = self.get_config_for_selected_device()
        self.ui.spinBoxGain_tx.setValue(dev_conf[TX_PREFIX + "rf_gain"][value])

    @pyqtSlot(int)
    def on_slider_if_gain_tx_value_changed(self, value: int):
        dev_conf = self.get_config_for_selected_device()
        self.ui.spinBoxIFGain_tx.setValue(dev_conf[TX_PREFIX + "if_gain"][value])

    @pyqtSlot(int)
    def on_slider_baseband_gain_tx_value_changed(self, value: int):
        dev_conf = self.get_config_for_selected_device()
        self.ui.spinBoxBasebandGain_tx.setValue(dev_conf[TX_PREFIX + "baseband_gain"][value])