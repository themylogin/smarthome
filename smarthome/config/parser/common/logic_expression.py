# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import __builtin__
import logging
import os
import re

from smarthome.architecture.object.logic_expression import LogicExpression
from smarthome.architecture.object.pointer import ObjectPointer, PropertyPointer, PropertyPointerList
from smarthome.common import DATA_DIR

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
    properties_involved = [PropertyPointer(ObjectPointer(object), property)
                           for (object, property) in re.findall(logic_expression_property_regexp, expression)]

    code = compile(expression + "\n", "<config>", "eval")
    return LogicExpression(expression=lambda container, **kwargs: eval(code, {},
                                                                       LogicExpressionContext(container, dict(
                                                                           dict(os=os,
                                                                                DATA_DIR=DATA_DIR,
                                                                                **__builtin__.__dict__),
                                                                           **kwargs
                                                                       ))),
                           properties_involved=PropertyPointerList(properties_involved))


class LogicExpressionContext(object):
    def __init__(self, container, kwargs):
        self.container = container
        self.kwargs = kwargs

    def __getitem__(self, item):
        if item in self.kwargs:
            return self.kwargs[item]

        return LogicExpressionObjectProxy(self.container, item)


class LogicExpressionObjectProxy(object):
    def __init__(self, container, name):
        self.container = container
        self.name = name

    def __getattr__(self, item):
        return self.container.object_manager.objects[self.name].get_property(item)
