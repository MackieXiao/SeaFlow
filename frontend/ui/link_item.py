from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import math


class UiLinkItem(QGraphicsPathItem):
    def __init__(self, parent=None, iport=None, oport=None):
        super().__init__(parent)
        self.__iport = iport
        self.__oport = oport
        self.__start_point = [0, 0]
        self.__end_point = [0, 0]
        self.__line_color = QColor("#AAAAAA")
        self.__line_color_selected = QColor("#EB5C20")
        self.__line_width = 3
        self.pen = QPen(self.__line_color, self.__line_width)
        self.set_interactive(False)

    def set_interactive(self, state: bool):
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, state)

    def set_iport(self, iport) -> bool:
        self.__iport = iport
        return True

    def set_oport(self, oport) -> bool:
        self.__oport = oport
        return True

    def iport(self):
        return self.__iport

    def oport(self):
        return self.__oport

    def set_start_point(self, x: float, y: float):
        self.__start_point = [x, y]

    def set_end_point(self, x: float, y: float):
        self.__end_point = [x, y]

    def start_point(self) -> list:
        return self.__start_point

    def end_point(self) -> list:
        return self.__end_point

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        self.update_path()
        self.pen = QPen(self.__line_color_selected if self.isSelected() else self.__line_color, self.__line_width)
        painter.setPen(self.pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def calculate_path(self):
        s = self.start_point()
        d = self.end_point()
        dist = (d[0] - s[0]) * 0.5

        cpx_s = +dist
        cpx_d = -dist
        cpy_s = 0
        cpy_d = 0

        if self.oport() is not None:
            if s[0] > d[0]:
                cpx_d *= -1
                cpx_s *= -1

                cpy_d = (s[1]-d[1]) / math.fabs((s[1]-d[1]) if (s[1]-d[1]) != 0 else 0.00001) * 100

                cpy_s = (d[1]-s[1]) / math.fabs((d[1]-s[1]) if (d[1]-s[1]) != 0 else 0.00001) * 100

        path = QPainterPath(QPainterPath(QPointF(self.__start_point[0], self.__start_point[1])))
        path.cubicTo(s[0]+cpx_s, s[1]+cpy_s, d[0]+cpx_d, d[1]+cpy_d, self.__end_point[0], self.__end_point[1])

        return path

    def update_path(self):
        path = self.calculate_path()#QPainterPath(QPainterPath(QPointF(self.__start_point[0], self.__start_point[1])))
        #path.lineTo(self.__end_point[0], self.__end_point[1])
        self.setPath(path)