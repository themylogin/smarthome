# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"BaseHotkeyProvider"]


class BaseHotkeyProvider(object):
    def bind(self, hotkey, func):
        raise NotImplementedError

    def unbind(self, hotkey):
        raise NotImplementedError
