# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"RoutineManager"]


class RoutineManager(object):
    def __init__(self, container):
        self.container = container
        self.local_routines = {}

    def add_routine(self, name, routine):
        if name in self.local_routines:
            raise KeyError("Routine %s already exists" % name)

        self.local_routines[name] = routine

    def call_routine(self, name):
        if name in self.local_routines:
            return self.local_routines[name]()

        for peer_name, peer in self.container.peer_manager.peers.iteritems():
            if name in peer.possessions["routines"]:
                with self.container.peer_manager.control_connection(peer_name) as connection:
                    return connection.control("call_routine", {"name": name})

        raise ValueError("Nobody has routine named %s" % name)
