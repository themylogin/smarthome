# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
from lxml import etree

from smarthome.config.parser.common.logic_expression import parse_logic_expression
from smarthome.config.parser.common.procedure import eval_procedure

logger = logging.getLogger(__name__)

__all__ = [b"setup_ons"]


def setup_ons(config, container):
    for on_xml in config.xpath("/smarthome/on"):
        if on_xml.get("signal"):
            object, signal = on_xml.get("signal").split(".")
            container.object_manager.connect_object_signal(object, signal,
                                                           functools.partial(handle_signal, container, on_xml))
        elif on_xml.get("expression") or on_xml.get("property"):
            expression = parse_logic_expression(on_xml.get("expression") or on_xml.get("property"))
            observer = create_expression_change_observer(container, on_xml, expression, {})
            for property_pointer in expression.properties_involved:
                container.object_manager.add_object_property_change_observer(property_pointer.object_pointer.name,
                                                                             property_pointer.name,
                                                                             observer)
        else:
            raise ValueError("<on/> should specify signal or property to bind")


def handle_signal(container, on_xml, **kwargs):
    for k, v in kwargs.iteritems():
        if on_xml.get(k):
            w = parse_logic_expression(on_xml.get(k)).expression(container)
            if w != v:
                logger.debug("Skipping %s because %s value %r != %r", etree.tostring(on_xml).strip(), k, w, v)
                return

    eval_procedure(container, on_xml.getchildren())


def create_expression_change_observer(container, on_xml, expression, context):
    def observer(old_value, new_value):
        new_expression_value = expression.expression(container)
        run = True

        if on_xml.get("value") is not None:
            run = run and (parse_logic_expression(on_xml.get("value")).expression(container) == new_expression_value)

        if on_xml.get("old_value") is not None and "value" in context:
            run = run and (parse_logic_expression(on_xml.get("old_value")).expression(container) == context["value"])

        context["value"] = new_expression_value

        if run:
            eval_procedure(container, on_xml.getchildren(), expression_value=new_expression_value)

    return observer
