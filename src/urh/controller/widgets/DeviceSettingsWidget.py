from statistics import median

from PyQt5.QtCore import QRegExp, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtWidgets import QWidget, QSpinBox, QLabel, QComboBox, QSlider

from urh import constants
from urh.dev import config
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.VirtualDevice import VirtualDevice
from urh.plugins.NetworkSDRInterface.NetworkSDRInterfacePlugin import NetworkSDRInterfacePlugin
from urh.plugins.PluginManager import PluginManager
from urh.ui.ui_send_recv_device_settings import Ui_FormDeviceSettings
from urh.util.ProjectManager import ProjectManager


class DeviceSettingsWidget(QWidget):
    selected_device_changed = pyqtSignal()
    gain_edited = pyqtSignal()
    device_parameters_changed = pyqtSignal(dict)

    def __init__(self, project_manager: ProjectManager, is_tx: bool, backend_handler: BackendHandler = None,
                 continuous_send_mode=False, parent=None):
        super().__init__(parent)
        self.ui = Ui_FormDeviceSettings()
        self.ui.setupUi(self)

        self.__device = None  # type: VirtualDevice

        self.is_tx = is_tx
        self.is_rx = not is_tx
        if backend_handler is None:
            self.backend_handler = BackendHandler()
        else:
            self.backend_handler = backend_handler

        if self.is_rx:
            self.ui.spinBoxNRepeat.hide()
            self.ui.labelNRepeat.hide()
        else:
            self.ui.labelDCCorrection.hide()
            self.ui.checkBoxDCCorrection.hide()

        self.bw_sr_are_locked = constants.SETTINGS.value("lock_bandwidth_sample_rate", True, bool)
        self.ui.cbDevice.clear()
        items = self.get_devices_for_combobox(continuous_send_mode)
        self.ui.cbDevice.addItems(items)
        self.bootstrap(project_manager.device_conf, enforce_default=True)

        self.ui.btnLockBWSR.setChecked(self.bw_sr_are_locked)
        self.on_btn_lock_bw_sr_clicked()

        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QRegExp("^" + ip_range
                           + "\\." + ip_range
                           + "\\." + ip_range
                           + "\\." + ip_range + "$")
        self.ui.lineEditIP.setValidator(QRegExpValidator(ip_regex))

        self.create_connects()
        self.sync_gain_sliders()

    def bootstrap(self, conf_dict: dict, enforce_default=False):
        def set_val(ui_widget, key: str, default):
            try:
                value = conf_dict[key]
            except KeyError:
                value = default if enforce_default else None

            if value is not None:
                ui_widget.setValue(value)

        self.set_bandwidth_status()

        self.ui.cbDevice.setCurrentText(conf_dict.get("name", ""))
        dev_name = self.ui.cbDevice.currentText()
        self.set_device_ui_items_visibility(dev_name, overwrite_settings=True)

        set_val(self.ui.spinBoxFreq, "frequency", config.DEFAULT_FREQUENCY)
        set_val(self.ui.spinBoxSampleRate, "sample_rate", config.DEFAULT_SAMPLE_RATE)
        set_val(self.ui.spinBoxBandwidth, "bandwidth", config.DEFAULT_BANDWIDTH)
        set_val(self.ui.spinBoxGain, self.rx_tx_prefix + "gain", config.DEFAULT_GAIN)
        set_val(self.ui.spinBoxIFGain, self.rx_tx_prefix + "if_gain", config.DEFAULT_IF_GAIN)
        set_val(self.ui.spinBoxBasebandGain, self.rx_tx_prefix + "baseband_gain", config.DEFAULT_BB_GAIN)
        set_val(self.ui.spinBoxFreqCorrection, "freq_correction", config.DEFAULT_FREQ_CORRECTION)
        set_val(self.ui.spinBoxNRepeat, "num_sending_repeats",
                constants.SETTINGS.value('num_sending_repeats', 1, type=int))

        if self.rx_tx_prefix + "antenna_index" in conf_dict:
            self.ui.comboBoxAntenna.setCurrentIndex(conf_dict[self.rx_tx_prefix + "antenna_index"])

        if self.rx_tx_prefix + "gain" not in conf_dict:
            self.set_default_rf_gain()

        if self.rx_tx_prefix + "if_gain" not in conf_dict:
            self.set_default_if_gain()

        if self.rx_tx_prefix + "baseband_gain" not in conf_dict:
            self.set_default_bb_gain()

        if self.is_rx:
            self.ui.checkBoxDCCorrection.setChecked(conf_dict.get("apply_dc_correction", False))

        self.emit_editing_finished_signals()

    @property
    def device(self) -> VirtualDevice:
        return self.__device

    @device.setter
    def device(self, value: VirtualDevice):
        self.__device = value

    @property
    def rx_tx_prefix(self) -> str:
        return "rx_" if self.is_rx else "tx_"

    @property
    def selected_device_conf(self) -> dict:
        device_name = self.ui.cbDevice.currentText()
        key = device_name if device_name in config.DEVICE_CONFIG.keys() else "Fallback"
        return config.DEVICE_CONFIG[key]

    def create_connects(self):
        self.ui.spinBoxFreq.editingFinished.connect(self.on_spinbox_frequency_editing_finished)
        self.ui.spinBoxSampleRate.editingFinished.connect(self.on_spinbox_sample_rate_editing_finished)

        self.ui.spinBoxGain.editingFinished.connect(self.on_spinbox_gain_editing_finished)
        self.ui.spinBoxGain.valueChanged.connect(self.on_spinbox_gain_value_changed)
        self.ui.sliderGain.valueChanged.connect(self.on_slider_gain_value_changed)

        self.ui.spinBoxIFGain.editingFinished.connect(self.on_spinbox_if_gain_editing_finished)
        self.ui.spinBoxIFGain.valueChanged.connect(self.on_spinbox_if_gain_value_changed)
        self.ui.sliderIFGain.valueChanged.connect(self.on_slider_if_gain_value_changed)

        self.ui.spinBoxBasebandGain.editingFinished.connect(self.on_spinbox_baseband_gain_editing_finished)
        self.ui.spinBoxBasebandGain.valueChanged.connect(self.on_spinbox_baseband_gain_value_changed)
        self.ui.sliderBasebandGain.valueChanged.connect(self.on_slider_baseband_gain_value_changed)

        self.ui.spinBoxBandwidth.editingFinished.connect(self.on_spinbox_bandwidth_editing_finished)
        self.ui.spinBoxPort.editingFinished.connect(self.on_spinbox_port_editing_finished)
        self.ui.lineEditIP.editingFinished.connect(self.on_line_edit_ip_editing_finished)

        self.ui.comboBoxAntenna.currentIndexChanged.connect(self.on_combobox_antenna_current_index_changed)
        self.ui.comboBoxChannel.currentIndexChanged.connect(self.on_combobox_channel_current_index_changed)

        self.ui.spinBoxFreqCorrection.editingFinished.connect(self.on_spinbox_freq_correction_editing_finished)
        self.ui.comboBoxDirectSampling.currentIndexChanged.connect(self.on_combobox_direct_sampling_index_changed)

        self.ui.cbDevice.currentIndexChanged.connect(self.on_cb_device_current_index_changed)

        self.ui.spinBoxNRepeat.editingFinished.connect(self.on_num_repeats_changed)
        self.ui.btnLockBWSR.clicked.connect(self.on_btn_lock_bw_sr_clicked)

        self.ui.btnRefreshDeviceIdentifier.clicked.connect(self.on_btn_refresh_device_identifier_clicked)
        self.ui.comboBoxDeviceIdentifier.currentIndexChanged.connect(
            self.on_combo_box_device_identifier_current_index_changed)

        self.ui.checkBoxDCCorrection.clicked.connect(self.on_check_box_dc_correction_clicked)

    def set_gain_defaults(self):
        self.set_default_rf_gain()
        self.set_default_if_gain()
        self.set_default_bb_gain()

    def set_default_rf_gain(self):
        conf = self.selected_device_conf
        prefix = self.rx_tx_prefix
        if prefix + "rf_gain" in conf:
            key = prefix + "rf_gain"
            gain = conf[key][int(median(range(len(conf[key]))))]
            self.ui.spinBoxGain.setValue(gain)

    def set_default_if_gain(self):
        conf = self.selected_device_conf
        prefix = self.rx_tx_prefix
        if prefix + "if_gain" in conf:
            key = prefix + "if_gain"
            if_gain = conf[key][int(median(range(len(conf[key]))))]
            self.ui.spinBoxIFGain.setValue(if_gain)

    def set_default_bb_gain(self):
        conf = self.selected_device_conf
        prefix = self.rx_tx_prefix
        if prefix + "baseband_gain" in conf:
            key = prefix + "baseband_gain"
            baseband_gain = conf[key][int(median(range(len(conf[key]))))]
            self.ui.spinBoxBasebandGain.setValue(baseband_gain)

    def sync_gain_sliders(self):
        self.ui.spinBoxGain.valueChanged.emit(self.ui.spinBoxGain.value())
        self.ui.spinBoxIFGain.valueChanged.emit(self.ui.spinBoxIFGain.value())
        self.ui.spinBoxBasebandGain.valueChanged.emit(self.ui.spinBoxBasebandGain.value())

    def set_device_ui_items_visibility(self, device_name: str, overwrite_settings=True):
        key = device_name if device_name in config.DEVICE_CONFIG.keys() else "Fallback"
        conf = config.DEVICE_CONFIG[key]
        key_ui_dev_param_map = {"center_freq": "Freq", "sample_rate": "SampleRate", "bandwidth": "Bandwidth"}

        for key, ui_item in key_ui_dev_param_map.items():
            spinbox = getattr(self.ui, "spinBox" + ui_item)  # type: QSpinBox
            label = getattr(self.ui, "label" + ui_item)  # type: QLabel
            if key in conf:
                spinbox.setVisible(True)
                label.setVisible(True)

                if isinstance(conf[key], list):
                    spinbox.setMinimum(min(conf[key]))
                    spinbox.setMaximum(max(conf[key]))
                    spinbox.setSingleStep(conf[key][1] - conf[key][0])
                    spinbox.auto_update_step_size = False
                    if "default_" + key in conf:
                        spinbox.setValue(conf["default_" + key])
                else:
                    spinbox.setMinimum(conf[key].start)
                    spinbox.setMaximum(conf[key].stop)
                    spinbox.auto_update_step_size = True
                    spinbox.adjust_step()
            else:
                spinbox.setVisible(False)
                label.setVisible(False)

        self.ui.btnLockBWSR.setVisible("sample_rate" in conf and "bandwidth" in conf)

        if "freq_correction" in conf:
            self.ui.labelFreqCorrection.setVisible(True)
            self.ui.spinBoxFreqCorrection.setVisible(True)
            self.ui.spinBoxFreqCorrection.setMinimum(conf["freq_correction"].start)
            self.ui.spinBoxFreqCorrection.setMaximum(conf["freq_correction"].stop)
            self.ui.spinBoxFreqCorrection.setSingleStep(conf["freq_correction"].step)
        else:
            self.ui.labelFreqCorrection.setVisible(False)
            self.ui.spinBoxFreqCorrection.setVisible(False)

        if "direct_sampling" in conf:
            self.ui.labelDirectSampling.setVisible(True)
            self.ui.comboBoxDirectSampling.setVisible(True)
            items = [self.ui.comboBoxDirectSampling.itemText(i) for i in range(self.ui.comboBoxDirectSampling.count())]
            if items != conf["direct_sampling"]:
                self.ui.comboBoxDirectSampling.clear()
                self.ui.comboBoxDirectSampling.addItems(conf["direct_sampling"])
        else:
            self.ui.labelDirectSampling.setVisible(False)
            self.ui.comboBoxDirectSampling.setVisible(False)

        prefix = self.rx_tx_prefix
        key_ui_gain_map = {prefix + "rf_gain": "Gain", prefix + "if_gain": "IFGain",
                           prefix + "baseband_gain": "BasebandGain"}
        for conf_key, ui_element in key_ui_gain_map.items():
            getattr(self.ui, "label" + ui_element).setVisible(conf_key in conf)

            spinbox = getattr(self.ui, "spinBox" + ui_element)  # type: QSpinBox
            slider = getattr(self.ui, "slider" + ui_element)  # type: QSlider

            if conf_key in conf:
                gain_values = conf[conf_key]
                assert len(gain_values) >= 2
                spinbox.setMinimum(gain_values[0])
                spinbox.setMaximum(gain_values[-1])
                if overwrite_settings:
                    spinbox.setValue(gain_values[len(gain_values) // 2])
                spinbox.setSingleStep(gain_values[1] - gain_values[0])
                spinbox.setVisible(True)

                slider.setMaximum(len(gain_values) - 1)
            else:
                spinbox.setVisible(False)
                slider.setVisible(False)
            getattr(self.ui, "slider" + ui_element).setVisible(conf_key in conf)

        if overwrite_settings:
            key_ui_channel_ant_map = {prefix + "antenna": "Antenna", prefix + "channel": "Channel"}
            for conf_key, ui_element in key_ui_channel_ant_map.items():
                getattr(self.ui, "label" + ui_element).setVisible(conf_key in conf)
                combobox = getattr(self.ui, "comboBox" + ui_element)  # type: QComboBox
                if conf_key in conf:
                    combobox.clear()
                    combobox.addItems(conf[conf_key])
                    if conf_key + "_default_index" in conf:
                        combobox.setCurrentIndex(conf[conf_key + "_default_index"])

                    combobox.setVisible(True)
                else:
                    combobox.setVisible(False)

        multi_dev_support = hasattr(self.device, "has_multi_device_support") and self.device.has_multi_device_support
        self.ui.labelDeviceIdentifier.setVisible(multi_dev_support)
        self.ui.btnRefreshDeviceIdentifier.setVisible(multi_dev_support)
        self.ui.comboBoxDeviceIdentifier.setVisible(multi_dev_support)
        self.ui.lineEditIP.setVisible("ip" in conf)
        self.ui.labelIP.setVisible("ip" in conf)
        self.ui.spinBoxPort.setVisible("port" in conf)
        self.ui.labelPort.setVisible("port" in conf)
        show_dc_correction = self.is_rx and self.device is not None and self.device.apply_dc_correction is not None
        self.ui.checkBoxDCCorrection.setVisible(show_dc_correction)
        self.ui.labelDCCorrection.setVisible(show_dc_correction)

    def get_devices_for_combobox(self, continuous_send_mode):
        items = []
        for device_name in self.backend_handler.DEVICE_NAMES:
            dev = self.backend_handler.device_backends[device_name.lower()]
            if self.is_tx and dev.is_enabled and dev.supports_tx:
                if not continuous_send_mode:
                    items.append(device_name)
                elif dev.selected_backend != Backends.grc:
                    items.append(device_name)
            elif self.is_rx and dev.is_enabled and dev.supports_rx:
                items.append(device_name)

        if PluginManager().is_plugin_enabled("NetworkSDRInterface"):
            items.append(NetworkSDRInterfacePlugin.NETWORK_SDR_NAME)

        return items

    def set_bandwidth_status(self):
        if hasattr(self, "device") and self.device is not None and self.device.backend != Backends.none:
            self.ui.spinBoxBandwidth.setEnabled(self.device.bandwidth_is_adjustable)
            self.ui.btnLockBWSR.setEnabled(self.device.bandwidth_is_adjustable)

            if not self.device.bandwidth_is_adjustable:
                self.bw_sr_are_locked = False
                self.ui.spinBoxBandwidth.setToolTip(self.tr("Your driver of RTL-SDR does not support "
                                                            "setting the bandwidth. "
                                                            "If you need this feature, install a recent version."))
            else:
                self.ui.spinBoxBandwidth.setToolTip("")
                self.bw_sr_are_locked = self.ui.btnLockBWSR.isChecked()

    def emit_editing_finished_signals(self):
        self.ui.spinBoxFreq.editingFinished.emit()
        self.ui.spinBoxBandwidth.editingFinished.emit()
        self.ui.spinBoxGain.editingFinished.emit()
        self.ui.spinBoxIFGain.editingFinished.emit()
        self.ui.spinBoxBasebandGain.editingFinished.emit()
        self.ui.spinBoxNRepeat.editingFinished.emit()
        self.ui.spinBoxSampleRate.editingFinished.emit()
        self.ui.spinBoxFreqCorrection.editingFinished.emit()
        self.ui.lineEditIP.editingFinished.emit()
        self.ui.spinBoxPort.editingFinished.emit()
        self.ui.comboBoxAntenna.currentIndexChanged.emit(self.ui.comboBoxAntenna.currentIndex())
        self.ui.comboBoxChannel.currentIndexChanged.emit(self.ui.comboBoxChannel.currentIndex())
        self.ui.checkBoxDCCorrection.clicked.emit(self.ui.checkBoxDCCorrection.isChecked())

    def emit_device_parameters_changed(self):
        settings = {"name": str(self.device.name)}
        for attrib in ("frequency", "sample_rate", "bandwidth", "gain", "if_gain", "baseband_gain", "freq_correction",
                       "antenna_index", "num_sending_repeats", "apply_dc_correction"):
            try:
                value = getattr(self.device, attrib, None)
                if value is not None:
                    if "gain" in attrib or attrib == "antenna_index":
                        attrib = self.rx_tx_prefix + attrib
                    settings[attrib] = value
            except (ValueError, AttributeError):
                continue

        self.device_parameters_changed.emit(settings)

    @pyqtSlot()
    def on_btn_lock_bw_sr_clicked(self):
        self.bw_sr_are_locked = self.ui.btnLockBWSR.isChecked()
        constants.SETTINGS.setValue("lock_bandwidth_sample_rate", self.bw_sr_are_locked)
        if self.bw_sr_are_locked:
            self.ui.btnLockBWSR.setIcon(QIcon(":/icons/icons/lock.svg"))
            self.ui.spinBoxBandwidth.setValue(self.ui.spinBoxSampleRate.value())
            self.ui.spinBoxBandwidth.editingFinished.emit()
        else:
            self.ui.btnLockBWSR.setIcon(QIcon(":/icons/icons/unlock.svg"))

    @pyqtSlot()
    def on_spinbox_sample_rate_editing_finished(self):
        self.device.sample_rate = self.ui.spinBoxSampleRate.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxBandwidth.setValue(self.ui.spinBoxSampleRate.value())
            self.device.bandwidth = self.ui.spinBoxBandwidth.value()

    @pyqtSlot()
    def on_spinbox_frequency_editing_finished(self):
        self.device.frequency = self.ui.spinBoxFreq.value()

    @pyqtSlot()
    def on_spinbox_bandwidth_editing_finished(self):
        self.device.bandwidth = self.ui.spinBoxBandwidth.value()
        if self.bw_sr_are_locked:
            self.ui.spinBoxSampleRate.setValue(self.ui.spinBoxBandwidth.value())
            self.device.sample_rate = self.ui.spinBoxSampleRate.value()

    @pyqtSlot()
    def on_line_edit_ip_editing_finished(self):
        self.device.ip = self.ui.lineEditIP.text()

    @pyqtSlot()
    def on_spinbox_port_editing_finished(self):
        self.device.port = self.ui.spinBoxPort.value()

    @pyqtSlot(int)
    def on_combobox_antenna_current_index_changed(self, index: int):
        self.device.antenna_index = index

    @pyqtSlot(int)
    def on_combobox_channel_current_index_changed(self, index: int):
        self.device.channel_index = index

    @pyqtSlot()
    def on_spinbox_freq_correction_editing_finished(self):
        self.device.freq_correction = self.ui.spinBoxFreqCorrection.value()

    @pyqtSlot(int)
    def on_combobox_direct_sampling_index_changed(self, index: int):
        self.device.direct_sampling_mode = index

    @pyqtSlot()
    def on_spinbox_gain_editing_finished(self):
        self.device.gain = self.ui.spinBoxGain.value()

    @pyqtSlot(int)
    def on_spinbox_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        try:
            self.ui.sliderGain.setValue(dev_conf[self.rx_tx_prefix + "rf_gain"].index(value))
        except (ValueError, KeyError):
            pass

    @pyqtSlot(int)
    def on_slider_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        self.ui.spinBoxGain.setValue(dev_conf[self.rx_tx_prefix + "rf_gain"][value])

    @pyqtSlot()
    def on_spinbox_if_gain_editing_finished(self):
        self.device.if_gain = self.ui.spinBoxIFGain.value()

    @pyqtSlot(int)
    def on_slider_if_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        self.ui.spinBoxIFGain.setValue(dev_conf[self.rx_tx_prefix + "if_gain"][value])

    @pyqtSlot(int)
    def on_spinbox_if_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        try:
            self.ui.sliderIFGain.setValue(dev_conf[self.rx_tx_prefix + "if_gain"].index(value))
        except (ValueError, KeyError):
            pass

    @pyqtSlot()
    def on_num_repeats_changed(self):
        self.device.num_sending_repeats = self.ui.spinBoxNRepeat.value()

    @pyqtSlot()
    def on_spinbox_baseband_gain_editing_finished(self):
        self.device.baseband_gain = self.ui.spinBoxBasebandGain.value()

    @pyqtSlot(int)
    def on_slider_baseband_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        self.ui.spinBoxBasebandGain.setValue(dev_conf[self.rx_tx_prefix + "baseband_gain"][value])

    @pyqtSlot(int)
    def on_spinbox_baseband_gain_value_changed(self, value: int):
        dev_conf = self.selected_device_conf
        try:
            self.ui.sliderBasebandGain.setValue(dev_conf[self.rx_tx_prefix + "baseband_gain"].index(value))
        except (ValueError, KeyError):
            pass

    def update_for_new_device(self, overwrite_settings=True):
        if self.device is not None:
            self.device.free_data()

        # Here init_device of dialogs gets called
        self.selected_device_changed.emit()

        dev_name = self.ui.cbDevice.currentText()
        self.set_device_ui_items_visibility(dev_name, overwrite_settings=overwrite_settings)

        if overwrite_settings:
            self.set_gain_defaults()

        self.sync_gain_sliders()
        self.set_bandwidth_status()

        self.ui.comboBoxDeviceIdentifier.clear()

    @pyqtSlot()
    def on_cb_device_current_index_changed(self):
        self.update_for_new_device(overwrite_settings=True)

    @pyqtSlot()
    def on_btn_refresh_device_identifier_clicked(self):
        if self.device is None:
            return
        self.ui.comboBoxDeviceIdentifier.clear()
        self.ui.comboBoxDeviceIdentifier.addItems(self.device.get_device_list())

    @pyqtSlot(bool)
    def on_check_box_dc_correction_clicked(self, checked: bool):
        self.device.apply_dc_correction = bool(checked)

    @pyqtSlot()
    def on_combo_box_device_identifier_current_index_changed(self):
        if self.device is not None:
            self.device.device_serial = self.ui.comboBoxDeviceIdentifier.currentText()
            self.device.device_number = self.ui.comboBoxDeviceIdentifier.currentIndex()


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    from urh.controller.MainController import MainController

    app = QApplication([])
    mc = MainController()
    widget = DeviceSettingsWidget(mc.project_manager, is_tx=False)

    widget.show()
    app.exec_()
