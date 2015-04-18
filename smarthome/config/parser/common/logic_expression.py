# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import re

from smarthome.architecture.object.logic_expression import LogicExpression
from smarthome.architecture.object.pointer import ObjectPointer, PropertyPointer, PropertyPointerList

logger = logging.getLogger(__name__)
logic_expression_property_regexp = "(?P<object>[a-zA-Z0-9_\[\].]+)\.(?P<property>[a-zA-Z0-9_]+)"

__all__ = [b"parse_logic_expression"]


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


def parse_logic_expression(expression):
    properties_involved = []

    def python_property_expression(match):
        properties_involved.append(PropertyPointer(ObjectPointer(match.group("object")), match.group("property")))
        return "objects[\"%s\"].get_property(\"%s\")" % (match.group("object"), match.group("property"))

    expression = re.sub(logic_expression_property_regexp, python_property_expression, expression)

    code = compile(expression + "\n", "<config>", "eval")
    return LogicExpression(expression=lambda object_manager, **kwargs: eval(code, {"objects": object_manager.objects},
                                                                            kwargs),
                           properties_involved=PropertyPointerList(properties_involved))
