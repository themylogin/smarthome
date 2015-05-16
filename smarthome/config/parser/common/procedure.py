# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
from lxml import etree

from smarthome.architecture.deferred import Promise
from smarthome.config.parser.common.logic_expression import parse_logic_expression

logger = logging.getLogger(__name__)

__all__ = [b"eval_procedure"]


def eval_procedure(container, procedure):
    for command in procedure:
        logger.debug("Evaluating %s", etree.tostring(command).strip())

        if command.tag == "call":
            object, method = command.get("method").split(".")
            meth = getattr(container.object_manager.objects[object], method)
            result = meth(**{k: parse_logic_expression(v).expression(container.object_manager)
                             for k, v in command.attrib.iteritems()
                             if k not in ("method",)})

            if command.getchildren():
                if not isinstance(result, Promise):
                    raise ValueError("Command has children but did not returned a Promise")

                for child in command.getchildren():
                    getattr(result, "on_%s" % child.tag)(functools.partial(eval_procedure, container,
                                                                           child.getchildren()))

        elif command.tag == "set":
            object, property = command.get("property").split(".")
            expression = parse_logic_expression(command.get("value"))
            container.object_manager.objects[object].set_property(property,
                                                                  expression.expression(container.object_manager))

        elif command.tag == "async":
            container.worker_pool.run_task(functools.partial(eval_procedure, container, command.getchildren()))

        else:
            raise ValueError("Unknown command: %s" % command.tag)
