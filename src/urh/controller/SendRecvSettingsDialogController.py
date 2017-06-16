from urh.controller.ContinuousSendDialogController import ContinuousSendDialogController
from urh.controller.ProtocolSniffDialogController import ProtocolSniffDialogController
from urh.ui.ui_send_recv_settings import Ui_SendRecvSettingsDialog
from urh.dev import config

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot

RX_PREFIX = "rx_"
TX_PREFIX = "tx_"

class SendRecvSettingsDialogController(QDialog):
    def __init__(self, project_manager, noise, center, bit_length, tolerance, modulation_type_index,
                 parent=None):
        super().__init__(parent)

        self.ui = Ui_SendRecvSettingsDialog()
        self.ui.setupUi(self)

        self.recv_settings_controller = ProtocolSniffDialogController(project_manager, noise,
                                            center, bit_length, tolerance, modulation_type_index,
                                            [], parent=self)

        self.send_settings_controller = ContinuousSendDialogController(project_manager, [], [], 0, parent=self)

        self.ui.tab_receive.layout().addWidget(self.recv_settings_controller)
        self.ui.tab_send.layout().addWidget(self.send_settings_controller)

        self.setWindowTitle("Receive/Send settings")

        self.recv_settings_controller.ui.label_sniff_viewtype.hide()
        self.recv_settings_controller.ui.comboBox_sniff_viewtype.hide()
        self.recv_settings_controller.ui.label_sniff_encoding.hide()
        self.recv_settings_controller.ui.comboBox_sniff_encoding.hide()
        self.recv_settings_controller.ui.label_sniff_OutputFile.hide()
        self.recv_settings_controller.ui.lineEdit_sniff_OutputFile.hide()
        self.recv_settings_controller.ui.groupBox.hide()
        self.recv_settings_controller.ui.txtEditErrors.hide()
        self.recv_settings_controller.ui.widget.hide()

        self.send_settings_controller.hide_send_ui_items()
        self.send_settings_controller.ui.groupBox.hide()
        self.send_settings_controller.ui.txtEditErrors.hide()
        self.send_settings_controller.ui.widget.hide()

        self.profiles = config.profiles
        self.block_profile = False

        self.ui.comboBoxProfiles.clear()

        if len(self.profiles):
            for profile in self.profiles:
                self.ui.comboBoxProfiles.addItem(profile["name"])
        else:
            self.on_add_profile_clicked()

        if len(self.profiles) == 1:
            self.ui.btnRemoveProfile.setDisabled(True)

        self.create_connects()

    @property
    def current_profile(self):
        index = self.ui.comboBoxProfiles.currentIndex()
        return None if index == -1 else self.profiles[index]

    def create_connects(self):
        self.ui.comboBoxProfiles.editTextChanged.connect(self.on_profile_name_edited)
        self.ui.comboBoxProfiles.currentIndexChanged.connect(self.on_profile_index_changed)
        self.ui.btnAddProfile.clicked.connect(self.on_add_profile_clicked)
        self.ui.btnRemoveProfile.clicked.connect(self.on_remove_profile_clicked)

        self.recv_settings_controller.ui.cbDevice.currentIndexChanged.connect(self.on_rx_device_changed)
        self.recv_settings_controller.ui.lineEditDeviceArgs.textChanged.connect(self.on_rx_device_args_changed)
        self.recv_settings_controller.ui.comboBoxChannel.currentIndexChanged.connect(self.on_rx_channel_changed)
        self.recv_settings_controller.ui.comboBoxAntenna.currentIndexChanged.connect(self.on_rx_antenna_changed)
        self.recv_settings_controller.ui.lineEditIP.textChanged.connect(self.on_rx_ip_changed)
        self.recv_settings_controller.ui.spinBoxPort.valueChanged.connect(self.on_rx_port_changed)
        self.recv_settings_controller.ui.spinBoxFreq.valueChanged.connect(self.on_rx_center_freq_changed)
        self.recv_settings_controller.ui.spinBoxSampleRate.valueChanged.connect(self.on_rx_sample_rate_changed)
        self.recv_settings_controller.ui.spinBoxBandwidth.valueChanged.connect(self.on_rx_bandwidth_changed)
        self.recv_settings_controller.ui.spinBoxGain.valueChanged.connect(self.on_rx_rf_gain_changed)
        self.recv_settings_controller.ui.spinBoxIFGain.valueChanged.connect(self.on_rx_if_gain_changed)
        self.recv_settings_controller.ui.spinBoxBasebandGain.valueChanged.connect(self.on_rx_baseband_gain_changed)
        self.recv_settings_controller.ui.spinBoxFreqCorrection.valueChanged.connect(self.on_rx_freq_correction_changed)
        self.recv_settings_controller.ui.comboBoxDirectSampling.currentIndexChanged.connect(self.on_rx_direct_sampling_changed)
        self.recv_settings_controller.ui.btnLockBWSR.clicked.connect(self.on_rx_btn_lock_bw_sr_clicked)

        self.recv_settings_controller.ui.spinbox_sniff_Noise.valueChanged.connect(self.on_noise_changed)
        self.recv_settings_controller.ui.spinbox_sniff_Center.valueChanged.connect(self.on_center_changed)
        self.recv_settings_controller.ui.spinbox_sniff_BitLen.valueChanged.connect(self.on_bit_length_changed)
        self.recv_settings_controller.ui.spinbox_sniff_ErrorTolerance.valueChanged.connect(self.on_error_tolerance_changed)
        self.recv_settings_controller.ui.combox_sniff_Modulation.currentIndexChanged.connect(self.on_modulation_changed)

        self.send_settings_controller.ui.cbDevice.currentIndexChanged.connect(self.on_tx_device_changed)
        self.send_settings_controller.ui.lineEditDeviceArgs.textChanged.connect(self.on_tx_device_args_changed)
        self.send_settings_controller.ui.comboBoxChannel.currentIndexChanged.connect(self.on_tx_channel_changed)
        self.send_settings_controller.ui.comboBoxAntenna.currentIndexChanged.connect(self.on_tx_antenna_changed)
        self.send_settings_controller.ui.lineEditIP.textChanged.connect(self.on_tx_ip_changed)
        self.send_settings_controller.ui.spinBoxPort.valueChanged.connect(self.on_tx_port_changed)
        self.send_settings_controller.ui.spinBoxFreq.valueChanged.connect(self.on_tx_center_freq_changed)
        self.send_settings_controller.ui.spinBoxSampleRate.valueChanged.connect(self.on_tx_sample_rate_changed)
        self.send_settings_controller.ui.spinBoxBandwidth.valueChanged.connect(self.on_tx_bandwidth_changed)
        self.send_settings_controller.ui.spinBoxGain.valueChanged.connect(self.on_tx_rf_gain_changed)
        self.send_settings_controller.ui.spinBoxIFGain.valueChanged.connect(self.on_tx_if_gain_changed)
        self.send_settings_controller.ui.spinBoxBasebandGain.valueChanged.connect(self.on_tx_baseband_gain_changed)
        self.send_settings_controller.ui.spinBoxFreqCorrection.valueChanged.connect(self.on_tx_freq_correction_changed)
        self.send_settings_controller.ui.comboBoxDirectSampling.currentIndexChanged.connect(self.on_tx_direct_sampling_changed)
        self.send_settings_controller.ui.btnLockBWSR.clicked.connect(self.on_tx_btn_lock_bw_sr_clicked)

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

        prefix_ui_map = { RX_PREFIX: self.recv_settings_controller.ui,
                          TX_PREFIX: self.send_settings_controller.ui }

        for prefix, ui in prefix_ui_map.items():
            channel_index = ui.comboBoxChannel.currentIndex()
            antenna_index = ui.comboBoxAntenna.currentIndex()
            direct_sampling_index = ui.comboBoxDirectSampling.currentIndex()

            profile.update({
                prefix + 'device': ui.cbDevice.currentText(),
                prefix + 'device_args': ui.lineEditDeviceArgs.text(),
                prefix + 'channel': 0 if channel_index == -1 else channel_index,
                prefix + 'antenna': 0 if antenna_index == -1 else antenna_index,
                prefix + 'ip': ui.lineEditIP.text(),
                prefix + 'port': ui.spinBoxPort.value(),
                prefix + 'center_freq': ui.spinBoxFreq.value(),
                prefix + 'sample_rate': ui.spinBoxSampleRate.value(),
                prefix + 'bandwidth': ui.spinBoxBandwidth.value(),
                prefix + 'rf_gain': ui.spinBoxGain.value(),
                prefix + 'if_gain': ui.spinBoxIFGain.value(),
                prefix + 'baseband_gain': ui.spinBoxBasebandGain.value(),
                prefix + 'freq_correction': ui.spinBoxFreqCorrection.value(),
                prefix + 'direct_sampling': 0 if direct_sampling_index == -1 else direct_sampling_index,
                prefix + 'bw_sr_locked': ui.btnLockBWSR.isChecked()
            })

        profile.update({
            'noise': self.recv_settings_controller.ui.spinbox_sniff_Noise.value(),
            'center': self.recv_settings_controller.ui.spinbox_sniff_Center.value(),
            'bit_length': self.recv_settings_controller.ui.spinbox_sniff_BitLen.value(),
            'error_tolerance': self.recv_settings_controller.ui.spinbox_sniff_ErrorTolerance.value(),
            'modulation': self.recv_settings_controller.ui.combox_sniff_Modulation.currentIndex()
        })

        self.profiles.append(profile)
        self.ui.comboBoxProfiles.addItem(name)
        self.ui.comboBoxProfiles.setCurrentIndex(len(self.profiles) - 1)
        self.ui.btnRemoveProfile.setEnabled(True)

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
        controller_ui_map = { RX_PREFIX: self.recv_settings_controller,
                              TX_PREFIX: self.send_settings_controller }

        self.block_profile = True

        for prefix, controller in controller_ui_map.items():
            controller.ui.btnLockBWSR.setChecked(self.get_profile_value(prefix + "bw_sr_locked"))
            controller.on_btn_lock_bw_sr_clicked()
            controller.ui.cbDevice.setCurrentText(self.get_profile_value(prefix + "device"))
            controller.ui.lineEditDeviceArgs.setText(self.get_profile_value(prefix + "device_args"))
            controller.ui.comboBoxChannel.setCurrentIndex(self.get_profile_value(prefix + "channel"))
            controller.ui.comboBoxAntenna.setCurrentIndex(self.get_profile_value(prefix + "antenna"))
            controller.ui.lineEditIP.setText(self.get_profile_value(prefix + "ip"))
            controller.ui.spinBoxPort.setValue(self.get_profile_value(prefix + "port"))
            controller.ui.spinBoxFreq.setValue(self.get_profile_value(prefix + "center_freq"))
            controller.ui.spinBoxSampleRate.setValue(self.get_profile_value(prefix + "sample_rate"))
            controller.ui.spinBoxBandwidth.setValue(self.get_profile_value(prefix + "bandwidth"))
            controller.ui.spinBoxGain.setValue(self.get_profile_value(prefix + "rf_gain"))
            controller.ui.spinBoxIFGain.setValue(self.get_profile_value(prefix + "if_gain"))
            controller.ui.spinBoxBasebandGain.setValue(self.get_profile_value(prefix + "baseband_gain"))
            controller.ui.spinBoxFreqCorrection.setValue(self.get_profile_value(prefix + "freq_correction"))
            controller.ui.comboBoxDirectSampling.setCurrentIndex(self.get_profile_value(prefix + "direct_sampling"))

        self.recv_settings_controller.ui.spinbox_sniff_Noise.setValue(self.get_profile_value("noise"))
        self.recv_settings_controller.ui.spinbox_sniff_Center.setValue(self.get_profile_value("center"))
        self.recv_settings_controller.ui.spinbox_sniff_BitLen.setValue(self.get_profile_value("bit_length"))
        self.recv_settings_controller.ui.spinbox_sniff_ErrorTolerance.setValue(self.get_profile_value("error_tolerance"))
        self.recv_settings_controller.ui.combox_sniff_Modulation.setCurrentIndex(self.get_profile_value("modulation"))

        self.block_profile = False

    def on_rx_device_changed(self):
        self.set_profile_value(RX_PREFIX + "device", self.recv_settings_controller.ui.cbDevice.currentText())

    def on_rx_device_args_changed(self, text: str):
        self.set_profile_value(RX_PREFIX + "device_args", text)

    def on_rx_channel_changed(self, index: int):
        self.set_profile_value(RX_PREFIX + "channel", index)

    def on_rx_antenna_changed(self, index: int):
        self.set_profile_value(RX_PREFIX + "antenna", index)

    def on_rx_ip_changed(self, text: str):
        self.set_profile_value(RX_PREFIX + "ip", text)

    def on_rx_port_changed(self, value):
        self.set_profile_value(RX_PREFIX + "port", value)

    def on_rx_center_freq_changed(self, value):
        self.set_profile_value(RX_PREFIX + "center_freq", value)

    def on_rx_sample_rate_changed(self, value):
        self.set_profile_value(RX_PREFIX + "sample_rate", value)

    def on_rx_bandwidth_changed(self, value):
        self.set_profile_value(RX_PREFIX + "bandwidth", value)

    def on_rx_rf_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "rf_gain", value)

    def on_rx_if_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "if_gain", value)

    def on_rx_baseband_gain_changed(self, value):
        self.set_profile_value(RX_PREFIX + "baseband_gain", value)

    def on_rx_freq_correction_changed(self, value):
        self.set_profile_value(RX_PREFIX + "freq_correction", value)

    def on_rx_direct_sampling_changed(self, index: int):
        self.set_profile_value(RX_PREFIX + "direct_sampling", index)

    def on_rx_btn_lock_bw_sr_clicked(self, checked):
        self.set_profile_value(RX_PREFIX + "bw_sr_locked", checked)

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

    def on_tx_device_changed(self):
        self.set_profile_value(TX_PREFIX + "device", self.recv_settings_controller.ui.cbDevice.currentText())

    def on_tx_device_args_changed(self, text: str):
        self.set_profile_value(TX_PREFIX + "device_args", text)

    def on_tx_channel_changed(self, index: int):
        self.set_profile_value(TX_PREFIX + "channel", index)

    def on_tx_antenna_changed(self, index: int):
        self.set_profile_value(TX_PREFIX + "antenna", index)

    def on_tx_ip_changed(self, text: str):
        self.set_profile_value(TX_PREFIX + "ip", text)

    def on_tx_port_changed(self, value):
        self.set_profile_value(TX_PREFIX + "port", value)

    def on_tx_center_freq_changed(self, value):
        self.set_profile_value(TX_PREFIX + "center_freq", value)

    def on_tx_sample_rate_changed(self, value):
        self.set_profile_value(TX_PREFIX + "sample_rate", value)

    def on_tx_bandwidth_changed(self, value):
        self.set_profile_value(TX_PREFIX + "bandwidth", value)

    def on_tx_rf_gain_changed(self, value):
        self.set_profile_value(TX_PREFIX + "rf_gain", value)

    def on_tx_if_gain_changed(self, value):
        self.set_profile_value(TX_PREFIX + "if_gain", value)

    def on_tx_baseband_gain_changed(self, value):
        self.set_profile_value(TX_PREFIX + "baseband_gain", value)

    def on_tx_freq_correction_changed(self, value):
        self.set_profile_value(TX_PREFIX + "freq_correction", value)

    def on_tx_direct_sampling_changed(self, index: int):
        self.set_profile_value(TX_PREFIX + "direct_sampling", index)

    def on_tx_btn_lock_bw_sr_clicked(self, checked):
        self.set_profile_value(TX_PREFIX + "bw_sr_locked", checked)