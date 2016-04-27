import os

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QCompleter, QDirModel
from subprocess import call, DEVNULL

from urh import constants
from urh.controller.PluginController import PluginController
from urh.dev.BackendHandler import BackendHandler, Backends, BackendContainer
from urh.ui.ui_options import Ui_DialogOptions


class OptionsController(QDialog):
    values_changed = pyqtSignal(dict)

    def __init__(self, installed_plugins, highlighted_plugins=None, parent=None):
        super().__init__(parent)

        self.backend_handler = BackendHandler()

        self.ui = Ui_DialogOptions()
        self.ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QHBoxLayout(self.ui.tab_plugins)
        self.plugin_controller = PluginController(installed_plugins, highlighted_plugins, parent=self)
        layout.addWidget(self.plugin_controller)
        self.ui.tab_plugins.setLayout(layout)

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEditPython2Interpreter.setCompleter(completer)

        for devname in self.backend_handler.DEVICE_NAMES:
            self.ui.listWidgetDevices.addItem(devname)

        self.set_device_enabled_suffix()

        self.ui.listWidgetDevices.setCurrentRow(0)
        self.refresh_device_tab()

        self.create_connects()
        self.old_symbol_tresh = 10
        self.old_show_pause_as_time = False

        self.read_options()

    @property
    def selected_device(self) -> BackendContainer:
        try:
            devname = self.ui.listWidgetDevices.currentItem().text().lower()
            dev_key = self.__get_key_from_device_display_text(devname)

            return self.backend_handler.device_backends[dev_key]
        except:
            return ""

    def __get_key_from_device_display_text(self, displayed_device_name):
            displayed_device_name = displayed_device_name.lower()
            for key in self.backend_handler.DEVICE_NAMES:
                key = key.lower()
                if displayed_device_name.startswith(key):
                    return key
            return None

    def create_connects(self):
        self.ui.spinBoxSymbolTreshold.valueChanged.connect(self.handle_spinbox_symbol_treshold_value_changed)
        self.ui.chkBoxEnableSymbols.clicked.connect(self.on_chkbox_enable_symbols_clicked)
        self.ui.lineEditPython2Interpreter.editingFinished.connect(self.on_python2_exe_path_edited)
        self.ui.listWidgetDevices.currentRowChanged.connect(self.show_selected_device_params)
        self.ui.chkBoxDeviceEnabled.clicked.connect(self.on_chk_box_device_enabled_clicked)
        self.ui.rbGnuradioBackend.clicked.connect(self.on_rb_gnuradio_backend_clicked)
        self.ui.rbNativeBackend.clicked.connect(self.on_rb_native_backend_clicked)

    def set_device_enabled_suffix(self):
        for i in range(self.ui.listWidgetDevices.count()):
            w = self.ui.listWidgetDevices.item(i)
            dev_key = self.__get_key_from_device_display_text(w.text())
            is_enabled = self.backend_handler.device_backends[dev_key].is_enabled
            suffix = self.tr("enabled") if is_enabled else self.tr("disabled")
            dev_name = next(dn for dn in BackendHandler.DEVICE_NAMES if dn.lower() == dev_key)
            w.setText("{0} - {1}".format(dev_name, suffix))


    def show_gnuradio_infos(self):
        self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)
        if self.backend_handler.gnuradio_installed:
            self.ui.lGnuradioInstalled.setStyleSheet("")
            self.ui.lGnuradioInstalled.setText(self.tr("Gnuradio interface is working."))
        else:
            self.ui.lGnuradioInstalled.setStyleSheet("color: red")
            self.ui.lGnuradioInstalled.setText(
                self.tr("Gnuradio is not installed or incompatible with python2 interpreter."))

    def show_selected_device_params(self):
        if self.ui.listWidgetDevices.currentRow() >= 0:
            dev = self.selected_device

            self.ui.chkBoxDeviceEnabled.setEnabled(len(dev.avail_backends) > 0)
            self.ui.rbGnuradioBackend.setEnabled(dev.has_gnuradio_backend)
            self.ui.rbNativeBackend.setEnabled(dev.has_native_backend)

            self.ui.chkBoxDeviceEnabled.setChecked(dev.is_enabled)
            self.ui.rbGnuradioBackend.setChecked(dev.selected_backend == Backends.grc)
            self.ui.rbNativeBackend.setChecked(dev.selected_backend == Backends.native)

    def closeEvent(self, event: QCloseEvent):
        changed_values = {}
        if self.ui.spinBoxSymbolTreshold.value() != self.old_symbol_tresh:
            changed_values["rel_symbol_length"] = 100 - 2 * self.ui.spinBoxSymbolTreshold.value()
        if bool(self.ui.checkBoxPauseTime.isChecked()) != self.old_show_pause_as_time:
            changed_values['show_pause_as_time'] = bool(self.ui.checkBoxPauseTime.isChecked())

        settings = constants.SETTINGS
        settings.setValue('default_view', self.ui.comboBoxDefaultView.currentIndex())
        settings.setValue('num_sending_repeats', self.ui.spinBoxNumSendingRepeats.value())
        settings.setValue('show_pause_as_time', self.ui.checkBoxPauseTime.isChecked())

        self.values_changed.emit(changed_values)

        self.plugin_controller.save_enabled_states()
        event.accept()

    def read_options(self):
        settings = constants.SETTINGS
        # self.ui.chkBoxUSRP.setChecked(settings.value('usrp_available', type=bool))
        # self.ui.chkBoxHackRF.setChecked(settings.value('hackrf_available', type=bool))

        self.ui.comboBoxDefaultView.setCurrentIndex(settings.value('default_view', type=int))
        self.ui.spinBoxNumSendingRepeats.setValue(settings.value('num_sending_repeats', type=int))
        self.ui.checkBoxPauseTime.setChecked(settings.value('show_pause_as_time', type=bool))

        symbol_thresh = (settings.value('rel_symbol_length', type=int) - 100) / (-2)
        self.ui.spinBoxSymbolTreshold.setValue(symbol_thresh)
        self.old_symbol_tresh = symbol_thresh
        self.old_show_pause_as_time = bool(self.ui.checkBoxPauseTime.isChecked())

    @pyqtSlot()
    def handle_spinbox_symbol_treshold_value_changed(self):
        val = self.ui.spinBoxSymbolTreshold.value()
        self.ui.lSymbolLength.setText(str(100 - 2 * val) + "%")
        if val == 50:
            txt = self.tr("No symbols will be created")
            self.ui.chkBoxEnableSymbols.setChecked(False)
        elif val == 0:
            txt = self.tr("A symbol will be created in any case")
            self.ui.chkBoxEnableSymbols.setChecked(True)
        else:
            self.ui.chkBoxEnableSymbols.setChecked(True)
            bit_len = 1000
            rel_val = val / 100
            rel_symbol_len = (100 - 2 * val) / 100
            txt = self.tr(
                "Custom symbols will be created outside {0:d}%-{1:d}% of selected bit length.\n\n"
                "Example - With bit length {2:d} following will hold: \n"
                "{3:d} - {4:d}: \tSymbol A\n"
                "{5:d} - {6:d}: \tStandard symbol (0 or 1)\n"
                "{7:d} - {8:d}: \tSymbol B\n"
                "{9:d} - {10:d}: \tStandard symbol (0 or 1)\n\nNote there will be different symbols for various signal levels (e.g. low and high).".format(
                    100 - val, 100 + val, bit_len,
                    int((1 - rel_val) * bit_len - rel_symbol_len * bit_len), int((1 - rel_val) * bit_len),
                    int((1 - rel_val) * bit_len), int((1 + rel_val) * bit_len),
                    int((1 + rel_val) * bit_len), int((1 + rel_val) * bit_len + rel_symbol_len * bit_len),
                    int((2 - rel_val) * bit_len), int((2 + rel_val) * bit_len)))
        self.ui.lExplanation.setText(txt)

    @pyqtSlot()
    def on_python2_exe_path_edited(self):
        python2_exe = self.ui.lineEditPython2Interpreter.text()
        if os.path.isfile(python2_exe) and os.access(python2_exe, os.X_OK):
            self.backend_handler.python2_exe = python2_exe
            self.backend_handler.gnuradio_installed = call([python2_exe, "-c", "import gnuradio"], stderr=DEVNULL) == 0
            constants.SETTINGS.setValue("python2_exe", python2_exe)
            self.refresh_device_tab()
        else:
            self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)

    @pyqtSlot()
    def on_chk_box_device_enabled_clicked(self):
        self.selected_device.is_enabled = bool(self.ui.chkBoxDeviceEnabled.isChecked())
        self.selected_device.write_settings()
        self.set_device_enabled_suffix()

    @pyqtSlot()
    def on_rb_gnuradio_backend_clicked(self):
        if Backends.grc in self.selected_device.avail_backends:
            self.selected_device.selected_backend = Backends.grc
            self.selected_device.write_settings()

    @pyqtSlot()
    def on_rb_native_backend_clicked(self):
        if Backends.native in self.selected_device.avail_backends:
            self.selected_device.selected_backend = Backends.native
            self.selected_device.write_settings()

    def on_chkbox_enable_symbols_clicked(self):
        if self.ui.chkBoxEnableSymbols.isChecked():
            self.ui.spinBoxSymbolTreshold.setValue(10)
        else:
            self.ui.spinBoxSymbolTreshold.setValue(50)

    def refresh_device_tab(self):
        self.backend_handler.get_backends()
        self.show_gnuradio_infos()
        self.show_selected_device_params()
        self.set_device_enabled_suffix()

    @staticmethod
    def write_default_options():
        settings = constants.SETTINGS
        keys = settings.allKeys()
        if not 'rel_symbol_length' in keys:
            settings.setValue('rel_symbol_length', 10)

        if not 'default_view' in keys:
            settings.setValue('default_view', 0)

        if not 'num_sending_repeats' in keys:
            settings.setValue('num_sending_repeats', 0)

        if not 'show_pause_as_time' in keys:
            settings.setValue('show_pause_as_time', False)

        bh = BackendHandler()
        for be in bh.device_backends.values():
            be.write_settings()
