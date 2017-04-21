from urh.ui.views.TableView import TableView

from urh.models.SimulatorMessageTableModel import SimulatorMessageTableModel

class SimulatorMessageTableView(TableView):
    def __init__(self, parent=None):
        super().__init__(parent)

    def model(self) -> SimulatorMessageTableModel:
        return super().model()