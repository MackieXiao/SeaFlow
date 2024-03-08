from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from backend.component.comp_element import *
from frontend.ui.link_item import *


# element port type
PORT_TYPE_OUTPUT = 0
PORT_TYPE_INPUT = 1


class UiElementPortItem(QGraphicsEllipseItem):
    def __init__(self, parent, port_name, port_type):
        super().__init__(parent)
        self.__name = port_name
        self.__type = port_type
        self.__link = []
        self.ui_diameter = 16  # port diameter
        self.ui_background_normal_color = QColor("#EB5C20")
        self.ui_background_hover_color = QColor("#00AA00")
        self.ui_background_color = self.ui_background_normal_color
        self.ui_outline_normal_color = QColor("#202020")
        self.ui_outline_color = self.ui_outline_normal_color
        self.ui_outline_width = 2
        self.__interactive = False
        self.set_interactive(True)

    def name(self) -> str:
        """
        get port name
        :return: port name
        """
        return self.__name

    def link(self) -> list:
        return self.__link

    def port_type(self) -> int:
        """
        get port type
        :return: port type
        """
        return self.__type

    def post_link(self, link_item: UiLinkItem) -> bool:
        """
        post a link item to current port
        :param link_item: link item
        :return: True for success, False for fail
        """
        # every input port can only have one linkage
        if self.__type == PORT_TYPE_INPUT and len(self.__link) != 0:
            return False
        # make sure every linkage in current port is unique
        if link_item in self.__link:
            return False
        self.__link.append(link_item)
        return True

    def delete_link(self, link_item: UiLinkItem) -> bool:
        """
        delete a link item from current port
        :param link_item: link item
        :return: True for success, False for fail
        """
        if link_item in self.__link:
            self.__link.remove(link_item)
            return True
        else:
             return False

    def set_interactive(self, state: bool):
        """
        set the port as an interactive item
        :param state: interactive state
        :return: no return
        """
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, state)  # set the item is selectable
        self.setAcceptHoverEvents(state)
        self.__interactive = True

    def paint(self, painter, QPainter=None, *args, **kwargs):
        # draw background
        path_background = QPainterPath()
        path_background.addEllipse(self.rect().x(), self.rect().y(), self.ui_diameter, self.ui_diameter)
        painter.setBrush(QBrush(self.ui_background_color))
        painter.drawPath(path_background.simplified())

        # draw outline
        path_outline = QPainterPath()
        path_outline.addEllipse(self.rect().x(), self.rect().y(), self.ui_diameter, self.ui_diameter)
        pen = QPen(self.ui_outline_color, self.ui_outline_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        if self.__interactive:
            self.ui_background_color = self.ui_background_hover_color

    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        if self.__interactive:
            self.ui_background_color = self.ui_background_normal_color


class UiElementItem(QGraphicsItem):
    def __init__(self, name: str, elem_category: str, elem_type: str):
        super().__init__(None)
        self.elem = CompElement(None, name, elem_category, elem_type)
        # ui: title
        self.ui_title_class = QGraphicsTextItem(self)
        self.ui_tite_background_color = QColor("#FF595959")
        self.ui_title_text_color = QColor("#FFDDD6C5")
        self.ui_title_text_size = 20
        self.ui_title_height = 50
        # ui: element type
        self.ui_type_class = QGraphicsTextItem(self)
        self.ui_type_text_color = QColor("#FFDAD8D6")
        self.ui_type_font = QFont("Ubuntu", 15)
        # ui: element port
        self.ui_port_node_radius = 8
        self.ui_port_node_color = QColor("#FFEB5C20")
        self.ui_port_text_color = QColor("#FFFAF8F6")
        self.ui_port_text_font = QFont("Ubuntu", 20)
        self.ui_port_node_text_padding = 5
        self.ui_port_spacing_y = 50
        self.ui_iport_node = []
        self.ui_oport_node = []
        self.ui_iport_text = []
        self.ui_oport_text = []
        self.body_background_color = QColor("#FF363636")
        self.ui_rect_width, self.ui_rect_height = self.__calculate_rect_size()
        self.ui_full_width = self.ui_rect_width + 2*self.ui_port_node_radius
        self.ui_full_height = self.ui_rect_height + 35
        self.ui_rect_radius = 10  # round corner
        # ui: outline
        self.ui_outline_color = QColor("#FF202020")
        self.ui_outline_color_selected = QColor("#FFFFA637")
        self.ui_outline_width = 3

        # template value for snap
        self.__snap_gird_interval = 50
        self.__snap_x = 0
        self.__snap_y = 0
        self.__snap_offset_x = 0
        self.__snap_offset_y = 0

        # template value for link movement
        self.__link_x = 0
        self.__link_y = 0

        # interact flag
        self.__flag_interactive = False

        self.__setup_ui()

    def iport(self):
        return self.ui_iport_node

    def oport(self):
        return self.ui_oport_node

    def __setup_ui(self):
        """
        setup ui
        :return: no return
        """
        # title text
        self.__draw_title_text()
        self.__draw_port()
        self.__draw_elem_type()
        self.set_interactive(False)

    def __draw_title_text(self):
        """
        draw title text at the top of the node
        :return: no return
        """
        font = QFont("Ubuntu", self.ui_title_text_size)
        font.setBold(True)
        self.ui_title_class.setDefaultTextColor(self.ui_title_text_color)
        self.ui_title_class.setFont(font)
        self.ui_title_class.setPos(10, 5)
        self.ui_title_class.setPlainText(self.elem.name())

    def __draw_port(self):
        """
        draw node port info
        :return: no return
        """
        width, height = self.__calculate_rect_size()
        node_diameter = 2 * self.ui_port_node_radius
        x = 0
        y = self.ui_title_height + self.ui_port_spacing_y
        for i in self.elem.iport():
            text = QGraphicsTextItem(self)
            node = UiElementPortItem(self, i, PORT_TYPE_INPUT)
            node.setRect(0, 0, node_diameter, node_diameter)
            node.setPos(-self.ui_port_node_radius, y-self.ui_port_node_radius)
            node.setBrush(QBrush(self.ui_port_node_color))
            text.setDefaultTextColor(self.ui_port_text_color)
            text.setFont(self.ui_port_text_font)
            text.setPos(x + self.ui_port_node_radius + self.ui_port_node_text_padding,
                        y - text.document().size().height()/2)
            text.setPlainText(i)
            self.ui_iport_text.append(text)
            self.ui_iport_node.append(node)
            y += self.ui_port_spacing_y

        x = width
        y = self.ui_title_height + self.ui_port_spacing_y
        for o in self.elem.oport():
            text = QGraphicsTextItem(self)
            text.setDefaultTextColor(self.ui_port_text_color)
            text.setFont(self.ui_port_text_font)
            text.setPlainText(o)
            text.setPos(x - text.boundingRect().width() - self.ui_port_node_text_padding - self.ui_port_node_radius, y - text.document().size().height()/2)
            node = UiElementPortItem(self, o, PORT_TYPE_OUTPUT)
            node.setRect(0, 0, node_diameter, node_diameter)
            node.setPos(x-self.ui_port_node_radius, y - self.ui_port_node_radius)
            node.setBrush(QBrush(self.ui_port_node_color))
            self.ui_oport_text.append(text)
            self.ui_oport_node.append(node)
            y += self.ui_port_spacing_y

    def __draw_elem_type(self):
        """
        draw element type at the bottom of the node
        :return: no return
        """
        self.ui_type_class.setDefaultTextColor(self.ui_type_text_color)
        self.ui_type_class.setFont(self.ui_type_font)
        self.ui_type_class.setPos(0, self.ui_rect_height)
        self.ui_type_class.setPlainText(self.elem.category() + "." + self.elem.elem_type())

    def name(self):
        return self.elem.name()

    def comp_type(self):
        return self.elem.elem_type()

    def set_name(self, name: str) -> bool:
        if type(name) is not str or not self.elem.set_name(name):
            return False
        self.ui_title_class.setPlainText(self.elem.name())

    def __calculate_rect_size(self):
        """
        calculate the node rectangle width and height based on the info
        :return: rect width and height
        """
        title_width = 17 * len(self.elem.name())
        oport = []
        for o in self.elem.oport():
            oport.append(len(o))
        iport = []
        for i in self.elem.iport():
            iport.append(len(i))
        iport_width = 0 if len(iport) == 0 else max(iport)*15
        oport_width = 0 if len(oport) == 0 else max(oport)*15
        port_width = iport_width + oport_width + 100
        port_height = self.ui_title_height + (max(len(self.elem.iport()), len(self.elem.oport()))+1)*50

        width = max(port_width, title_width)
        width = (width//50 + 1)*50 if width % 50 != 0 else width

        return width, port_height

    def set_snap_grid(self, grid_size: int) -> bool:
        """
        set item snap grid size
        :param grid_size: snap grid size
        :return: True for success, False for fail
        """
        if type(grid_size) is not int or grid_size <= 0:
            return False
        else:
            self.__snap_gird_interval = grid_size
            return True

    def set_interactive(self, state: bool):
        """
        set the item to be interactive
        :param state: state
        :return: no return
        """
        interact_flag = Qt.TextInteractionFlag.TextSelectableByKeyboard | Qt.TextInteractionFlag.TextEditable
        self.setFlag(self.GraphicsItemFlag.ItemIsSelectable, state)
        self.setFlag(self.GraphicsItemFlag.ItemIsMovable, state)
        self.ui_title_class.setTextInteractionFlags(interact_flag if state else Qt.TextInteractionFlag.NoTextInteraction)
        self.__flag_interactive = state

    def paint(self, painter, QPainter=None, *args, **kwargs):
        # background
        path_background = QPainterPath()
        path_background.addRoundedRect(0, 0, self.ui_rect_width, self.ui_rect_height, self.ui_rect_radius, self.ui_rect_radius)
        painter.setBrush(QBrush(self.body_background_color))
        painter.drawPath(path_background.simplified())

        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.FillRule.WindingFill)
        path_title.addRoundedRect(0, 0, self.ui_rect_width, self.ui_title_height, self.ui_rect_radius, self.ui_rect_radius)
        path_title.addRect(0, self.ui_rect_radius, self.ui_rect_width, self.ui_title_height - self.ui_rect_radius)
        brush_title = QBrush(self.ui_tite_background_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(brush_title)
        painter.drawPath(path_title.simplified())

        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.ui_rect_width, self.ui_rect_height, self.ui_rect_radius, self.ui_rect_radius)
        pen = QPen(self.ui_outline_color_selected, self.ui_outline_width) if self.isSelected() \
            else QPen(self.ui_outline_color, self.ui_outline_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path_outline.simplified())

    def boundingRect(self):
        return QRectF(0, 0, self.ui_rect_width, self.ui_rect_height).normalized()

    def mousePressEvent(self, event):
        if not self.__flag_interactive:
            super().mousePressEvent(event)
            return

        if event.button() == Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            self.__snap_x = event.pos().x()
            self.__snap_y = event.pos().y()
            self.__link_x = self.pos().x()
            self.__link_y = self.pos().y()

    def mouseMoveEvent(self, event):
        if not self.__flag_interactive:
            super().mouseMoveEvent(event)
            return

        block_size = self.__snap_gird_interval

        '''
        map graphics view position to moved scene position
        
        graphics view position:       moved scene position
                  ^                          ^
                  |                          |
                  |                   -------+------------->
        ----------+---------->               |
                  |                          |
                  |                          |
                  |                          |
        No matter how the scene is moved, current scene position take the center of
        the graphics view as the original point(0,0)
        '''
        x = event.scenePos().x() + self.scene().parent().scene_offset_x
        y = event.scenePos().y() + self.scene().parent().scene_offset_y

        # calculate the snap position and remap to the current scene position
        x = round((x - self.__snap_x) // block_size) * block_size - self.scene().parent().scene_offset_x
        y = round((y - self.__snap_y) // block_size) * block_size - self.scene().parent().scene_offset_y
        pos = QPointF(x, y)
        self.setPos(pos)

        offset_x = x - self.__link_x
        offset_y = y - self.__link_y
        for port in self.ui_oport_node:
            for link in port.link():
                link.set_start_point(link.start_point()[0]+offset_x, link.start_point()[1]+offset_y)
        for port in self.ui_iport_node:
            for link in port.link():
                link.set_end_point(link.end_point()[0] + offset_x, link.end_point()[1] + offset_y)

        self.__link_x = x
        self.__link_y = y
