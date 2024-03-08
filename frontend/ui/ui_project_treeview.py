from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from backend.component.lib_loader import *


class UiProjectViewStandardItem(QStandardItem):
    def __init__(self, txt='', font_size=12, set_bold=False, color=QColor(0xDD, 0xD6, 0xC5)):
        super().__init__()
        #font = QFont('Open Sans', font_size)
        font = QFont('Ubuntu', font_size)
        font.setBold(set_bold)

        self.setEditable(False)
        self.setForeground(color)
        self.setFont(font)
        self.setText(txt)


class UiProjectTreeView(QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.tree_model = QStandardItemModel(self)
        self.root_node = self.tree_model.invisibleRootItem()

        self.__setup_ui()

    def __setup_ui(self):
        """
        setup ui
        :return: no return
        """
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFrameShape(self.Shape.NoFrame)
        self.setFrameShadow(self.Shadow.Plain)
        self.setModel(self.tree_model)
        self.setSortingEnabled(True)
        self.expandAll()
        title = UiProjectViewStandardItem("Project View", font_size=20, set_bold=True)
        title.setBackground(QColor(0x4E, 0x51, 0x57))
        self.tree_model.setHorizontalHeaderItem(0, title)

    def __get_project_node(self, project: str) -> UiProjectViewStandardItem:
        """
        get the project item node
        :param project: project name
        :return: project node class, None for not found
        """
        i = 0
        node = self.root_node.child(i, 0)
        while node is not None:
            if node.text() == project:
                return node
            i += 1
            node = self.root_node.child(i, 0)
        return None

    def post_project(self, project: str) -> bool:
        """
        post a project to the treeview
        :param project: project name
        :return: True for success, False for fail
        """
        if type(project) is not str or self.__get_project_node(project) is not None:
            return False

        p = UiProjectViewStandardItem(project, font_size=16, set_bold=True)
        self.root_node.appendRow(p)
        self.expandAll()
        return True

    def __get_pipeline_node(self, project: str, pipeline: str) -> UiProjectViewStandardItem:
        """
        get pipeline item node
        :param project_node: project item node
        :param pipeline_name: pipeline name
        :return: pipeline item node, None for not found
        """
        project_node = self.__get_project_node(project)
        if project_node is None:
            return None
        i = 0
        node = project_node.child(i, 0)
        while node is not None:
            if node.text() == pipeline:
                return node
            i += 1
            node = project_node.child(i, 0)
        return None

    def post_pipeline(self, project: str, pipeline: str) -> bool:
        """
        post a pipeline to project in treeview
        :param project: project name
        :param pipeline: pipeline name
        :return: True for success, False for fail
        """
        if type(project) is not str or type(pipeline) is not str:
            return False
        project_node = self.__get_project_node(project)
        if project_node is None or self.__get_pipeline_node(project, pipeline) is not None:
            return False
        p = UiProjectViewStandardItem(pipeline, font_size=14)
        project_node.appendRow(p)
        self.expandAll()
        return True

    def __get_element_node(self, project: str, pipeline: str, element: str) -> UiProjectViewStandardItem:
        """
        get element item node
        :param project: project name
        :param pipeline: pipeline name
        :param element: element name
        :return: element item node, None for not found
        """
        pipeline_node = self.__get_pipeline_node(project, pipeline)
        if pipeline_node is None:
            return None
        i = 0
        node = pipeline_node.child(i, 0)
        while node is not None:
            if node.text() == element:
                return node
            i += 1
            node = pipeline_node.child(i, 0)
        return None

    def post_element(self, project: str, pipeline: str, element: str) -> bool:
        """
        post an element to pipeline in treeview
        :param project: project name
        :param pipeline: pipeline name
        :param element: element name
        :return: True for success, False for fail
        """
        if type(project) is not str or type(pipeline) is not str or type(element) is not str:
            return False
        pipeline_node = self.__get_pipeline_node(project, pipeline)
        if pipeline_node is None or self.__get_element_node(project, pipeline, element) is not None:
            return False
        p = UiProjectViewStandardItem(element, font_size=14)
        pipeline_node.appendRow(p)
        self.expandAll()
        return True

    def delete_element(self, project: str, pipeline: str, element: str) -> bool:
        """
        delete an element from pipeline in the treeview
        :param project: project name
        :param pipeline: pipeline name
        :param element: element name
        :return: True for success, False for fail
        """
        if type(project) is not str or type(pipeline) is not str or type(element) is not str:
            return False
        pipeline_node = self.__get_pipeline_node(project, pipeline)
        elem_node = self.__get_element_node(project, pipeline, element)
        if pipeline_node is None or elem_node is None:
            return False
        pipeline_node.removeRow(elem_node.row())
        self.expandAll()
        return True
