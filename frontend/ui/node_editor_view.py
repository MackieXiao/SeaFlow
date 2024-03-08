from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from transitions import Machine
from frontend.ui.node_editor_scene import *
from frontend.ui.node_item import *
from backend.component.lib_loader import *
from frontend.ui.link_item import *


__all__ = ['UiNodeEditorView']


def Try(func):
    try:
        func()
    except:
        pass


# mouse button definition
MouseButtonRight = int(1)
MouseButtonLeft = int(2)
MouseButtonMiddle = int(4)


# mouse state machine definition
mouse_sm_state = ['Idle', 'Detecting', 'Pan', 'Zoom', "Select"]
mouse_sm_transitions = [
    {'source': 'Idle', 'dest': 'Detecting', 'trigger': 'rightPressed'},
    {'source': 'Idle', 'dest': "Select", 'trigger': 'leftPressed'},
    {'source': 'Select', 'dest': "Idle", 'trigger': 'leftReleased'},
    {'source': 'Detecting', 'dest': 'Idle', 'trigger': 'rightReleased'},
    {'source': 'Detecting', 'dest': 'Pan', 'trigger': 'moved'},
    {'source': 'Detecting', 'dest': 'Zoom', 'trigger': 'leftPressed'},
    {'source': 'Pan', 'dest': 'Zoom', 'trigger': 'leftPressed'},
    {'source': 'Pan', 'dest': 'Idle', 'trigger': 'rightReleased'},
    {'source': 'Pan', 'dest': 'Zoom', 'trigger': 'leftPressed'},
    {'source': 'Zoom', 'dest': 'Pan', 'trigger': 'leftReleased'},
    {'source': 'Zoom', 'dest': 'Idle', 'trigger': 'rightReleased'},
]


class MouseStateMachine(object):
    def __init__(self):
        self.state = None


