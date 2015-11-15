# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.server.hotkey.provider.base import BaseHotkeyProvider

logger = logging.getLogger(__name__)

__all__ = [b"NoneHotkeyProvider"]


class NoneHotkeyProvider(BaseHotkeyProvider):
    def bind(self, hotkey, func):
        pass

    def unbind(self, hotkey):
        pass
