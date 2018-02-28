from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget

from urh import constants
from urh.controller.dialogs.ModulatorDialog import ModulatorDialog
from urh.signalprocessing.Modulator import Modulator
from urh.ui.ui_modulation_settings_widget import Ui_ModulationSettings


class ModulationSettingsWidget(QWidget):
    def __init__(self, modulators, selected_index=0, signal_tree_model=None, parent=None):
        """

        :type modulators: list of Modulator
        :param parent:
        """
        super().__init__(parent)
        self.ui = Ui_ModulationSettings()
        self.ui.setupUi(self)

        self.ui.labelModulationProfile.setVisible(constants.SETTINGS.value("multiple_modulations", False, bool))
        self.ui.comboBoxModulationProfiles.setVisible(constants.SETTINGS.value("multiple_modulations", False, bool))

        self.signal_tree_model = signal_tree_model
        self.modulators = modulators  # type: list[Modulator]
        for modulator in self.modulators:
            self.ui.comboBoxModulationProfiles.addItem(modulator.name)

        self.ui.comboBoxModulationProfiles.setCurrentIndex(selected_index)

        self.show_selected_modulation_infos()
        self.create_connects()

    @property
    def selected_modulator(self) -> Modulator:
        return self.modulators[self.ui.comboBoxModulationProfiles.currentIndex()]

    @selected_modulator.setter
    def selected_modulator(self, value: Modulator):
        if value in self.modulators:
            self.ui.comboBoxModulationProfiles.setCurrentIndex(self.modulators.index(value))

    def create_connects(self):
        self.ui.comboBoxModulationProfiles.currentIndexChanged.connect(self.on_cb_modulation_type_current_index_changed)
        self.ui.btnConfigurationDialog.clicked.connect(self.on_btn_configuration_dialog_clicked)

    def show_selected_modulation_infos(self):
        modulator = self.selected_modulator
        self.ui.labelCarrierFrequencyValue.setText(modulator.carrier_frequency_str)
        self.ui.labelBitLengthValue.setText(modulator.bit_len_str)
        self.ui.labelSampleRateValue.setText(modulator.sample_rate_str)
        self.ui.labelModulationTypeValue.setText(modulator.modulation_type_verbose_str)
        prefixes = {"ASK": "Amplitude", "PSK": "Phase", "FSK": "Frequency", "GFSK": "Frequency"}
        self.ui.labelParamZero.setText(prefixes[modulator.modulation_type_str] + " for 0:")
        self.ui.labelParamOne.setText(prefixes[modulator.modulation_type_str] + " for 1:")

        self.ui.labelParamZeroValue.setText(modulator.param_for_zero_str)
        self.ui.labelParamOneValue.setText(modulator.param_for_one_str)

    @pyqtSlot()
    def on_cb_modulation_type_current_index_changed(self):
        self.show_selected_modulation_infos()

    @pyqtSlot()
    def on_btn_configuration_dialog_clicked(self):
        dialog = ModulatorDialog(self.modulators, tree_model=self.signal_tree_model, parent=self)
        dialog.ui.comboBoxCustomModulations.setCurrentIndex(self.ui.comboBoxModulationProfiles.currentIndex())
        dialog.finished.connect(self.refresh_modulators_from_dialog)
        dialog.show()
        dialog.initialize("101010")

    @pyqtSlot()
    def refresh_modulators_from_dialog(self):
        current_index = 0
        if type(self.sender()) == ModulatorDialog:
            current_index = self.sender().ui.comboBoxCustomModulations.currentIndex()

        self.ui.comboBoxModulationProfiles.clear()
        for modulator in self.modulators:
            self.ui.comboBoxModulationProfiles.addItem(modulator.name)

        self.ui.comboBoxModulationProfiles.setCurrentIndex(current_index)
        self.show_selected_modulation_infos()

if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication([""])
    w = ModulationSettingsWidget([Modulator("test")])
    w.show()
    app.exec()