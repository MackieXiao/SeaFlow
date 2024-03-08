from .comp_browser_scene import *
from .node_item import *
from backend.component.lib_loader import *


__all__ = ['UiCompBrowserView']


class UiCompBrowserView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__scene = UiCompBrowserScene(self)
        self.__setup_ui()

    def __setup_ui(self):
        """
        setup ui
        :return: no return
        """
        self.setScene(self.__scene)
        self.setFrameShape(self.Shape.NoFrame)
        self.setFrameShadow(self.Shadow.Plain)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setRenderHints(QPainter.RenderHint.Antialiasing | QPainter.RenderHint.TextAntialiasing | QPainter.RenderHint.SmoothPixmapTransform)

    @pyqtSlot(QItemSelection)
    def slot_show_item(self, selected: QItemSelection):
        """
        This is a slot function that connected to component browser treeview selection change event.
        After the selection is changed, the view will show up the preview of the selected component.
        :param selected: QItemSelection info
        :return: no return
        """
        for i in selected.indexes():
            category = i.parent().data()
            elem_type = i.data()
            info = lib_get_elem_info(category, elem_type)
            if info is None:
                return

            item = UiElementItem(elem_type, category, elem_type)
            view_width = self.width()
            view_height = self.height()
            factor_width = (view_width-24)/item.ui_full_width
            factor_height = (view_height-24)/item.ui_full_height
            scale_factor = min(factor_width, factor_height)
            self.scene().setSceneRect(-500, -500, 1000, 1000)
            self.scene().update()
            self.setTransform(QTransform())
            item.setScale(scale_factor)
            self.scene().clear()
            self.scene().addItem(item)
            item.setPos((view_width-scale_factor*item.ui_rect_width)/2, (view_height-scale_factor*item.ui_full_height)/2)
