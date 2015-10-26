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
    had_if = False
    eval_next_else = False
    for command in procedure:
        logger.debug("Evaluating %s", etree.tostring(command).strip())

        if command.tag == "else":
            if not had_if:
                raise ValueError("Else witout preceding if")

            if eval_next_else:
                eval_procedure(container, command.getchildren())
            else:
                logger.debug("Skipping this else because if condition was True")

            continue

        had_if = False
        eval_next_else = False

        if command.tag == "if":
            had_if = True
            condition = parse_logic_expression(command.get("condition")).expression(container)
            logger.debug("Condition value: %r", condition)
            if condition:
                eval_procedure(container, command.getchildren())
            else:
                eval_next_else = True

        elif command.tag == "call":
            if command.get("method"):
                object, method = command.get("method").split(".")
                meth = getattr(container.object_manager.objects[object], method)
                result = meth(**{k: parse_logic_expression(v).expression(container)
                                 for k, v in command.attrib.iteritems()
                                 if k not in ("method",)})

                if command.getchildren():
                    if not isinstance(result, Promise):
                        raise ValueError("Command has children but did not returned a Promise")

                    for child in command.getchildren():
                        getattr(result, "on_%s" % child.tag)(functools.partial(eval_procedure, container,
                                                                               child.getchildren()))

            elif command.get("routine"):
                container.routine_manager.call_routine(command.get("routine"))

        elif command.tag == "set":
            object, property = command.get("property").split(".")
            expression = parse_logic_expression(command.get("value"))
            container.object_manager.objects[object].set_property(property,
                                                                  expression.expression(container))

        elif command.tag == "async":
            container.worker_pool.run_task(functools.partial(eval_procedure, container, command.getchildren()))

        elif command.tag == "connect_pad":
            dst_object = container.object_manager.objects[command.get("dst_object")]
            dst_object.connect_to_pad(command.get("dst_pad"), command.get("src_object"), command.get("src_pad"))

        elif command.tag == "disconnect_pad":
            dst_object = container.object_manager.objects[command.get("dst_object")]
            dst_object.disconnect_from_pad(command.get("dst_pad"), command.get("src_object"), command.get("src_pad"))

        elif command.tag == "toggle_pad_connection":
            dst_object = container.object_manager.objects[command.get("dst_object")]
            dst_pad = command.get("dst_pad")
            if len(dst_object.dump_incoming_pad_connections().get(dst_pad, [])) == 0:
                dst_object.connect_to_pad(dst_pad, command.get("src_object"), command.get("src_pad"))
            else:
                dst_object.disconnect_all_from_pad(dst_pad)

        elif command.tag == "disconnect_all_from_pad":
            dst_object = container.object_manager.objects[command.get("dst_object")]
            dst_object.disconnect_all_from_pad(command.get("dst_pad"))

        else:
            raise ValueError("Unknown command: %s" % command.tag)
