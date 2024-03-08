import json


class Json(object):
    @staticmethod
    def load(file_path: str):
        try:
            with open(file_path, 'r') as f:
                lib = json.load(f)
        except Exception as e:
            print(e)
            return None
        return lib

    @staticmethod
    def has_key(json_node: dict, key: str):
        if type(json_node) is dict and type(key) is str:
            if key in json_node.keys():
                return True
        return False

    @staticmethod
    def check_key_type(json_node: dict, key: str, key_type):
        if not Json.has_key(json_node, key):
            return False
        if type(json_node[key]) is key_type:
            return True
        else:
            return False

    @staticmethod
    def check_key_value(json_node: dict, key: str, key_value):
        if not Json.check_key_type(json_node, key, type(key_value)):
            return False
        if json_node[key] == key_value:
            return True
        else:
            return False