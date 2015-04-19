# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.config.parser.common.logic_expression import parse_logic_expression

logger = logging.getLogger(__name__)

__all__ = [b"eval_procedure"]


def eval_procedure(object_manager, procedure, *args, **kwargs):
    for command in procedure:
        if command.tag == "call":
            object, method = command.get("method").split(".")
            getattr(object_manager.objects[object], method)()

        elif command.tag == "set":
            object, property = command.get("property").split(".")
            expression = parse_logic_expression(command.get("value"))
            object_manager.objects[object].set_property(property, expression.expression(object_manager))

        else:
            raise ValueError("Unknown command: %s" % command.tag)
