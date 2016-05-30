from PyQt5.QtCore import pyqtSlot, QRegExp
from PyQt5.QtGui import QRegExpValidator

from urh.signalprocessing.LabelSet import LabelSet
from urh.signalprocessing.ProtocolAnalyzer import ProtocolAnalyzer
from ..Plugin import LabelAssignPlugin
from ..AmbleAnalyzer.AmbleAssignAction import AmbleAssignAction


class AmbleAnalyzerPlugin(LabelAssignPlugin):
    def __init__(self):
        super().__init__(name="AmbleAnalyzer")

        if 'amble_pattern' in self.qsettings.allKeys():
            self.amble_pattern = self.qsettings.value('amble_pattern', type=str)
        else:
            self.amble_pattern = "10"

        if 'min_occurences' in self.qsettings.allKeys():
            self.min_occurences = self.qsettings.value('min_occurences', type=int)
        else:
            self.min_occurences = 8

    def create_connects(self):
        self.settings_frame.spinBoxMinOccurences.setValue(self.min_occurences)
        self.settings_frame.spinBoxMinOccurences.valueChanged.connect(self.set_min_occurences)

        self.settings_frame.lAmblePattern.setText(self.amble_pattern)
        self.settings_frame.lAmblePattern.textEdited.connect(self.set_amble_pattern)
        self.settings_frame.lAmblePattern.setValidator(QRegExpValidator(QRegExp("[0-1]+")))

        self.settings_frame.lPreview.setText(self.amble_pattern * self.min_occurences + "..")

    def set_min_occurences(self):
        self.min_occurences = self.settings_frame.spinBoxMinOccurences.value()
        self.settings_frame.lPreview.setText(self.amble_pattern * self.min_occurences + "..")
        self.qsettings.setValue('min_occurences', self.min_occurences)

    @pyqtSlot(str)
    def set_amble_pattern(self, text: str):
        self.amble_pattern = text
        self.settings_frame.lPreview.setText(self.amble_pattern * self.min_occurences + "..")
        self.qsettings.setValue('amble_pattern', self.amble_pattern)

    def get_action(self, groups, labelset: LabelSet):
        action = AmbleAssignAction(self.amble_pattern, self.min_occurences, groups, labelset)
        return action
