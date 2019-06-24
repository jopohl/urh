from urh.ui.KillerDoubleSpinBox import KillerDoubleSpinBox
from urh.ui.delegates.SpinBoxDelegate import SpinBoxDelegate


class KillerSpinBoxDelegate(SpinBoxDelegate):
    def __init__(self, minimum, maximum, parent=None, suffix=""):
        super().__init__(minimum, maximum, parent, suffix)

    def _get_editor(self, parent):
        editor = KillerDoubleSpinBox(parent)
        editor.setDecimals(3)
        return editor