class UiNodeEditorView(QGraphicsView):
    linkEstablished = pyqtSignal(str, str, str, str)
    deleteElement = pyqtSignal(UiElementItem)
    deleteLink = pyqtSignal(UiLinkItem)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__mouse_sm = MouseStateMachine()
        self.__mouse_btn = None
        self.__mouse_pos = QPointF()
        self.__zoom_factor = 1.0
        self.__zoom_step = 0.04
        self.__zoom_rng = [0.1, 10.0]
        self.elem_item = []
        self.link_item = []
        self.scene_offset_x = 0
        self.scene_offset_y = 0
        self.__link_start_port = None
        self.__link_offset_x = self.scene_offset_x
        self.__link_offset_y = self.scene_offset_y
        Machine(self.__mouse_sm, states=mouse_sm_state, transitions=mouse_sm_transitions, initial='Idle')
        self.__setup_ui()

    def __setup_ui(self):
        """
        setup ui
        :return: no return
        """
        self.setScene(UiNodeEditorScene(self))
        self.setFrameShape(self.Shape.NoFrame)
        self.setFrameShadow(self.Shadow.Plain)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        #self.setTransformationAnchor(self.ViewportAnchor.AnchorUnderMouse)

    def __getMouseButton(self, event):
        """
        get current button id
        :param event: mouse event
        :return: button id
        """
        btn = 0
        if event.button() == Qt.MouseButton.RightButton:
            btn |= MouseButtonRight
        if event.button() == Qt.MouseButton.LeftButton:
            btn |= MouseButtonLeft
        if event.button() == Qt.MouseButton.MiddleButton:
            btn |= MouseButtonMiddle
        self.__mouse_btn = btn

    def mousePressEvent(self, event, QMouseEvent=None):
        """
        mouse press event handler
        :param event: mouse event
        :param QMouseEvent: None
        :return: no return
        """
        self.__getMouseButton(event)
        if self.__mouse_btn == MouseButtonRight:
            Try(self.__mouse_sm.rightPressed)
        if self.__mouse_btn == MouseButtonLeft:
            Try(self.__mouse_sm.leftPressed)

        if self.__mouse_sm.state == 'Detecting':
            self.__mouse_pos = event.pos()
        elif self.__mouse_sm.state == 'Zoom':
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.SizeVerCursor)
            #self.__mouse_pos = event.pos()
        elif self.__mouse_sm.state == "Select":
            super().mousePressEvent(event)
            # create link event
            if self.__mouse_btn != MouseButtonLeft or \
               len(self.scene().selectedItems()) != 1 or type(self.scene().selectedItems()[0]) != UiElementPortItem:
                return
            if self.__link_start_port is None:
                self.__link_start_port = self.scene().selectedItems()[0]
                if self.__link_start_port.port_type() == PORT_TYPE_INPUT and len(self.__link_start_port.link()) != 0:
                    self.__link_start_port = None
                    return
                link = UiLinkItem()
                self.scene().addItem(link)
                x = self.__link_start_port.pos().x() + self.__link_start_port.parentItem().pos().x() + self.__link_start_port.ui_diameter/2
                y = self.__link_start_port.pos().y() + self.__link_start_port.parentItem().pos().y() + self.__link_start_port.ui_diameter/2
                link.set_start_point(x, y)
                link.set_end_point(x, y)
                link.setZValue(-1)
                link.update()
                self.link_item.append(link)
                self.__link_offset_x = self.scene_offset_x
                self.__link_offset_y = self.scene_offset_y
            else:
                port = self.scene().selectedItems()[0]
                if self.__link_start_port == port:
                    self.scene().removeItem(self.link_item[-1])
                    self.link_item.pop(-1)
                # link between two same port type is invalid
                elif self.__link_start_port.port_type() == port.port_type():
                    return
                else:
                    oport = self.__link_start_port if self.__link_start_port.port_type() == PORT_TYPE_OUTPUT else port
                    iport = self.__link_start_port if self.__link_start_port.port_type() == PORT_TYPE_INPUT else port
                    offset_x = self.scene_offset_x - self.__link_offset_x
                    offset_y = self.scene_offset_y - self.__link_offset_y
                    self.link_item[-1].set_iport(iport)
                    self.link_item[-1].set_oport(oport)
                    if not iport.post_link(self.link_item[-1]):
                        return

                    oport.post_link(self.link_item[-1])
                    x = port.x() + port.parentItem().pos().x() + port.ui_diameter/2 + offset_x
                    y = port.y() + port.parentItem().pos().y() + port.ui_diameter/2 + offset_y
                    if port.port_type() == PORT_TYPE_INPUT:
                        self.link_item[-1].set_end_point(x, y)
                        self.link_item[-1].set_interactive(True)
                        self.linkEstablished.emit(self.__link_start_port.parentItem().name(),
                                                  self.__link_start_port.name(),
                                                  port.parentItem().name(), port.name())
                    else:
                        self.link_item[-1].set_start_point(x, y)
                        self.link_item[-1].set_interactive(True)
                        self.linkEstablished.emit(port.parentItem().name(),
                                                  port.name(),
                                                  self.__link_start_port.parentItem().name(),
                                                  self.__link_start_port.name())

                self.__link_start_port = None

    def mouseMoveEvent(self, event, QMouseEvent=None):
        """
        mouse move event handler
        :param event: mouse event
        :param QMouseEvent: None
        :return: no return
        """
        self.__getMouseButton(event)
        Try(self.__mouse_sm.moved)

        if self.__mouse_sm.state == "Idle":
            super().mouseMoveEvent(event)
        elif self.__mouse_sm.state == "Select":
            super().mouseMoveEvent(event)
        elif self.__mouse_sm.state == 'Pan':
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            diff = self.__mouse_pos - event.pos()
            self.__mouse_pos = event.pos()
            diff_x = diff.x()*(1/self.__zoom_factor)
            diff_y = diff.y()*(1/self.__zoom_factor)

            self.scene().setSceneRect(self.scene().sceneRect().x() - diff_x,
                                      self.scene().sceneRect().y() - diff_y,
                                      self.scene().sceneRect().width(),
                                      self.scene().sceneRect().height())
            # move all the items
            for item in self.elem_item:
                item.setPos(item.pos().x() - diff_x,
                            item.pos().y() - diff_y)
            for item in self.link_item:
                item.setPos(item.pos().x() - diff_x,
                            item.pos().y() - diff_y)

            self.scene_offset_x += diff_x
            self.scene_offset_y += diff_y
            self.scene().update()
        elif self.__mouse_sm.state == 'Zoom':
            diff = self.__mouse_pos - event.pos()
            self.__mouse_pos = event.pos()
            if float(diff.y()) > 0:
                factor = 1.0 + self.__zoom_step
                if self.__zoom_factor * factor > self.__zoom_rng[1]:
                    factor = self.__zoom_rng[1] / self.__zoom_factor
            else:
                factor = 1.0 - self.__zoom_step
                if self.__zoom_factor * factor < self.__zoom_rng[0]:
                    factor = self.__zoom_rng[0] / self.__zoom_factor

            self.__zoom_factor *= factor
            self.scale(factor, factor)

        if self.__link_start_port is not None:
            pos = self.mapToScene(event.pos())
            x = (pos.x() + self.scene_offset_x - self.__link_offset_x)
            y = (pos.y() + self.scene_offset_y - self.__link_offset_y)
            if self.__link_start_port.port_type() == PORT_TYPE_INPUT:
                self.link_item[-1].set_start_point(x, y)
            else:
                self.link_item[-1].set_end_point(x, y)
            self.link_item[-1].update()

    def mouseReleaseEvent(self, event, QMouseEvent=None):
        """
        mouse release event handler
        :param event: mouse event
        :param QMouseEvent: None
        :return: no return
        """
        self.__getMouseButton(event)
        if self.__mouse_btn == MouseButtonRight:
            Try(self.__mouse_sm.rightReleased)
        if self.__mouse_btn == MouseButtonLeft:
            Try(self.__mouse_sm.leftReleased)

        if self.__mouse_sm.state == 'Idle':
            self.setDragMode(QGraphicsView.DragMode.NoDrag)
            self.setCursor(Qt.CursorShape.ArrowCursor)
            super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event, QMouseEvent=None):
        """
        mouse double click event handler
        :param event: mouse event
        :param QMouseEvent: None
        :return: no return
        """
        #self.__getMouseButton(event)
        #if event.button() == Qt.MouseButton.RightButton:
        #    Try(self.__mouse_sm.rightPressed)
        super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            for i in self.scene().selectedItems():
                if type(i) is UiElementItem:
                    self.delete_element_item(i)
                elif type(i) is UiLinkItem:
                    self.delete_link_item(i)

    def post_element_item(self, category: str, elem_type: str, name: str) -> bool:
        """
        post an element item to graphics scene
        :param category: element category
        :param elem_type: element type
        :param name: element name
        :return: True for success, False for fail
        """
        if lib_get_elem_info(category, elem_type) is None:
            return False
        item = UiElementItem(name, category, elem_type)
        item.set_interactive(True)
        self.scene().addItem(item)
        self.elem_item.append(item)
        return True

    def delete_element_item(self, elem_item: UiElementItem) -> bool:
        """
        delete an element item from graphics scene
        :param elem_item: element item
        :return: True for success, False for fail
        """
        if type(elem_item) is not UiElementItem:
            return False
        link = []
        for port in elem_item.iport():
            for l in port.link():
                link.append(l)
        for port in elem_item.oport():
            for l in port.link():
                link.append(l)
        for l in link:
            self.delete_link_item(l)
        self.scene().removeItem(elem_item)
        self.elem_item.remove(elem_item)
        self.deleteElement.emit(elem_item)
        return True

    def get_element_item(self, name: str) -> UiElementItem:
        """
        get an element item by name
        :param name: element name
        :return: element item, None for not found
        """
        if type(name) is not str:
            return None
        for e in self.elem_item:
            if e.name() == name:
                return e
        return None

    def delete_link_item(self, link_item: UiLinkItem) -> bool:
        """
        delete an element item from current graphics scene
        this operation will also delete the related link connection from the node
        :param link_item: link item
        :return: True for success, False for fail
        """
        if type(link_item) is not UiLinkItem:
            return False
        link_item.oport().delete_link(link_item)
        link_item.iport().delete_link(link_item)
        self.scene().removeItem(link_item)
        self.link_item.remove(link_item)
        self.deleteLink.emit(link_item)
        return True

    @pyqtSlot(QItemSelection)
    def slot_highlight_item(self, item: QItemSelection):
        """
        slot function for item highlight when related item in project view is selected
        :param item: selected item in project view
        :return: no return
        """
        for i in self.scene().selectedItems():
            i.setSelected(False)

        for i in item.indexes():
            if i.parent().data() is not None and i.parent().parent().data() is not None and \
               i.parent().parent().parent().data() is None:
                temp = self.get_element_item(i.data())
                if temp is not None:
                    temp.setSelected(True)
