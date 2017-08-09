from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class SpectrogramGraphicView(ZoomableGraphicView):
    def __init__(self, parent=None):
        super().__init__(parent)

    @property
    def y_center(self):
        return self.sceneRect().height() // 2

    def auto_fit_view(self):
        pass
