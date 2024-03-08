from .comp_base import *
from .lib_loader import *


__all__ = ["CompElement"]


class CompElement(CompBase):
    def __init__(self, parent, name: str, category: str, elem_type: str):
        super().__init__("Element")
        self.__parent = parent  # pointer to the parent container
        self.__name = name  # element name
        self.__category: str = ""  # element category
        self.__type: str = ""  # element type
        self.__description: str = ""  # element description
        self.__iport: list = []  # input port
        self.__oport: list = []  # output port
        self.__method = None  # user defined method
        self.__valid = self.set_type(category, elem_type)

    def set_name(self, name: str) -> bool:
        """
        set element name
        :param name: element name
        :return: True for success, False for fail
        """
        if type(name) is not str:
            return False
        self.__name = name
        return True

    def set_type(self, category: str, elem_type: str) -> bool:
        """
        set element type
        :param category: element category
        :param elem_type: element type
        :return: True for success, False for fail
        """
        # make sure element type is included in lib
        info = lib_get_elem_info(category, elem_type)
        if info is None:
            return False

        # get element property
        description = lib_get_elem_description(category, elem_type)
        iport = lib_get_elem_iport(category, elem_type)
        oport = lib_get_elem_oport(category, elem_type)
        method = lib_get_elem_method(category, elem_type)
        if description is None or \
                iport is None or oport is None or \
                method is None:
            return False

        self.__category = category
        self.__type = elem_type
        self.__description = description
        self.__iport = iport
        self.__oport = oport
        self.__method = method
        self.__valid = True
        return True

    def name(self) -> str:
        """
        get the element name
        :return: element name
        """
        return self.__name

    def category(self) -> str:
        """
        get element category
        :return: element category
        """
        return self.__category

    def elem_type(self) -> str:
        """
        get element type
        :return: element type
        """
        return self.__type

    def iport(self) -> list:
        """
        get element input port
        :return: list of input port
        """
        return self.__iport

    def oport(self) -> list:
        """
        get element output port
        :return: list of output port
        """
        return self.__oport

    def is_valid(self) -> bool:
        """
        check if the element class is valid for use
        :return: True for valid, False for invalid
        """
        return self.__valid

    def has_iport(self, iport: str) -> bool:
        """
        check if the element has iport
        :param iport: iport name
        :return: True for existed, False for not found
        """
        return True if iport in self.__iport else False

    def has_oport(self, oport: str) -> bool:
        """
        check if the element has oport
        :param oport: oport name
        :return: True for existed, False for not found
        """
        return True if oport in self.__oport else False
