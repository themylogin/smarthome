# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.config.parser.common.procedure import eval_procedure

logger = logging.getLogger(__name__)

__all__ = [b"setup_routines"]


def setup_routines(config, container):
    for routine_xml in config.xpath("/smarthome/routines/*"):
        setup_routine(container, routine_xml)


def setup_routine(container, routine_xml):
    container.routine_manager.add_routine(routine_xml.tag, lambda: eval_procedure(container, routine_xml.getchildren()))
