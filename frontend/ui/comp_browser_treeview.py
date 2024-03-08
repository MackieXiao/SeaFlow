from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from backend.component.lib_loader import *


class UiCompBrowserStandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0xDD, 0xD6, 0xC5)):
        super().__init__()
        #font = QFont('Open Sans', font_size)
        font = QFont('Ubuntu', font_size)
        font.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(font)
        self.setText(txt)


class UiCompBrowserTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__setup_ui()

    def __setup_ui(self):
        """
        setup ui
        :return: no return
        """
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFrameShape(self.Shape.NoFrame)
        self.setFrameShadow(self.Shadow.Plain)
        self.__setup_tree_model()

    def __setup_tree_model(self):
        tree_model = QStandardItemModel(self)
        root_node = tree_model.invisibleRootItem()

        title = UiCompBrowserStandardItem("Component Library", font_size=24, set_bold=True)
        title.setBackground(QColor(0x4E, 0x51, 0x57))
        tree_model.setHorizontalHeaderItem(0, title)

        # setup component list
        self.__construct_node(root_node, lib_get_comp_list(), 3)
        self.setModel(tree_model)
        self.setSortingEnabled(True)
        self.expandAll()

    def __construct_node(self, node, data: dict, depth):
        depth -= 1
        if depth < 0:
            return
        for key in data.keys():
            if depth == 2:
                n = UiCompBrowserStandardItem("Elements", font_size=20, set_bold=True)
            else:
                n = UiCompBrowserStandardItem(key, font_size=14)
            node.appendRow(n)
            self.__construct_node(n, data[key], depth)

        node.sortChildren(0, order=Qt.SortOrder.AscendingOrder)
