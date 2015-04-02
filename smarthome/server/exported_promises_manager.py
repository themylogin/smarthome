# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging

from themyutils.oop.observable import Observable

logger = logging.getLogger(__name__)

__all__ = []


class ExportedPromisesManager(Observable("exported_promises_observer", ["exported_promise_resolved",
                                                                        "exported_promise_destroyed"])):
    def __init__(self):
        self.deferreds = {}

    def manage(self, uuid, deferred):
        self.deferreds[uuid] = deferred
        deferred.on_destroy(functools.partial(self.destroy, uuid))
        for event in deferred.events:
            getattr(deferred, "on_%s" % event)(functools.partial(self.notify_exported_promise_resolved, uuid, event))

    def destroy(self, uuid):
        if uuid in self.deferreds:
            del self.deferreds[uuid]
            self.notify_exported_promise_destroyed(uuid)
