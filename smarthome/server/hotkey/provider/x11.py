# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from gi.repository import GObject, Keybinder

import logging

from smarthome.server.hotkey.provider.base import BaseHotkeyProvider

logger = logging.getLogger(__name__)

__all__ = [b"X11HotkeyProvider"]


class X11HotkeyProvider(BaseHotkeyProvider):
    def __init__(self):
        Keybinder.init()

    def bind(self, hotkey, func):
        GObject.idle_add(self._bind, hotkey, func)

    def _bind(self, hotkey, func):
        gtk_hotkey = self._gtk_hotkey(hotkey)
        bound = Keybinder.bind(gtk_hotkey, lambda *args, **kwargs: func())
        if bound:
            logger.debug("Bound hotkey %r (gtk_hotkey = %r)", hotkey, gtk_hotkey)
        else:
            logger.error("Unable to bind hotkey %r (gtk_hotkey = %r)", hotkey, gtk_hotkey)

    def unbind(self, hotkey):
        GObject.idle_add(self._unbind, hotkey)

    def _unbind(self, hotkey):
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
