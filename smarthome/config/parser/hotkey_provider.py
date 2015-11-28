# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.server.hotkey.provider.libevdev import LibevdevHotkeyProvider
from smarthome.server.hotkey.provider.none import NoneHotkeyProvider
from smarthome.server.hotkey.provider.x11 import X11HotkeyProvider

logger = logging.getLogger(__name__)

__all__ = [b"get_hotkey_provider"]


def get_hotkey_provider(config):
    hotkey_provider = config.xpath("/smarthome/hotkey_provider")
    if hotkey_provider:
        if hotkey_provider[0].text == "libevdev":
            return LibevdevHotkeyProvider()
        if hotkey_provider[0].text == "x11":
            return X11HotkeyProvider()
    else:
        return NoneHotkeyProvider()
