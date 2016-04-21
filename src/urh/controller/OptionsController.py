import os

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QCompleter, QDirModel

from urh import constants
from urh.controller.PluginController import PluginController
from urh.dev.BackendHandler import BackendHandler
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

        self.show_gnuradio_infos()
        self.create_connects()
        self.old_symbol_tresh = 10
        self.old_show_pause_as_time = False

        self.read_options()

    def create_connects(self):
        self.ui.spinBoxSymbolTreshold.valueChanged.connect(self.handle_spinbox_symbol_treshold_value_changed)
        self.ui.chkBoxEnableSymbols.clicked.connect(self.on_chkbox_enable_symbols_clicked)
        self.ui.lineEditPython2Interpreter.editingFinished.connect(self.on_python2_exe_path_edited)


    def show_gnuradio_infos(self):
        self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)
        if self.backend_handler.gnuradio_installed:
            self.ui.lGnuradioInstalled.setStyleSheet("")
            self.ui.lGnuradioInstalled.setText(self.tr("Gnuradio installation found"))
        else:
            self.ui.lGnuradioInstalled.setStyleSheet("color: red")
            self.ui.lGnuradioInstalled.setText(self.tr("Gnuradio installation not found"))


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
        #self.ui.chkBoxUSRP.setChecked(settings.value('usrp_available', type=bool))
        #self.ui.chkBoxHackRF.setChecked(settings.value('hackrf_available', type=bool))

        self.ui.comboBoxDefaultView.setCurrentIndex(settings.value('default_view', type = int))
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
        exe = self.ui.lineEditPython2Interpreter.text()
        if os.path.isfile(exe) and os.access(exe, os.X_OK):
            self.backend_handler.python2_exe = exe
            constants.SETTINGS.setValue("python2_exe", exe)
            self.show_gnuradio_infos()
        else:
            self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)

    def on_chkbox_enable_symbols_clicked(self):
        if self.ui.chkBoxEnableSymbols.isChecked():
            self.ui.spinBoxSymbolTreshold.setValue(10)
        else:
            self.ui.spinBoxSymbolTreshold.setValue(50)


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