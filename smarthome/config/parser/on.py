# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging

from smarthome.config.parser.common.procedure import eval_procedure

logger = logging.getLogger(__name__)

__all__ = [b"setup_ons"]


def setup_ons(config, object_manager):
    for on_xml in config.xpath("/smarthome/on"):
        if on_xml.get("signal"):
            object, signal = on_xml.get("signal").split(".")
            object_manager.connect_object_signal(object, signal, functools.partial(eval_procedure, object_manager,
                                                                                   on_xml.getchildren()))
        else:
            raise ValueError("<on/> should specify signal to bind")
