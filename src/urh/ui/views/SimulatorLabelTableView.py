from urh.models.SimulatorMessageFieldModel import SimulatorMessageFieldModel
from urh.ui.views.ProtocolLabelTableView import ProtocolLabelTableView


class SimulatorLabelTableView(ProtocolLabelTableView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def model(self) -> SimulatorMessageFieldModel:
        return super().model()

