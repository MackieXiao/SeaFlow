from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from frontend.ui.mainwindow import *
from frontend.ui.node_item import *
from backend.sf_constructor import *


class CmdConstructor(object):
    @staticmethod
    def post_element(pipeline: str, category: str, elem_type: str, name: str) -> str:
        if type(pipeline) is not str or type(category) is not str or \
           type(elem_type) is not str or type(name) is not str:
            return ""
        return "POST Element=" + pipeline + "/" + category + "." + elem_type + "/" + name

    @staticmethod
    def delete_element(pipeline: str, elem_name: str) -> str:
        if type(pipeline) is not str or type(elem_name) is not str:
            return ""
        return "DELETE Element=" + pipeline + "/" + elem_name

    @staticmethod
    def post_link(pipeline: str, elem_o: str, oport: str, elem_i: str, iport:str) -> str:
        if type(pipeline) is not str or \
           type(elem_o) is not str or type(oport) is not str or \
           type(elem_i) is not str or type(iport) is not str:
            return ""
        return "POST Link=" + pipeline + "/" + elem_o + ":" + oport + "&" + pipeline + "/" + elem_i + ":" + iport

    @staticmethod
    def delete_link(pipeline: str, elem_o: str, oport: str, elem_i: str, iport: str) -> str:
        if type(pipeline) is not str or \
           type(elem_o) is not str or type(oport) is not str or \
           type(elem_i) is not str or type(iport) is not str:
            return ""
        return "DELETE Link=" + pipeline + "/" + elem_o + ":" + oport + "&" + pipeline + "/" + elem_i + ":" + iport


class AppMainWindow(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.default_project = "project0"
        self.default_pipeline = "pipeline0"
        self.ctor = SFConstructor()
        self.element = []

        self.title = 'SeaFlow'
        self.MainWindow = QMainWindow()

        # setup main window ui
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)



        self.ui.ProjectView.post_project(self.default_project)
        self.cmd("POST Pipeline=" + self.default_pipeline)
        self.ui.ProjectView.post_pipeline(self.default_project, self.default_pipeline)

        # signal and slot
        self.ui.CompBrowserTreeView.selectionModel().selectionChanged.connect(
            self.ui.CompBrowserView.slot_show_item
        )
        self.ui.CompBrowserTreeView.doubleClicked.connect(
            self.slot_post_element_item
        )
        self.ui.ProjectView.selectionModel().selectionChanged.connect(
            self.ui.NodeEditorView.slot_highlight_item
        )
        self.ui.NodeEditorView.linkEstablished.connect(
            self.slot_post_link
        )
        self.ui.NodeEditorView.deleteElement.connect(
            self.slot_delete_element_item
        )
        self.ui.NodeEditorView.deleteLink.connect(
            self.slot_delete_link_item
        )

        #self.MainWindow.showMaximized()
        self.MainWindow.show()
        self.MainWindow.setWindowTitle(self.title)

    def cmd(self, command: str) -> list:
        """
        pass a command to ctor and console browser
        :param command: input command
        :return: result from the ctor
        """
        if type(command) is not str:
            return [False]
        self.ui.ConsoleBrowser.append("> " + command)
        ret = self.ctor.cmd(command)
        if ret[0]:
            self.ui.ConsoleBrowser.append("< [ OK ]")
        else:
            self.ui.ConsoleBrowser.append("< [ ERROR ]")
        return ret

    def request_elem_name(self, elem_type: str) -> str:
        if type(elem_type) is not str:
            return ""
        count = 1
        name = elem_type + "_" + str(count)
        while name in self.element:
            count += 1
            name = elem_type + "_" + str(count)
        self.element.append(name)
        return name


    @pyqtSlot(QModelIndex)
    def slot_post_element_item(self, index: QModelIndex):
        category = index.parent().data()
        elem_type = index.data()
        if category == "Elements" or category is None:
            return
        name = self.request_elem_name(elem_type)
        cmd = CmdConstructor.post_element(self.default_pipeline, category, elem_type, name)
        if self.cmd(cmd)[0]:
            self.ui.NodeEditorView.post_element_item(category, elem_type, name)
            self.ui.ProjectView.post_element(self.default_project, self.default_pipeline, name)

    @pyqtSlot(UiElementItem)
    def slot_delete_element_item(self, elem_item: UiElementItem):
        cmd = CmdConstructor.delete_element(self.default_pipeline, elem_item.name())
        if self.cmd(cmd)[0]:
            self.ui.ProjectView.delete_element(self.default_project, self.default_pipeline, elem_item.name())

    @pyqtSlot(str, str, str, str)
    def slot_post_link(self, elem_o: str, oport: str, elem_i: str, iport: str):
        cmd = CmdConstructor.post_link(self.default_pipeline, elem_o, oport, elem_i, iport)
        if self.cmd(cmd)[0]:
            pass

    @pyqtSlot(UiLinkItem)
    def slot_delete_link_item(self, link_item: UiLinkItem):
        elem_o = link_item.oport().parentItem().name()
        oport = link_item.oport().name()
        elem_i = link_item.iport().parentItem().name()
        iport = link_item.iport().name()
        cmd = CmdConstructor.delete_link(self.default_pipeline, elem_o, oport, elem_i, iport)
        self.cmd(cmd)
