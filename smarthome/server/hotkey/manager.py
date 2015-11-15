# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from gi.repository import Keybinder
import logging

logger = logging.getLogger(__name__)

__all__ = [b"HotkeyManager"]


class HotkeyManager(object):
    def __init__(self, container, provider):
        self.container = container
        self.provider = provider

    def bind(self, hotkey, func):
        logger.debug("Binding hotkey %r", hotkey)
        self.provider.bind(hotkey, lambda: self._execute_hotkey(hotkey, func))

    def unbind(self, hotkey):
        self.provider.unbind(hotkey)

    def _execute_hotkey(self, hotkey, func):
        logger.debug("Got hotkey: %s", hotkey)
        self.container.worker_pool.run_task(func)
