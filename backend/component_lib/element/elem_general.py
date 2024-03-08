_category = "general_method"


class ElemConstant(object):
    def __init__(self):
        self.value = 0
        self.param_list = ["value"]

    def set_param(self, name: str, value) -> bool:
        if type(name) is not str:
            return False
        elif name == "value":
            self.value = value
            return True
        else:
            return False

    def ht(self):
        print("this is a test from ElemConstant")


class ElemDivider(object):
    def __init__(self):
        pass


class ElemAdder2(object):
    def __init__(self):
        pass


class ElemAdder3(object):
    def __init__(self):
        pass