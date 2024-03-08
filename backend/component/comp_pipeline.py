from backend.component.comp_base import *
from backend.component.comp_element import *


class CompPipeline(CompBase):
    def __init__(self, name: str):
        super().__init__("Pipeline")
        self.__name = name
        self.__element = []
        self.__link = []

    def post_element(self, name: str, category: str, elem_type: str) -> CompElement:
        """
        post and element to the pipeline
        :param name: element name
        :param category: element category
        :param elem_type: element type
        :return: element class for success, None for fail
        """
        if self.get_element(name) is not None:
            return None
        elem = CompElement(self, name, category, elem_type)
        if elem.is_valid():
            self.__element.append(elem)
            return elem
        return None

    def delete_element(self, name: str) -> bool:
        """
        delete an element from pipeline
        :param name: element name
        :return: True for success, False for fail
        """
        elem = self.get_element(name)
        if elem is None:
            return False
        # make sure to clean all the linkage of the element before delete it
        link = []
        for l in self.__link:
            if l[0].name() == elem.name() or l[2].name() == elem.name():
                link.append(l)
        for l in link:
            self.__link.remove(l)
        self.__element.remove(elem)
        return True

    def post_link(self, elem_o: str, oport: str, elem_i: str, iport: str) -> bool:
        """
        post a link to pipeline
        :param elem_o: output element name
        :param oport: output port name
        :param elem_i: input element name
        :param iport: input port name
        :return: True for success, False for fail
        """
        node_o = self.get_element(elem_o)
        node_i = self.get_element(elem_i)
        if node_o is None or node_i is None or not node_o.has_oport(oport) or not node_i.has_iport(iport) or self.has_link(elem_o, oport, elem_i, iport):
            return False
        self.__link.append([node_o, oport, node_i, iport])
        return True

    def delete_link(self, elem_o: str, oport: str, elem_i: str, iport: str) -> bool:
        """
        delete a link from pipeline
        :param elem_o: output element name
        :param oport: output port name
        :param elem_i: input element name
        :param iport: input port name
        :return: True for success, False for fail
        """
        node_o = self.get_element(elem_o)
        node_i = self.get_element(elem_i)
        if type(oport) is not str or type(iport) is not str or \
           node_o is None or node_i is None:
            return False
        link = [node_o, oport, node_i, iport]
        for l in self.__link:
            if l == link:
                self.__link.remove(l)
                return True
        return False



    def get_element(self, name: str) -> CompElement:
        """
        get an element class
        :param name: element name
        :return: element class, None for no found
        """
        if type(name) is not str:
            return None
        for e in self.__element:
            if e.name() == name:
                return e
        return None

    def has_link(self, elem_o, oport, elem_i, iport):
        """
        check if the pipeline has link
        :param elem_o: output element
        :param oport: output port
        :param elem_i: input element
        :param iport: input port
        :return: True for existed, False for not found
        """
        link = [elem_o, oport, elem_i, iport]
        for l in self.__link:
            l = [l[0].name(), l[1], l[2].name(), l[3]]
            if link == l:
                return True
        return False

    def name(self) -> str:
        """
        get the pipeline name
        :return: pipeline name
        """
        return self.__name
