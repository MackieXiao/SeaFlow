from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class UiConsoleTextBrowser(QTextBrowser):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Ubuntu", 10))
        self.setTextColor(QColor("#FFFFFFFF"))
        self.setFontPointSize(15)