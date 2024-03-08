__all__ = ["CompBase"]


component_type = {"Element": 0, "Pipeline": 1}


class CompBase(object):
    def __init__(self, comp_type: str):
        if comp_type in component_type.keys():
            self.__comp_type = comp_type
        else:
            self.__comp_type = None

    def component_type(self):
        """
        get component type
        :return: component type string
        """
        return self.__comp_type
