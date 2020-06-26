import os
import subprocess
import sys
import tempfile
import time

import numpy as np
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal, QSize, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QCompleter, QDirModel, QApplication, QHeaderView, QRadioButton, \
    QFileDialog, qApp

from urh import settings, colormaps
from urh.controller.widgets.PluginFrame import PluginFrame
from urh.dev.BackendHandler import BackendHandler, Backends
from urh.dev.native import ExtensionHelper
from urh.models.FieldTypeTableModel import FieldTypeTableModel
from urh.signalprocessing.FieldType import FieldType
from urh.signalprocessing.Modulator import Modulator
from urh.signalprocessing.ProtocoLabel import ProtocolLabel
from urh.signalprocessing.Spectrogram import Spectrogram
from urh.ui.delegates.ComboBoxDelegate import ComboBoxDelegate
from urh.ui.ui_options import Ui_DialogOptions
from urh.util import util


class DeviceOptionsTableModel(QAbstractTableModel):
    header_labels = ["Software Defined Radio", "Info", "Native backend (recommended)", "GNU Radio backend"]

    def __init__(self, backend_handler: BackendHandler, parent=None):
        self.backend_handler = backend_handler

        super().__init__(parent)

    def update(self):
        self.beginResetModel()
        self.endResetModel()

    def columnCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.header_labels)

    def rowCount(self, parent: QModelIndex = None, *args, **kwargs):
        return len(self.backend_handler.DEVICE_NAMES)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]
        return super().headerData(section, orientation, role)

    def get_device_at(self, index: int):
        dev_key = self.backend_handler.get_key_from_device_display_text(self.backend_handler.DEVICE_NAMES[index])
        return self.backend_handler.device_backends[dev_key]

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        i = index.row()
        j = index.column()
        device = self.get_device_at(i)
        if role == Qt.DisplayRole:
            if j == 0:
                return self.backend_handler.DEVICE_NAMES[i]
            elif j == 1:
                if device.is_enabled:
                    if device.supports_rx and device.supports_tx:
                        device_info = "supports RX and TX"
                    elif device.supports_rx and not device.supports_tx:
                        device_info = "supports RX only"
                    elif not device.supports_rx and device.supports_tx:
                        device_info = "supports TX only"
                    else:
                        device_info = ""
                else:
                    device_info = "disabled"

                return device_info
            elif j == 2:
                return "" if device.has_native_backend else "not available"
            elif j == 3:
                return "" if device.has_gnuradio_backend else "not available"
        elif role == Qt.CheckStateRole:
            if j == 0 and (device.has_native_backend or device.has_gnuradio_backend):
                return Qt.Checked if device.is_enabled else Qt.Unchecked
            elif j == 2 and device.has_native_backend:
                return Qt.Checked if device.selected_backend == Backends.native else Qt.Unchecked
            elif j == 3 and device.has_gnuradio_backend:
                return Qt.Checked if device.selected_backend == Backends.grc else Qt.Unchecked

    def setData(self, index: QModelIndex, value, role=None):
        if not index.isValid():
            return False

        i, j = index.row(), index.column()
        device = self.get_device_at(i)
        if role == Qt.CheckStateRole:
            enabled = bool(value)
            if j == 0:
                device.is_enabled = enabled
            if j == 2:
                if enabled and device.has_native_backend:
                    device.selected_backend = Backends.native
                elif not enabled and device.has_gnuradio_backend:
                    device.selected_backend = Backends.grc
            elif j == 3:
                if enabled and device.has_gnuradio_backend:
                    device.selected_backend = Backends.grc
                elif not enabled and device.has_native_backend:
                    device.selected_backend = Backends.native

            self.update()
            device.write_settings()
            return True

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return None

        j = index.column()
        device = self.get_device_at(index.row())
        if j == 0 and not device.has_native_backend and not device.has_gnuradio_backend:
            return Qt.NoItemFlags

        if j in [1, 2, 3] and not device.is_enabled:
            return Qt.NoItemFlags

        if j == 2 and not device.has_native_backend:
            return Qt.NoItemFlags

        if j == 3 and not device.has_gnuradio_backend:
            return Qt.NoItemFlags

        flags = Qt.ItemIsEnabled

        if j in [0, 2, 3]:
            flags |= Qt.ItemIsUserCheckable

        return flags


