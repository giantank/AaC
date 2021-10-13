import os
import yaml
from aac import parser

primitives = []
root_names = []
aac_model = {}


def search(model, input_keys):
    """
    Searches a dict for the contents given a set of keys. Search returns a list of
    the entries in the model that correcpond to those keys.  This search will
    traverse the full dict tree, including embeded lists.
    """
    # print("searching for keys: {}",format(keys))
    keys = input_keys.copy()
    if len(keys) == 0:
        print("search error - empty keys")
        return []
    search_key = keys.pop(0)
    final_key = len(keys) == 0
    if not isinstance(model, dict):
        print("search error - model is not a dict")
        return []
    else:
        if search_key in model:
            model_value = model[search_key]
            if final_key:
                if isinstance(model_value, list):
                    return model_value
                else:
                    retVal = []
                    retVal.append(model_value)
                    return retVal

            if isinstance(model_value, dict):
                return search(model[search_key], keys)
            elif isinstance(model_value, list):
                retVal = []
                for model_item in model_value:
                    # print(model_item)
                    if isinstance(model_item, dict):
                        retVal.extend(search(model_item, keys))
                    else:
                        print("serach error - lists can only contain dicts")
                return retVal
            else:
                print(f"search warning - keys[{input_keys}] not found in model")
                return []
        else:
            # not an error, just zero search results
            return []


def getAaCSpec():
    """
    Gets the specification for Architecture-as-Code iteself.  The AaC model specification is
    defined as an AaC model and is needed for model validation.
    """

    global aac_model
    if len(aac_model.keys()) > 0:
        # already parsed, just return cached values
        aac_data = getModelsByType(aac_model, "data")
        aac_enums = getModelsByType(aac_model, "enum")
        return aac_data, aac_enums

    # get the AaC.yaml spec for architecture modeling
    this_file_path = os.path.dirname(os.path.realpath(__file__))
    relpath_to_aac_yaml = "../../model/aac/AaC.yaml"
    aac_model_file = os.path.join(this_file_path, relpath_to_aac_yaml)

    aac_model = parser.parseFile(aac_model_file, False)
    aac_data = getModelsByType(aac_model, "data")
    aac_enums = getModelsByType(aac_model, "enum")

    return aac_data, aac_enums


def getAacSpecAsYaml() -> str:
    global aac_model
    aac_yaml = ""
    isFirst = True
    for aac_name in aac_model.keys():
        # put in the separator for all but the first
        if isFirst:
            isFirst = False
        else:
            aac_yaml = aac_yaml + "---\n"

        aac_yaml = aac_yaml + yaml.dump(aac_model[aac_name]) + "\n"
    return aac_yaml


def extendAaCSpec(parsed_model):
    global aac_model
    apply_me = parsed_model.copy()
    exts = getModelsByType(apply_me, "ext")
    for ext_type in exts.keys():
        del apply_me[ext_type]
    aac_model = aac_model | apply_me


def getPrimitives(reload=False):
    """
    Gets the list of primitives as defined in the Arch-As-Code spec.
    """

    global primitives

    if len(primitives) == 0 or reload:
        aac_data, aac_enums = getAaCSpec()
        primitives = search(aac_enums["Primitives"], ["enum", "values"])

    return primitives


def getRoots(reload=False):
    """
    Gets the list of defined model roots as defined in the Arch-As-Code spec.
    """

    global root_names

    if len(root_names) == 0 or reload:
        aac_data, aac_enums = getAaCSpec()
        root_names = search(aac_data["root"], ["data", "fields", "name"])

    return root_names


def getModelsByType(models, type_name):
    ret_val = {}
    for key, value in models.items():
        if type_name in value.keys():
            ret_val[key] = value

    return ret_val