# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
from lxml import etree

from smarthome.config.parser.common.logic_expression import parse_logic_expression
from smarthome.config.parser.common.procedure import eval_procedure

logger = logging.getLogger(__name__)

__all__ = [b"setup_ons"]


def setup_ons(config, object_manager):
    for on_xml in config.xpath("/smarthome/on"):
        if on_xml.get("signal"):
            object, signal = on_xml.get("signal").split(".")
            object_manager.connect_object_signal(object, signal, functools.partial(handle_on, object_manager, on_xml))
        else:
            raise ValueError("<on/> should specify signal to bind")


def handle_on(object_manager, on_xml, **kwargs):
    for k, v in kwargs.iteritems():
        if on_xml.get(k):
            w = parse_logic_expression(on_xml.get(k)).expression(object_manager)
            if w != v:
                logger.debug("Skipping %s because %s value %r != %r", etree.tostring(on_xml).strip(), k, w, v)
                return

    eval_procedure(object_manager, on_xml.getchildren())
