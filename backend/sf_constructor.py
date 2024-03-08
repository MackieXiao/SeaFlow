from backend.component.comp_pipeline import *


__all__ = ["SFConstructor"]


cmd_operator = {
    "=": "assignment",
    "/": "sub-item",
    ".": "sub-value",
    ":": "component port",
    "&": "link"
}


class SFConstructor(object):
    def __init__(self):
        self.__cmd_handler = {
            "POST": self.__post_handler,
            "DELETE": self.__delete_handler
        }
        self.__post_sub_handler = {
            "Pipeline": self.__post_pipeline_handler,
            "Element": self.__post_element_handler,
            "Link": self.__post_link_handler
        }
        self.__delete_sub_handler = {
            "Pipeline": self.__delete_pipeline_handler,
            "Element": self.__delete_element_handler,
            "Link": self.__delete_link_handler
        }
        self.__pipeline = []

    def cmd(self, command: str) -> list:
        """
        handle input command
        :param command: input command
        :return: list with command status and info
        """
        # check type
        if type(command) is not str:
            return [False]

        cmd_list = command.split()
        if len(cmd_list) != 2:
            return [False]
        try:
            return self.__cmd_handler[cmd_list[0]](cmd_list[1])
        except:
            return [False]

    def __post_handler(self, cmd_para: str) -> list:
        """
        handle the command with 'POST' prefix
        :param cmd_para: command parameter
        :return: list with command status and info
        """
        try:
            cmd_para = cmd_para.split("=", 1)
            comp_type = cmd_para[0]
            comp_para = cmd_para[1]
        except:
            return [False]

        try:
            return self.__post_sub_handler[comp_type](comp_para)
        except:
            return [False]

    def __delete_handler(self, cmd_para: str) -> list:
        """
        handler the command with 'DELETE' prefix
        :param cmd_para: command parameter
        :return: list with command status and info
        """
        try:
            cmd_para = cmd_para.split("=", 1)
            comp_type = cmd_para[0]
            comp_para = cmd_para[1]
        except:
            return [False]

        try:
            return self.__delete_sub_handler[comp_type](comp_para)
        except:
            return [False]

    def __delete_pipeline_handler(self, comp_para: str) -> list:
        """
        handle the command with 'DELETE Pipeline' prefix
        example:
        Delete Pipeline=pipeline0
        :param cmd_para: command parameter
        :return: list True for success, False for fail
        """
        print("delete pipeline")
        return [True]

    def __delete_element_handler(self, comp_para: str) -> list:
        """
        handle the command with 'DELETE Element' prefix
        example:
        DELETE Element=pipeline0/constant1
        :param comp_para: command parameter
        :return: list True for success, False for fail
        """
        # extract all the info
        comp_para = comp_para.split("/")
        if len(comp_para) != 2:
            return [False]
        pipeline = self.__get_pipeline(comp_para[0])
        elem = comp_para[1]
        if pipeline is None:
            return [False]
        return [pipeline.delete_element(elem)]

    def __delete_link_handler(self, comp_para: str) -> list:
        """
        delete a link from pipeline
        :param comp_para: command parameter
        :return: list True for success, False for fail
        """
        # extract all the info
        comp_para = comp_para.split("&")
        if len(comp_para) != 2:
            return [False]
        comp_o = comp_para[0].split(":")
        comp_i = comp_para[1].split(":")
        if len(comp_o) != 2 or len(comp_i) != 2:
            return [False]
        oport = comp_o[1]
        iport = comp_i[1]
        comp_o = comp_o[0].split("/")
        comp_i = comp_i[0].split("/")
        if len(comp_o) != 2 or len(comp_i) != 2:
            return [False]
        pl_o = self.__get_pipeline(comp_o[0])
        pl_i = self.__get_pipeline(comp_i[0])
        elem_o = comp_o[1]
        elem_i = comp_i[1]

        # make sure all pipelines are valid
        if pl_o is None or pl_i is None:
            return [False]
        elif pl_o == pl_i:
            return [pl_o.delete_link(elem_o, oport, elem_i, iport)]
        else:
            return [False]

    def __post_pipeline_handler(self, comp_para: str) -> list:
        """
        handle the command with 'POST Pipeline' prefix
        example:
        POST Pipeline=pipeline0
        :param comp_para: component parameter
        :return: list True for success, False for fail
        """
        if self.__has_cmd_operator(comp_para):
            return [False]
        else:
            return [self.__post_pipeline(comp_para)]

    def __post_element_handler(self, comp_para: str) -> list:
        """
        handle the command with 'POST Element' prefix
        example:
        POST Element=pipeline0/general.constant/constant0
        :param comp_para: component parameter
        :return: list True for success, False for fail
        """
        # extract all the info
        comp_para = comp_para.split("/")
        if len(comp_para) != 3 or len(comp_para[1].split(".")) != 2:
            return [False]
        pl = comp_para[0]
        elem = comp_para[1].split(".")
        elem_category = elem[0]
        elem_type = elem[1]
        name = comp_para[2]

        # make sure each name is not contain any cmd operator
        # make sure the pipeline has been post in the constructor
        if self.__has_cmd_operator(pl) or self.__has_cmd_operator(elem_category) or \
           self.__has_cmd_operator(elem_type) or self.__has_cmd_operator(name) or \
           self.__get_pipeline(pl) is None:
            return [False]

        pl = self.__get_pipeline(pl)
        return [None is not pl.post_element(name, elem_category, elem_type)]

    def __post_link_handler(self, comp_para: str) -> list:
        """
        handle the command with 'POST Link' prefix
        example:
        POST Link=pipeline0/elem1:oport&pipeline0/elem2:iport
        :param comp_para: component parameter
        :return: list True for success, False for fail
        """
        # extract all the info
        comp_para = comp_para.split("&")
        if len(comp_para) != 2:
            return [False]
        comp_o = comp_para[0].split(":")
        comp_i = comp_para[1].split(":")
        if len(comp_o) != 2 or len(comp_i) != 2:
            return [False]
        oport = comp_o[1]
        iport = comp_i[1]
        comp_o = comp_o[0].split("/")
        comp_i = comp_i[0].split("/")
        if len(comp_o) != 2 or len(comp_i) != 2:
            return [False]
        pl_o = self.__get_pipeline(comp_o[0])
        pl_i = self.__get_pipeline(comp_i[0])
        elem_o = comp_o[1]
        elem_i = comp_i[1]
        link = [elem_o, oport, elem_i, iport]

        # make sure all pipelines are valid
        if pl_o is None or pl_i is None:
            return [False]
        elif pl_o == pl_i:
            return [pl_o.post_link(elem_o, oport, elem_i, iport)]
        else:
            return [False]

    @staticmethod
    def __has_cmd_operator(command: str):
        """
        check if the command contains the cmd operator
        :param command: input command
        :return: True for existed, False for not found
        """
        for c in cmd_operator.keys():
            if c in command:
                return True
        return False

    def __get_pipeline(self, name: str) -> CompPipeline:
        """
        get ane pipeline class
        :param name: pipeline name
        :return: pipeline class, None for not found
        """
        if type(name) is not str:
            return None
        for pl in self.__pipeline:
            if pl.name() == name:
                return pl
        return None

    def __post_pipeline(self, name: str):
        """
        post a pipeline to constructor
        :param name: pipeline name
        :return: True for success, False for fail
        """
        if self.__get_pipeline(name)is not None:
            return False
        pl = CompPipeline(name)
        self.__pipeline.append(pl)
        return True

    def post_pipeline(self, name: str) -> list:
        """
        post a pipeline to the constructor
        :param name: pipeline name
        :return: command result, None for fail
        """
        cmd = "POST Pipeline=" + name
        if type(name) is not str:
            return None
        else:
            return self.cmd(cmd)[0]