class OptionsDialog(QDialog):
    values_changed = pyqtSignal(dict)

    def __init__(self, installed_plugins, highlighted_plugins=None, parent=None):
        super().__init__(parent)

        self.backend_handler = BackendHandler()

        self.ui = Ui_DialogOptions()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.Window)

        self.device_options_model = DeviceOptionsTableModel(self.backend_handler, self)
        self.device_options_model.update()
        self.ui.tblDevices.setModel(self.device_options_model)
        self.ui.tblDevices.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.ui.tblDevices.setItemDelegateForColumn(1, ComboBoxDelegate(["native", "GNU Radio"]))

        self.setAttribute(Qt.WA_DeleteOnClose)
        layout = QHBoxLayout(self.ui.tab_plugins)
        self.plugin_controller = PluginFrame(installed_plugins, highlighted_plugins, parent=self)
        layout.addWidget(self.plugin_controller)
        self.ui.tab_plugins.setLayout(layout)

        self.ui.btnViewBuildLog.hide()
        self.build_log = ""

        # We use bundled native device backends on windows, so no need to reconfigure them
        self.ui.groupBoxNativeOptions.setVisible(sys.platform != "win32")
        self.ui.labelIconTheme.setVisible(sys.platform == "linux")
        self.ui.comboBoxIconTheme.setVisible(sys.platform == "linux")

        self.ui.comboBoxTheme.setCurrentIndex(settings.read("theme_index", 0, int))
        self.ui.comboBoxIconTheme.setCurrentIndex(settings.read("icon_theme_index", 0, int))
        self.ui.checkBoxShowConfirmCloseDialog.setChecked(not settings.read('not_show_close_dialog', False, bool))
        self.ui.checkBoxHoldShiftToDrag.setChecked(settings.read('hold_shift_to_drag', True, bool))
        self.ui.checkBoxDefaultFuzzingPause.setChecked(settings.read('use_default_fuzzing_pause', True, bool))

        self.ui.checkBoxAlignLabels.setChecked(settings.read('align_labels', True, bool))

        self.ui.doubleSpinBoxRAMThreshold.setValue(100 * settings.read('ram_threshold', 0.6, float))

        if self.backend_handler.gr_python_interpreter:
            self.ui.lineEditGRPythonInterpreter.setText(self.backend_handler.gr_python_interpreter)

        self.ui.doubleSpinBoxFuzzingPause.setValue(settings.read("default_fuzzing_pause", 10 ** 6, int))
        self.ui.doubleSpinBoxFuzzingPause.setEnabled(settings.read('use_default_fuzzing_pause', True, bool))

        self.ui.checkBoxMultipleModulations.setChecked(settings.read("multiple_modulations", False, bool))

        self.ui.radioButtonLowModulationAccuracy.setChecked(Modulator.get_dtype() == np.int8)
        self.ui.radioButtonMediumModulationAccuracy.setChecked(Modulator.get_dtype() == np.int16)
        self.ui.radioButtonHighModulationAccuracy.setChecked(Modulator.get_dtype() == np.float32)

        completer = QCompleter()
        completer.setModel(QDirModel(completer))
        self.ui.lineEditGRPythonInterpreter.setCompleter(completer)

        self.ui.spinBoxFontSize.setValue(qApp.font().pointSize())

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
        self.restoreGeometry(settings.read("{}/geometry".format(self.__class__.__name__), type=bytes))

    def create_connects(self):
        self.ui.doubleSpinBoxFuzzingPause.valueChanged.connect(self.on_spinbox_fuzzing_pause_value_changed)
        self.ui.lineEditGRPythonInterpreter.editingFinished.connect(self.on_gr_python_interpreter_path_edited)
        self.ui.btnChooseGRPythonInterpreter.clicked.connect(self.on_btn_choose_gr_python_interpreter_clicked)
        self.ui.comboBoxTheme.currentIndexChanged.connect(self.on_combo_box_theme_index_changed)
        self.ui.checkBoxShowConfirmCloseDialog.clicked.connect(self.on_checkbox_confirm_close_dialog_clicked)
        self.ui.checkBoxHoldShiftToDrag.clicked.connect(self.on_checkbox_hold_shift_to_drag_clicked)
        self.ui.checkBoxAlignLabels.clicked.connect(self.on_checkbox_align_labels_clicked)
        self.ui.checkBoxDefaultFuzzingPause.clicked.connect(self.on_checkbox_default_fuzzing_pause_clicked)
        self.ui.btnAddLabelType.clicked.connect(self.on_btn_add_label_type_clicked)
        self.ui.btnRemoveLabeltype.clicked.connect(self.on_btn_remove_label_type_clicked)
        self.ui.radioButtonLowModulationAccuracy.clicked.connect(self.on_radio_button_low_modulation_accuracy_clicked)
        self.ui.radioButtonMediumModulationAccuracy.clicked.connect(self.on_radio_button_medium_modulation_accuracy_clicked)
        self.ui.radioButtonHighModulationAccuracy.clicked.connect(self.on_radio_button_high_modulation_accuracy_clicked)

        self.ui.doubleSpinBoxRAMThreshold.valueChanged.connect(self.on_double_spinbox_ram_threshold_value_changed)
        self.ui.btnRebuildNative.clicked.connect(self.on_btn_rebuild_native_clicked)
        self.ui.comboBoxIconTheme.currentIndexChanged.connect(self.on_combobox_icon_theme_index_changed)
        self.ui.checkBoxMultipleModulations.clicked.connect(self.on_checkbox_multiple_modulations_clicked)
        self.ui.btnViewBuildLog.clicked.connect(self.on_btn_view_build_log_clicked)
        self.ui.labelDeviceMissingInfo.linkActivated.connect(self.on_label_device_missing_info_link_activated)
        self.ui.spinBoxFontSize.editingFinished.connect(self.on_spin_box_font_size_editing_finished)

    def show_gnuradio_infos(self):
        self.ui.lineEditGRPythonInterpreter.setText(self.backend_handler.gr_python_interpreter)

        if self.backend_handler.gnuradio_is_installed:
            self.ui.lineEditGRPythonInterpreter.setStyleSheet("background-color: lightgreen")
            self.ui.lineEditGRPythonInterpreter.setToolTip("GNU Radio interface is working.")
        else:
            self.ui.lineEditGRPythonInterpreter.setStyleSheet("background-color: orange")
            self.ui.lineEditGRPythonInterpreter.setToolTip("GNU Radio is not installed or incompatible with "
                                                           "the configured python interpreter.")

    def read_options(self):
        self.ui.comboBoxDefaultView.setCurrentIndex(settings.read('default_view', 0, type=int))
        self.ui.spinBoxNumSendingRepeats.setValue(settings.read('num_sending_repeats', 0, type=int))
        self.ui.checkBoxPauseTime.setChecked(settings.read('show_pause_as_time', False, type=bool))

        self.old_show_pause_as_time = bool(self.ui.checkBoxPauseTime.isChecked())

        self.field_type_table_model.field_types = FieldType.load_from_xml()
        self.field_type_table_model.update()

    def refresh_device_tab(self):
        self.backend_handler.get_backends()
        self.show_gnuradio_infos()
        self.device_options_model.update()

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

        settings.write('default_view', self.ui.comboBoxDefaultView.currentIndex())
        settings.write('num_sending_repeats', self.ui.spinBoxNumSendingRepeats.value())
        settings.write('show_pause_as_time', self.ui.checkBoxPauseTime.isChecked())

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

        settings.write("{}/geometry".format(self.__class__.__name__), self.saveGeometry())
        super().closeEvent(event)

    def set_gnuradio_status(self):
        self.backend_handler.gr_python_interpreter = self.ui.lineEditGRPythonInterpreter.text()
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
        settings.write("ram_threshold", val / 100)

    @pyqtSlot(bool)
    def on_checkbox_confirm_close_dialog_clicked(self, checked: bool):
        settings.write("not_show_close_dialog", not checked)

    @pyqtSlot(int)
    def on_combo_box_theme_index_changed(self, index: int):
        settings.write('theme_index', index)

    @pyqtSlot(int)
    def on_combobox_icon_theme_index_changed(self, index: int):
        settings.write('icon_theme_index', index)
        util.set_icon_theme()

    @pyqtSlot(bool)
    def on_checkbox_hold_shift_to_drag_clicked(self, checked: bool):
        settings.write("hold_shift_to_drag", checked)

    @pyqtSlot(bool)
    def on_checkbox_default_fuzzing_pause_clicked(self, checked: bool):
        settings.write('use_default_fuzzing_pause', checked)
        self.ui.doubleSpinBoxFuzzingPause.setEnabled(checked)

    @pyqtSlot(float)
    def on_spinbox_fuzzing_pause_value_changed(self, value: float):
        settings.write("default_fuzzing_pause", int(value))

    @pyqtSlot()
    def on_gr_python_interpreter_path_edited(self):
        self.set_gnuradio_status()

    @pyqtSlot()
    def on_btn_choose_gr_python_interpreter_clicked(self):
        if sys.platform == "win32":
            dialog_filter = "Executable (*.exe);;All files (*.*)"
        else:
            dialog_filter = ""
        filename, _ = QFileDialog.getOpenFileName(self, self.tr("Choose python interpreter"), filter=dialog_filter)
        if filename:
            self.ui.lineEditGRPythonInterpreter.setText(filename)
            self.set_gnuradio_status()

    @pyqtSlot(bool)
    def on_checkbox_align_labels_clicked(self, checked: bool):
        settings.write("align_labels", checked)

    @pyqtSlot()
    def on_btn_rebuild_native_clicked(self):
        library_dirs = None if not self.ui.lineEditLibDirs.text() \
            else list(map(str.strip, self.ui.lineEditLibDirs.text().split(",")))
        include_dirs = None if not self.ui.lineEditIncludeDirs.text() \
            else list(map(str.strip, self.ui.lineEditIncludeDirs.text().split(",")))

        extensions, _ = ExtensionHelper.get_device_extensions_and_extras(library_dirs=library_dirs, include_dirs=include_dirs)

        self.ui.labelRebuildNativeStatus.setText(self.tr("Rebuilding device extensions..."))
        QApplication.instance().processEvents()
        build_cmd = [sys.executable, os.path.realpath(ExtensionHelper.__file__),
                     "build_ext", "--inplace", "-t", tempfile.gettempdir()]
        if library_dirs:
            build_cmd.extend(["-L", ":".join(library_dirs)])
        if include_dirs:
            build_cmd.extend(["-I", ":".join(include_dirs)])

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
    def on_checkbox_multiple_modulations_clicked(self):
        settings.write("multiple_modulations", self.ui.checkBoxMultipleModulations.isChecked())

    @pyqtSlot()
    def on_btn_view_build_log_clicked(self):
        if not self.build_log:
            return

        dialog = util.create_textbox_dialog(self.build_log, "Build log", parent=self)
        dialog.show()

    @pyqtSlot(str)
    def on_label_device_missing_info_link_activated(self, link: str):
        if link == "health_check":
            info = ExtensionHelper.perform_health_check()
            info += "\n" + BackendHandler.perform_soundcard_health_check()

            if util.get_shared_library_path():
                if sys.platform == "win32":
                    info += "\n\n[INFO] Used DLLs from " + util.get_shared_library_path()
                else:
                    info += "\n\n[INFO] Used shared libraries from " + util.get_shared_library_path()

            d = util.create_textbox_dialog(info, "Health check for native extensions", self)
            d.show()

    @pyqtSlot()
    def on_spin_box_font_size_editing_finished(self):
        settings.write("font_size", self.ui.spinBoxFontSize.value())
        font = qApp.font()
        font.setPointSize(self.ui.spinBoxFontSize.value())
        qApp.setFont(font)

    @pyqtSlot(bool)
    def on_radio_button_high_modulation_accuracy_clicked(self, checked):
        if checked:
            settings.write("modulation_dtype", "float32")

    @pyqtSlot(bool)
    def on_radio_button_medium_modulation_accuracy_clicked(self, checked):
        if checked:
            settings.write("modulation_dtype", "int16")

    @pyqtSlot(bool)
    def on_radio_button_low_modulation_accuracy_clicked(self, checked):
        if checked:
            settings.write("modulation_dtype", "int8")

    @staticmethod
    def write_default_options():
        keys = settings.all_keys()

        if 'default_view' not in keys:
            settings.write('default_view', 0)

        if 'num_sending_repeats' not in keys:
            settings.write('num_sending_repeats', 0)

        if 'show_pause_as_time' not in keys:
            settings.write('show_pause_as_time', False)

        settings.sync()  # Ensure conf dir is created to have field types in place

        if not os.path.isfile(settings.FIELD_TYPE_SETTINGS):
            FieldType.save_to_xml(FieldType.default_field_types())

        bh = BackendHandler()
        for be in bh.device_backends.values():
            be.write_settings()
