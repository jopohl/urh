from urh.ui.painting.SpectrogramScene import SpectrogramScene
from urh.ui.views.ZoomableGraphicView import ZoomableGraphicView


class SpectrogramGraphicView(ZoomableGraphicView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.move_y_with_drag = True
        self.setScene(SpectrogramScene())

    def scene(self) -> SpectrogramScene:
        return super().scene()

    @property
    def y_center(self):
        return self.sceneRect().height() // 2

    def auto_fit_view(self):
        pass
