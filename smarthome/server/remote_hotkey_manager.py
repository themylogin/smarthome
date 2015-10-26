# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"HotkeyManager"]


class RemoteHotkeyManager(object):
    def __init__(self, container):
        self.container = container
        self.remote_hotkeys = set()

    def on_peers_updated(self):
        for hotkey in self.remote_hotkeys:
            self.container.hotkey_manager.unbind(hotkey)

        self.remote_hotkeys = set()
        for peer in self.container.peer_manager.peers.itervalues():
            for routine_name, routine_desc in peer.possessions["routines"].iteritems():
                for hotkey in routine_desc["hotkeys"]:
                    self.container.hotkey_manager.bind(hotkey, lambda: self.container.routine_manager.call_routine(routine_name))
                    self.remote_hotkeys.add(hotkey)
