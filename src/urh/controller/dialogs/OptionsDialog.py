import os
import platform
import sys
import tempfile
import time
import subprocess

from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QSize
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QCompleter, QDirModel, QApplication, QHeaderView, QStyleFactory, \
    QRadioButton, QFileDialog

from urh import constants, colormaps
from urh.controller.widgets.PluginFrame import PluginFrame
from urh.dev.BackendHandler import BackendHandler, Backends, BackendContainer
from urh.dev.native import ExtensionHelper
from urh.models.FieldTypeTableModel import FieldTypeTableModel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_options import Ui_DialogOptions
from urh.util import util


class OptionsDialog(QDialog):
    values_changed = pyqtSignal(dict)

    def __init__(self, installed_plugins, highlighted_plugins=None, parent=None):
        super().__init__(parent)

        self.backend_handler = BackendHandler()

        self.ui = Ui_DialogOptions()
        self.ui.setupUi(self)

        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QHBoxLayout(self.ui.tab_plugins)
        self.plugin_controller = PluginFrame(installed_plugins, highlighted_plugins, parent=self)
        layout.addWidget(self.plugin_controller)
        self.ui.tab_plugins.setLayout(layout)

        self.ui.btnViewBuildLog.hide()
        self.build_log = ""

        # We use bundled native device backends on windows, so no need to reconfigure them
        self.ui.groupBoxNativeOptions.setVisible(sys.platform != "win32")
        self.ui.labelWindowsError.setVisible(sys.platform == "win32" and platform.architecture()[0] != "64bit")
        self.ui.labelIconTheme.setVisible(sys.platform == "linux")
        self.ui.comboBoxIconTheme.setVisible(sys.platform == "linux")

        self.ui.comboBoxTheme.setCurrentIndex(constants.SETTINGS.value("theme_index", 0, int))
        self.ui.comboBoxIconTheme.setCurrentIndex(constants.SETTINGS.value("icon_theme_index", 0, int))
        self.ui.checkBoxShowConfirmCloseDialog.setChecked(
            not constants.SETTINGS.value('not_show_close_dialog', False, bool))
        self.ui.checkBoxHoldShiftToDrag.setChecked(constants.SETTINGS.value('hold_shift_to_drag', True, bool))
        self.ui.checkBoxDefaultFuzzingPause.setChecked(
            constants.SETTINGS.value('use_default_fuzzing_pause', True, bool))

        self.ui.checkBoxAlignLabels.setChecked(constants.SETTINGS.value('align_labels', True, bool))

        self.ui.doubleSpinBoxRAMThreshold.setValue(100 * constants.SETTINGS.value('ram_threshold', 0.6, float))

        self.ui.radioButtonGnuradioDirectory.setChecked(self.backend_handler.use_gnuradio_install_dir)
        self.ui.radioButtonPython2Interpreter.setChecked(not self.backend_handler.use_gnuradio_install_dir)
        if self.backend_handler.gnuradio_install_dir:
            self.ui.lineEditGnuradioDirectory.setText(self.backend_handler.gnuradio_install_dir)
        if self.backend_handler.python2_exe:
            self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)

        self.ui.doubleSpinBoxFuzzingPause.setValue(constants.SETTINGS.value("default_fuzzing_pause", 10 ** 6, int))
        self.ui.doubleSpinBoxFuzzingPause.setEnabled(constants.SETTINGS.value('use_default_fuzzing_pause', True, bool))

        self.ui.checkBoxMultipleModulations.setChecked(constants.SETTINGS.value("multiple_modulations", False, bool))

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEditPython2Interpreter.setCompleter(completer)
        self.ui.lineEditGnuradioDirectory.setCompleter(completer)

        for dev_name in self.backend_handler.DEVICE_NAMES:
            self.ui.listWidgetDevices.addItem(dev_name)

        self.set_device_status()

        self.ui.listWidgetDevices.setCurrentRow(0)
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
        self.old_num_sending_repeats = self.ui.spinBoxNumSendingRepeats.value()
        self.ui.labelRebuildNativeStatus.setText("")

        self.show_available_colormaps()

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
        self.ui.btnChoosePython2Interpreter.clicked.connect(self.on_btn_choose_python2_interpreter_clicked)
        self.ui.btnChooseGnuRadioDirectory.clicked.connect(self.on_btn_choose_gnuradio_directory_clicked)
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
        self.ui.btnHealthCheck.clicked.connect(self.on_btn_health_check_clicked)
        self.ui.comboBoxIconTheme.currentIndexChanged.connect(self.on_combobox_icon_theme_index_changed)
        self.ui.checkBoxMultipleModulations.clicked.connect(self.on_checkbox_multiple_modulations_clicked)
        self.ui.btnViewBuildLog.clicked.connect(self.on_btn_view_build_log_clicked)

    def show_gnuradio_infos(self):
        self.ui.lineEditPython2Interpreter.setText(self.backend_handler.python2_exe)
        self.ui.lineEditGnuradioDirectory.setText(self.backend_handler.gnuradio_install_dir)

        if self.backend_handler.gnuradio_is_installed:
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

    def set_device_status(self):
        for i in range(self.ui.listWidgetDevices.count()):
            w = self.ui.listWidgetDevices.item(i)
            dev_key = self.__get_key_from_device_display_text(w.text())
            is_enabled = self.backend_handler.device_backends[dev_key].is_enabled
            selected_backend = self.backend_handler.device_backends[dev_key].selected_backend.value
            suffix = self.tr("enabled") if is_enabled else self.tr("disabled")
            dev_name = next(dn for dn in BackendHandler.DEVICE_NAMES if dn.lower() == dev_key)
            w.setText("{0}\t ({2})\t {1}".format(dev_name, suffix, selected_backend))

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
        self.set_device_status()

        self.ui.lineEditGnuradioDirectory.setEnabled(self.backend_handler.use_gnuradio_install_dir)
        self.ui.lineEditPython2Interpreter.setDisabled(self.backend_handler.use_gnuradio_install_dir)

    def show_available_colormaps(self):
        height = 50

        selected = colormaps.read_selected_colormap_name_from_settings()
        for colormap_name in sorted(colormaps.maps.keys()):
            image = Spectrogram.create_colormap_image(colormap_name, height=height)
            rb = QRadioButton(colormap_name)
            rb.setObjectName(colormap_name)
            rb.setChecked(colormap_name == selected)
            rb.setIcon(QIcon(QPixmap.fromImage(image)))
            rb.setIconSize(QSize(256, height))
            self.ui.scrollAreaWidgetSpectrogramColormapContents.layout().addWidget(rb)

    def closeEvent(self, event: QCloseEvent):
        changed_values = {}
        if bool(self.ui.checkBoxPauseTime.isChecked()) != self.old_show_pause_as_time:
            changed_values['show_pause_as_time'] = bool(self.ui.checkBoxPauseTime.isChecked())
        if self.old_default_view != self.ui.comboBoxDefaultView.currentIndex():
            changed_values['default_view'] = self.ui.comboBoxDefaultView.currentIndex()
        if self.old_num_sending_repeats != self.ui.spinBoxNumSendingRepeats.value():
            changed_values["num_sending_repeats"] = self.ui.spinBoxNumSendingRepeats.value()

        settings = constants.SETTINGS
        settings.setValue('default_view', self.ui.comboBoxDefaultView.currentIndex())
        settings.setValue('num_sending_repeats', self.ui.spinBoxNumSendingRepeats.value())
        settings.setValue('show_pause_as_time', self.ui.checkBoxPauseTime.isChecked())

        FieldType.save_to_xml(self.field_type_table_model.field_types)
        self.plugin_controller.save_enabled_states()
        for plugin in self.plugin_controller.model.plugins:
            plugin.destroy_settings_frame()

        for i in range(self.ui.scrollAreaWidgetSpectrogramColormapContents.layout().count()):
            widget = self.ui.scrollAreaWidgetSpectrogramColormapContents.layout().itemAt(i).widget()
            if isinstance(widget, QRadioButton) and widget.isChecked():
                selected_colormap_name = widget.objectName()
                if selected_colormap_name != colormaps.read_selected_colormap_name_from_settings():
                    colormaps.choose_colormap(selected_colormap_name)
                    colormaps.write_selected_colormap_to_settings(selected_colormap_name)
                    changed_values["spectrogram_colormap"] = selected_colormap_name
                break

        self.values_changed.emit(changed_values)

        constants.SETTINGS.setValue("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    def set_gnuradio_status(self):
        self.backend_handler.python2_exe = self.ui.lineEditPython2Interpreter.text()
        constants.SETTINGS.setValue("python2_exe", self.ui.lineEditPython2Interpreter.text())

        self.backend_handler.gnuradio_install_dir = self.ui.lineEditGnuradioDirectory.text()
        constants.SETTINGS.setValue("gnuradio_install_dir", self.ui.lineEditGnuradioDirectory.text())

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

    @pyqtSlot(int)
    def on_combobox_icon_theme_index_changed(self, index: int):
        constants.SETTINGS.setValue('icon_theme_index', index)
        util.set_icon_theme()

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
    def on_btn_choose_python2_interpreter_clicked(self):
        if sys.platform == "win32":
            dialog_filter = "Executable (*.exe);;All files (*.*)"
        else:
            dialog_filter = ""
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Choose python2 interpreter"), filter=dialog_filter)
        if filename:
            self.ui.lineEditPython2Interpreter.setText(filename)
            self.set_gnuradio_status()

    @pyqtSlot()
    def on_btn_choose_gnuradio_directory_clicked(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose GNU Radio directory")
        if directory:
            self.ui.lineEditGnuradioDirectory.setText(directory)
            self.set_gnuradio_status()

    @pyqtSlot()
    def on_chk_box_device_enabled_clicked(self):
        self.selected_device.is_enabled = bool(self.ui.chkBoxDeviceEnabled.isChecked())
        self.selected_device.write_settings()
        self.set_device_status()

    @pyqtSlot()
    def on_rb_gnuradio_backend_clicked(self):
        if Backends.grc in self.selected_device.avail_backends:
            self.ui.rbGnuradioBackend.setChecked(True)
            self.selected_device.selected_backend = Backends.grc
            self.selected_device.write_settings()
            self.set_device_status()

    @pyqtSlot()
    def on_rb_native_backend_clicked(self):
        if Backends.native in self.selected_device.avail_backends:
            self.ui.rbNativeBackend.setChecked(True)
            self.selected_device.selected_backend = Backends.native
            self.selected_device.write_settings()
            self.set_device_status()

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
        extensions = ExtensionHelper.get_device_extensions(use_cython=False, library_dirs=library_dirs)

        self.ui.labelRebuildNativeStatus.setText(self.tr("Rebuilding device extensions..."))
        QApplication.instance().processEvents()
        build_cmd = [sys.executable, os.path.realpath(ExtensionHelper.__file__),
                     "build_ext", "--inplace", "-t", tempfile.gettempdir()]
        if library_dirs:
            build_cmd.extend(["-L", ":".join(library_dirs)])

        subprocess.call([sys.executable, os.path.realpath(ExtensionHelper.__file__), "clean", "--all"])
        p = subprocess.Popen(build_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        num_dots = 1
        while p.poll() is None:
            self.ui.labelRebuildNativeStatus.setText(self.tr("Rebuilding device extensions" + ". " * num_dots))
            QApplication.instance().processEvents()
            time.sleep(0.1)
            num_dots %= 10
            num_dots += 1

        rc = p.returncode
        if rc == 0:
            self.ui.labelRebuildNativeStatus.setText(self.tr("<font color=green>"
                                                             "Rebuilt {0} device extensions. "
                                                             "</font>"
                                                             "Please restart URH.".format(len(extensions))))
        else:
            self.ui.labelRebuildNativeStatus.setText(self.tr("<font color='red'>"
                                                             "Failed to rebuild {0} device extensions. "
                                                             "</font>"
                                                             "Run URH as root (<b>sudo urh</b>) "
                                                             "and try again.".format(len(extensions))))

        self.build_log = p.stdout.read().decode()
        self.ui.btnViewBuildLog.show()

    @pyqtSlot()
    def on_btn_health_check_clicked(self):
        info = ExtensionHelper.perform_health_check()

        if util.get_windows_lib_path():
            info += "\n\n[INFO] Used DLLs from " + util.get_windows_lib_path()

        d = util.create_textbox_dialog(info, "Health check for native extensions", self)
        d.show()

    @pyqtSlot()
    def on_checkbox_multiple_modulations_clicked(self):
        constants.SETTINGS.setValue("multiple_modulations", self.ui.checkBoxMultipleModulations.isChecked())

    @pyqtSlot()
    def on_btn_view_build_log_clicked(self):
        if not self.build_log:
            return

        dialog = util.create_textbox_dialog(self.build_log, "Build log", parent=self)
        dialog.show()

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
