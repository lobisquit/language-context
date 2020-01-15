"""
Small module for generating cson structures from python objects

from https://codereview.stackexchange.com/questions/229336/creating-a-cson-generator-in-python
"""

__all__ = [
    "compile_cson"
]

import re

# Regex to check if a string complies with a variable name
VAR_NAME = re.compile("^[A-Za-z_$][A-Za-z_0-9$]*$")


class NoKey:
    """
    Type to indicate the absence of a key
    in a cson object eg. inside arrays
    """
    pass


# Mapping for correction to match
# python types to cson objects
type_aberrations = {
    float("nan"): "Nan",
    float("inf"): "Infinity",
    float("-inf"): "-Infinity",
    None: "null",
    False: "false",
    True: "true"
}


def dump_cson(obj,
              lines=None,
              key=NoKey,
              indent=2,
              indent_level=0,
              converter=lambda x: x):
    """
    Recursive function that traverses a tree of objects
    and converts them to lines of a cson file
    """
    if not lines:
        lines = []

    # allow user defined decoding function to convert custom types
    # into primitive types
    obj = converter(obj)

    if not key == NoKey:
        if key in type_aberrations:
            key = type_aberrations[key]
        # converts key into a string and handle the case where
        # it doesn't need quotes
        # this could be skipped for string keys but looks so much prettier
        key_str = str(converter(key))
        if type(key) in (float, int) or VAR_NAME.match(key_str):
            key = f"{converter(key_str)}: "

        # key must have quotes because it contains
        # bad characters that must be escaped
        else:
            key = f"{repr(converter(key_str))}: "
    else:
        # there's no, replace with empty string
        key = ""

    whtspace = " " * indent_level

    # handles numbers and truth value types
    if type(obj) in (int, float, bool) or obj == None:
        # match python's and cson types
        obj = type_aberrations.get(obj, obj)
        lines.append(f"{whtspace}{key}{obj}")

    # handles strings conversion
    elif isinstance(obj, str):
        obj = repr(obj)
        lines.append(f"{whtspace}{key}{obj}")

    # handle lists and tuples conversion to array
    elif isinstance(obj, (tuple, list)):
        lines.append(f"{whtspace}{key}[")

        # recursively dump list's content
        for obj in obj:
            dump_cson(obj,
                      lines,
                      NoKey,
                      indent,
                      indent_level + indent,
                      converter)
        lines.append(f"{whtspace}]")

    # handle dict to object conversion
    elif isinstance(obj, dict):
        # if we have a key, dont use curly braces for dicts
        # the single colon looks better and more readable
        if key:
            lines.append(f"{whtspace}{key}")

        # we have no key, it must use curky braces notation
        else:
            lines.append(whtspace + "{")

        # recursively dump dict's contents with
        for dkey, obj in obj.items():
            dump_cson(obj,
                      lines,
                      dkey,
                      indent,
                      indent_level + indent,
                      converter)

        if not key:
            lines.append(whtspace + "}")

    else:
        raise ValueError(f"type {obj} unsupported, you may use a converter function"
                         f" to convert it to a primitive datatype.")
    return lines


def compile_cson(obj, indent=2, converter=lambda x: x):
    return "\n".join(dump_cson(obj, indent=indent, converter=converter))


if __name__ == "__main__":
    # build random objects tree for test
    import random

    stuff = ["abc", "123abc", 123, 1.2, 32, "chars+--/",
             "variable_name", None, False, True]

    length_threshold = 2
    list_n = 5
    dict_n = 5


    def pick_thing():
        return random.choice(stuff)


    def build_list(max_depth):
        k = length_threshold / list_n
        return [build_random_tree(k, max_depth) for _ in range(list_n)]


    def build_dict(max_depth):
        k = length_threshold / list_n
        dict = {}
        for i in range(dict_n):
            dict[pick_thing()] = build_random_tree(k, max_depth)
        return dict


    def build_random_tree(threshold=2, max_depth=5):
        if random.random() < threshold and max_depth >= 0:
            return random.choice((build_dict, build_list))(max_depth - 1)
        else:
            return pick_thing()


    obj = build_random_tree()

    print(compile_cson(obj, indents=2))
