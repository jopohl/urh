import os
import pickle
import platform
import sys
import tempfile
from subprocess import call

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QCompleter, QDirModel, QApplication, QHeaderView, QStyleFactory

from urh import constants
from urh.controller.PluginController import PluginController
from urh.dev.BackendHandler import BackendHandler, Backends, BackendContainer
from urh.dev.native import ExtensionHelper
from urh.models.FieldTypeTableModel import FieldTypeTableModel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
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

        # We use bundled native device backends on windows, so no need to reconfigure them
        self.ui.groupBoxNativeOptions.setVisible(sys.platform != "win32")
        self.ui.labelWindowsError.setVisible(sys.platform == "win32" and platform.architecture()[0] != "64bit")

        self.ui.comboBoxTheme.setCurrentIndex(constants.SETTINGS.value("theme_index", 0, int))
        self.ui.checkBoxShowConfirmCloseDialog.setChecked(
            not constants.SETTINGS.value('not_show_close_dialog', False, bool))
        self.ui.checkBoxHoldShiftToDrag.setChecked(constants.SETTINGS.value('hold_shift_to_drag', False, bool))
        self.ui.checkBoxDefaultFuzzingPause.setChecked(
            constants.SETTINGS.value('use_default_fuzzing_pause', True, bool))

        self.ui.doubleSpinBoxRAMThreshold.setValue(100 * constants.SETTINGS.value('ram_threshold', 0.6, float))

        self.ui.radioButtonGnuradioDirectory.setChecked(self.backend_handler.use_gnuradio_install_dir)
        self.ui.radioButtonPython2Interpreter.setChecked(not self.backend_handler.use_gnuradio_install_dir)
        if self.backend_handler.gnuradio_install_dir:
            self.ui.lineEditGnuradioDirectory.setText(self.backend_handler.gnuradio_install_dir)
        if self.backend_handler.python2_exe:
            self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)

        self.ui.doubleSpinBoxFuzzingPause.setValue(constants.SETTINGS.value("default_fuzzing_pause", 10 ** 6, int))
        self.ui.doubleSpinBoxFuzzingPause.setEnabled(constants.SETTINGS.value('use_default_fuzzing_pause', True, bool))

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEditPython2Interpreter.setCompleter(completer)
        self.ui.lineEditGnuradioDirectory.setCompleter(completer)

        for dev_name in self.backend_handler.DEVICE_NAMES:
            self.ui.listWidgetDevices.addItem(dev_name)

        self.set_device_enabled_suffix()

        self.ui.listWidgetDevices.setCurrentRow(0)
        self.set_gnuradio_status()
        self.refresh_device_tab()

        self.create_connects()
        self.old_show_pause_as_time = False

        self.field_type_table_model = FieldTypeTableModel([], parent=self)
        self.ui.tblLabeltypes.setModel(self.field_type_table_model)
        self.ui.tblLabeltypes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.tblLabeltypes.setItemDelegateForColumn(1, ComboBoxDelegate([f.name for f in FieldType.Function],
                                                                           return_index=False, parent=self))
        self.ui.tblLabeltypes.setItemDelegateForColumn(2, ComboBoxDelegate(ProtocolLabel.DISPLAY_FORMATS, parent=self))

        self.read_options()

        self.old_default_view = self.ui.comboBoxDefaultView.currentIndex()
        self.ui.labelRebuildNativeStatus.setText("")

        try:
            self.restoreGeometry(constants.SETTINGS.value("{}/geometry".format(self.__class__.__name__)))
        except TypeError:
            pass

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
        self.ui.doubleSpinBoxFuzzingPause.valueChanged.connect(self.on_spinbox_fuzzing_pause_value_changed)
        self.ui.lineEditPython2Interpreter.editingFinished.connect(self.on_python2_exe_path_edited)
        self.ui.lineEditGnuradioDirectory.editingFinished.connect(self.on_gnuradio_install_dir_edited)
        self.ui.listWidgetDevices.currentRowChanged.connect(self.on_list_widget_devices_current_row_changed)
        self.ui.chkBoxDeviceEnabled.clicked.connect(self.on_chk_box_device_enabled_clicked)
        self.ui.rbGnuradioBackend.clicked.connect(self.on_rb_gnuradio_backend_clicked)
        self.ui.rbNativeBackend.clicked.connect(self.on_rb_native_backend_clicked)
        self.ui.comboBoxTheme.currentIndexChanged.connect(self.on_combo_box_theme_index_changed)
        self.ui.checkBoxShowConfirmCloseDialog.clicked.connect(self.on_checkbox_confirm_close_dialog_clicked)
        self.ui.checkBoxHoldShiftToDrag.clicked.connect(self.on_checkbox_hold_shift_to_drag_clicked)
        self.ui.checkBoxAlignLabels.clicked.connect(self.on_checkbox_align_labels_clicked)
        self.ui.checkBoxDefaultFuzzingPause.clicked.connect(self.on_checkbox_default_fuzzing_pause_clicked)
        self.ui.btnAddLabelType.clicked.connect(self.on_btn_add_label_type_clicked)
        self.ui.btnRemoveLabeltype.clicked.connect(self.on_btn_remove_label_type_clicked)
        self.ui.radioButtonPython2Interpreter.clicked.connect(self.on_radio_button_python2_interpreter_clicked)
        self.ui.radioButtonGnuradioDirectory.clicked.connect(self.on_radio_button_gnuradio_directory_clicked)
        self.ui.doubleSpinBoxRAMThreshold.valueChanged.connect(self.on_double_spinbox_ram_threshold_value_changed)
        self.ui.btnRebuildNative.clicked.connect(self.on_btn_rebuild_native_clicked)

    def show_gnuradio_infos(self):
        self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)
        self.ui.lineEditGnuradioDirectory.setText(self.backend_handler.gnuradio_install_dir)

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

            if dev.supports_tx and dev.supports_rx:
                self.ui.lSupport.setText(self.tr("device supports sending and receiving"))
                self.ui.lSupport.setStyleSheet("color: green")
            elif dev.supports_rx and not dev.supports_tx:
                self.ui.lSupport.setText(self.tr("device supports receiving only"))
                self.ui.lSupport.setStyleSheet("color: blue")
            elif not dev.supports_rx and dev.supports_tx:
                self.ui.lSupport.setText(self.tr("device supports sending only"))
                self.ui.lSupport.setStyleSheet("color: blue")
            else:
                self.ui.lSupport.setText(self.tr("device supports neither sending nor receiving"))
                self.ui.lSupport.setStyleSheet("color: red")

    def set_device_enabled_suffix(self):
        for i in range(self.ui.listWidgetDevices.count()):
            w = self.ui.listWidgetDevices.item(i)
            dev_key = self.__get_key_from_device_display_text(w.text())
            is_enabled = self.backend_handler.device_backends[dev_key].is_enabled
            suffix = self.tr("enabled") if is_enabled else self.tr("disabled")
            dev_name = next(dn for dn in BackendHandler.DEVICE_NAMES if dn.lower() == dev_key)
            w.setText("{0} - {1}".format(dev_name, suffix))

    def read_options(self):
        settings = constants.SETTINGS

        self.ui.comboBoxDefaultView.setCurrentIndex(settings.value('default_view', type=int))
        self.ui.spinBoxNumSendingRepeats.setValue(settings.value('num_sending_repeats', type=int))
        self.ui.checkBoxPauseTime.setChecked(settings.value('show_pause_as_time', type=bool))

        self.old_show_pause_as_time = bool(self.ui.checkBoxPauseTime.isChecked())

        self.field_type_table_model.field_types = FieldType.load_from_xml()
        self.field_type_table_model.update()

    def refresh_device_tab(self):
        self.backend_handler.get_backends()
        self.show_gnuradio_infos()
        self.show_selected_device_params()
        self.set_device_enabled_suffix()

        self.ui.lineEditGnuradioDirectory.setEnabled(self.backend_handler.use_gnuradio_install_dir)
        self.ui.lineEditPython2Interpreter.setDisabled(self.backend_handler.use_gnuradio_install_dir)

    def closeEvent(self, event: QCloseEvent):
        changed_values = {}
        if bool(self.ui.checkBoxPauseTime.isChecked()) != self.old_show_pause_as_time:
            changed_values['show_pause_as_time'] = bool(self.ui.checkBoxPauseTime.isChecked())
        if self.old_default_view != self.ui.comboBoxDefaultView.currentIndex():
            changed_values['default_view'] = self.ui.comboBoxDefaultView.currentIndex()

        settings = constants.SETTINGS
        settings.setValue('default_view', self.ui.comboBoxDefaultView.currentIndex())
        settings.setValue('num_sending_repeats', self.ui.spinBoxNumSendingRepeats.value())
        settings.setValue('show_pause_as_time', self.ui.checkBoxPauseTime.isChecked())

        FieldType.save_to_xml(self.field_type_table_model.field_types)
        self.plugin_controller.save_enabled_states()
        for plugin in self.plugin_controller.model.plugins:
            plugin.destroy_settings_frame()

        self.values_changed.emit(changed_values)

        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    def set_gnuradio_status(self):
        self.backend_handler.python2_exe = self.ui.lineEditPython2Interpreter.text()
        self.backend_handler.gnuradio_install_dir = self.ui.lineEditGnuradioDirectory.text()
        self.backend_handler.use_gnuradio_install_dir = self.ui.radioButtonGnuradioDirectory.isChecked()
        self.backend_handler.set_gnuradio_installed_status()
        constants.SETTINGS.setValue("use_gnuradio_install_dir", self.backend_handler.use_gnuradio_install_dir)
        self.refresh_device_tab()

    @pyqtSlot()
    def on_btn_add_label_type_clicked(self):
        suffix = 1
        field_type_names = {ft.caption for ft in self.field_type_table_model.field_types}
        while "New Fieldtype #" + str(suffix) in field_type_names:
            suffix += 1

        caption = "New Fieldtype #" + str(suffix)
        self.field_type_table_model.field_types.append(FieldType(caption, FieldType.Function.CUSTOM))
        self.field_type_table_model.update()

    @pyqtSlot()
    def on_btn_remove_label_type_clicked(self):
        if self.field_type_table_model.field_types:
            selected_indices = {i.row() for i in self.ui.tblLabeltypes.selectedIndexes()}

            if selected_indices:
                for i in reversed(sorted(selected_indices)):
                    self.field_type_table_model.field_types.pop(i)
            else:
                self.field_type_table_model.field_types.pop()

            self.field_type_table_model.update()

    @pyqtSlot()
    def on_double_spinbox_ram_threshold_value_changed(self):
        val = self.ui.doubleSpinBoxRAMThreshold.value()
        constants.SETTINGS.setValue("ram_threshold", val / 100)

    @pyqtSlot(bool)
    def on_checkbox_confirm_close_dialog_clicked(self, checked: bool):
        constants.SETTINGS.setValue("not_show_close_dialog", not checked)

    @pyqtSlot(int)
    def on_combo_box_theme_index_changed(self, index: int):
        constants.SETTINGS.setValue('theme_index', index)
        if index > 0:
            QApplication.instance().setStyle(QStyleFactory.create("Fusion"))
        else:
            QApplication.instance().setStyle(constants.SETTINGS.value("default_theme", type=str))

    @pyqtSlot(bool)
    def on_checkbox_hold_shift_to_drag_clicked(self, checked: bool):
        constants.SETTINGS.setValue("hold_shift_to_drag", checked)

    @pyqtSlot(bool)
    def on_checkbox_default_fuzzing_pause_clicked(self, checked: bool):
        constants.SETTINGS.setValue('use_default_fuzzing_pause', checked)
        self.ui.doubleSpinBoxFuzzingPause.setEnabled(checked)

    @pyqtSlot(float)
    def on_spinbox_fuzzing_pause_value_changed(self, value: float):
        constants.SETTINGS.setValue("default_fuzzing_pause", int(value))

    @pyqtSlot()
    def on_python2_exe_path_edited(self):
        self.set_gnuradio_status()

    @pyqtSlot()
    def on_chk_box_device_enabled_clicked(self):
        self.selected_device.is_enabled = bool(self.ui.chkBoxDeviceEnabled.isChecked())
        self.selected_device.write_settings()
        self.set_device_enabled_suffix()

    @pyqtSlot()
    def on_rb_gnuradio_backend_clicked(self):
        if Backends.grc in self.selected_device.avail_backends:
            self.ui.rbGnuradioBackend.setChecked(True)
            self.selected_device.selected_backend = Backends.grc
            self.selected_device.write_settings()

    @pyqtSlot()
    def on_rb_native_backend_clicked(self):
        if Backends.native in self.selected_device.avail_backends:
            self.ui.rbNativeBackend.setChecked(True)
            self.selected_device.selected_backend = Backends.native
            self.selected_device.write_settings()

    @pyqtSlot(bool)
    def on_checkbox_align_labels_clicked(self, checked: bool):
        constants.SETTINGS.setValue("align_labels", checked)

    @pyqtSlot(int)
    def on_list_widget_devices_current_row_changed(self, current_row: int):
        self.show_selected_device_params()

    @pyqtSlot(bool)
    def on_radio_button_gnuradio_directory_clicked(self, checked: bool):
        self.set_gnuradio_status()

    @pyqtSlot(bool)
    def on_radio_button_python2_interpreter_clicked(self, checked: bool):
        self.set_gnuradio_status()

    @pyqtSlot()
    def on_gnuradio_install_dir_edited(self):
        self.set_gnuradio_status()

    @pyqtSlot()
    def on_btn_rebuild_native_clicked(self):
        library_dirs = None if not self.ui.lineEditLibDirs.text() \
                            else list(map(str.strip, self.ui.lineEditLibDirs.text().split(",")))
        num_natives = self.backend_handler.num_native_backends
        extensions = ExtensionHelper.get_device_extensions(use_cython=False, library_dirs=library_dirs)
        new_natives = len(extensions) - num_natives

        if new_natives == 0:
            self.ui.labelRebuildNativeStatus.setText(self.tr("No new native backends were found."))
            return
        else:
            s = "s" if new_natives > 1 else ""
            self.ui.labelRebuildNativeStatus.setText(self.tr("Rebuilding device extensions..."))
            pickle.dump(extensions, open(os.path.join(tempfile.gettempdir(), "native_extensions"), "wb"))
            target_dir = os.path.realpath(os.path.join(__file__, "../../../"))
            build_cmd = [sys.executable, os.path.realpath(ExtensionHelper.__file__),
                         "build_ext", "-b", target_dir,
                         "-t", tempfile.gettempdir()]
            if library_dirs:
                build_cmd.extend(["-L", ":".join(library_dirs)])
            rc = call(build_cmd)

            if rc == 0:
                self.ui.labelRebuildNativeStatus.setText(self.tr("<font color=green>"
                                                                 "Rebuilt {0} new device extension{1}. "
                                                                 "</font>"
                                                                 "Please restart URH.".format(new_natives, s)))
            else:
                self.ui.labelRebuildNativeStatus.setText(self.tr("<font color='red'>"
                                                                 "Failed to rebuild {0} device extension{1}. "
                                                                 "</font>"
                                                                 "Run URH as root (<b>sudo urh</b>) "
                                                                 "and try again.".format(new_natives, s)))
            try:
                os.remove(os.path.join(tempfile.gettempdir(), "native_extensions"))
            except OSError:
                pass


    @staticmethod
    def write_default_options():
        settings = constants.SETTINGS
        keys = settings.allKeys()

        if 'default_view' not in keys:
            settings.setValue('default_view', 0)

        if 'num_sending_repeats' not in keys:
            settings.setValue('num_sending_repeats', 0)

        if 'show_pause_as_time' not in keys:
            settings.setValue('show_pause_as_time', False)

        settings.sync()  # Ensure conf dir is created to have field types in place

        if not os.path.isfile(constants.FIELD_TYPE_SETTINGS):
            FieldType.save_to_xml(FieldType.default_field_types())

        bh = BackendHandler()
        for be in bh.device_backends.values():
            be.write_settings()
