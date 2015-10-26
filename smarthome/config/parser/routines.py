# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import namedtuple
import logging

from smarthome.config.parser.common.procedure import eval_procedure

logger = logging.getLogger(__name__)

__all__ = [b"setup_routines"]

Routine = namedtuple("Routine", ["func", "hotkeys"])


def setup_routines(config, container):
    for routine_xml in config.xpath("/smarthome/routines/*"):
        setup_routine(container, routine_xml)


def setup_routine(container, routine_xml):
    name = routine_xml.tag

    func = lambda: eval_procedure(container, routine_xml.getchildren())

    hotkeys = []
    for hotkey in routine_xml.get("hotkey", "").split(" "):
        local = False
        if hotkey.startswith("(local)"):
            local = True
            hotkey = hotkey[len("(local)"):]

        if not local:
            hotkeys.append(hotkey)

        container.hotkey_manager.bind(hotkey, lambda: container.routine_manager.call_routine(name))

    container.routine_manager.add_routine(name, Routine(func, hotkeys))
