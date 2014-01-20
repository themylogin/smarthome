# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import re

logic_expression_property_regexp = "(?P<object>[a-zA-Z0-9_\[\].]+)\.(?P<property>[a-zA-Z0-9_]+)"


def parse_constant(val):
    try:
        return {
            "None": None,
            "True": True,
            "False": False,
            }[val]
    except KeyError:
        pass

    try:
        return int(val)
    except ValueError:
        pass

    return val


def extract_logic_expression_objects(expression):
    objects = []
    for match in re.finditer(logic_expression_property_regexp, expression):
        objects.append(match.group("object"))
    return objects


def parse_logic_expression(expression, dispatcher, properties_involved=None):
    if properties_involved is None:
        properties_involved = []

    def python_property_expression(match):
        try:
            object = dispatcher.objects[match.group("object")]
            property = object.properties.access(match.group("property"))
        except KeyError:
            return match.group(0)

        properties_involved.append(property)
        return "objects[\"%s\"].properties[\"%s\"]" % (match.group("object"), match.group("property"))

    expression = re.sub(logic_expression_property_regexp, python_property_expression, expression)

    code = compile(expression + "\n", "<config>", "eval")
    return lambda **kwargs: eval(code, {"objects": dispatcher.objects}, kwargs)
