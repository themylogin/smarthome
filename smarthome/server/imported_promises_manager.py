# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = []


class ImportedPromisesManager(object):
    def __init__(self):
        self.deferreds = {}

    def manage(self, uuid, deferred):
        self.deferreds[uuid] = deferred

    def on_deferred_resolve(self, uuid, event, *args, **kwargs):
        if uuid in self.deferreds:
            getattr(self.deferreds[uuid], "resolve_%s" % event)(*args, **kwargs)

    def on_deferred_destroy(self, uuid):
        del self.deferreds[uuid]
