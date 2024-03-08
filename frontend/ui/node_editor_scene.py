from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class UiNodeEditorScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(-self.canvas.width // 2, -self.canvas.height // 2, self.canvas.width, self.canvas.height)
        color = QColor()
        color.setRgb(*self.canvas.background_color)
        self.setBackgroundBrush(color)


    class canvas(object):
        width = 50000
        height = 50000
        background_color = [63, 65, 68, 255]
        grid_interval = 50
        grid_width = 1
        grid_color = [33, 35, 38, 255]

    def drawBackground(self, painter, QPainter=None, *args, **kwargs):
        super().drawBackground(painter, QPainter)

        color = QColor()
        color.setRgb(*self.canvas.grid_color)
        pen_line = QPen(QColor(color), self.canvas.grid_width)
        rect: QRectF = self.sceneRect()
        left = int(rect.left())
        right = int(rect.right())
        top = int(rect.top())
        bottom = int(rect.bottom())

        line: list = []
        for x in range(left, right, self.canvas.grid_interval):
            line.append(QLineF(x, top, x, bottom))

        for y in range(top, bottom, self.canvas.grid_interval):
            line.append(QLineF(left, y, right, y))

        painter.setPen(pen_line)
        painter.drawLines(*line)
