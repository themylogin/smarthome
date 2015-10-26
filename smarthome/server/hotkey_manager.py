# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from gi.repository import Keybinder
import logging

logger = logging.getLogger(__name__)

__all__ = [b"HotkeyManager"]


class HotkeyManager(object):
    def __init__(self, container):
        self.container = container

        Keybinder.init()

    def bind(self, hotkey, func):
        gtk_hotkey = self._gtk_hotkey(hotkey)
        bound = Keybinder.bind(gtk_hotkey, lambda *args: self._execute_hotkey(hotkey, func))
        if bound:
            logger.debug("Bound hotkey %r (gtk_hotkey = %r)", hotkey, gtk_hotkey)
        else:
            logger.error("Unable to bind hotkey %r (gtk_hotkey = %r)", hotkey, gtk_hotkey)

    def unbind(self, hotkey):
        Keybinder.unbind(self._gtk_hotkey(hotkey))

    def _gtk_hotkey(self, hotkey):
        modifiers = hotkey.split("-")
        key = modifiers.pop()

        gtk_modifiers = []
        for modifier in modifiers:
            map = {"A": "Alt",
                   "C": "Ctrl",
                   "S": "Shift",
                   "W": "Super"}
            if modifier in map:
                gtk_modifiers.append("<%s>" % map[modifier])
            else:
                raise ValueError("Unknown modifier %r while processing hotkey %r" % (modifier, hotkey))

        return "".join(gtk_modifiers + [key])

    def _execute_hotkey(self, hotkey, func):
        logger.debug("Got hotkey: %s", hotkey)
        self.container.worker_pool.run_task(func)
