from backend.general_method.method_json import Json
import sys
import os


__all__ = ["lib_get_comp_list", "lib_get_elem_info",
           "lib_get_elem_method", "lib_get_elem_description", "lib_get_elem_iport", "lib_get_elem_oport"]


_component_lib_path = os.path.join(os.getcwd(), "backend/component_lib")
_component_list_path = os.path.join(_component_lib_path, "lib_list.json")
_element_lib_path = os.path.join(_component_lib_path, "element")


def _get_lib_list():
    lib_list = []
    component_file = Json.load(_component_list_path)
    if Json.has_key(component_file, "element"):
        lib_file = component_file["element"]
        for lib_path in lib_file:
            path = os.path.join(_component_lib_path, lib_path)
            lib_list.append(path)
    return lib_list


def _check_lib_header(lib):
    if Json.check_key_value(lib, "component_type", "element") and \
            Json.check_key_type(lib, "category", str) and \
            Json.check_key_type(lib, "method_source", str) and \
            Json.check_key_type(lib, "component_info", dict):
        return True
    else:
        return False


def _check_elem_property(elem_node):
    if type(elem_node) is not dict:
        return False
    if Json.check_key_type(elem_node, "description", str) and \
            Json.check_key_type(elem_node, "iport", list) and \
            Json.check_key_type(elem_node, "oport", list) and \
            Json.check_key_type(elem_node, "method", str):
        return True
    else:
        return False


def _load_element_list():
    sys.path.append(_element_lib_path)
    elem_list = {}
    lib_list = _get_lib_list()
    for lib_path in lib_list:
        lib = Json.load(lib_path)

        # if library header is valid
        if not _check_lib_header(lib):
            print("invalid")
            continue

        # import method source
        try:
            module = __import__(lib["method_source"])
        except Exception as e:
            print(e)
            continue

        # if element_list doesn't contain the category, init the dict with empty list
        category = lib["category"]
        if category not in elem_list.keys():
            elem_list[category] = {}

        # unpack the component list
        e_list = lib["component_info"]
        for key in e_list.keys():
            elem_node = e_list[key]
            if not _check_elem_property(elem_node):
                continue

            # append component info to component list
            try:
                method = {"name": elem_node["method"]}
                method_class = getattr(module, method["name"])
                method["class"] = method_class
                elem_list[category][key] = elem_node
                elem_list[category][key]["method"] = method
            except Exception as e:
                print(e)
                continue
    return elem_list


def _load_comp_list():
    comp_list = {"Element": _load_element_list()}
    return comp_list


_lib_list = _get_lib_list()
_comp_list = _load_comp_list()


# API

def lib_get_comp_list():
    return _comp_list


def lib_get_elem_info(category: str, elem_type: str):
    try:
        return _comp_list["Element"][category][elem_type]
    except:
        return None


def lib_get_elem_description(category: str, ele_type: str):
    try:
        return _comp_list["Element"][category][ele_type]["description"]
    except:
        return None


def lib_get_elem_iport(category: str, elem_type: str):
    try:
        return _comp_list["Element"][category][elem_type]["iport"]
    except:
        return None


def lib_get_elem_oport(category: str, elem_type: str):
    try:
        return  _comp_list["Element"][category][elem_type]["oport"]
    except:
        return None


def lib_get_elem_method(category: str, elem_type: str):
    try:
        return _comp_list["Element"][category][elem_type]["method"]["class"]
    except:
        return None


