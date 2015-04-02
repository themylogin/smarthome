# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import functools

from smarthome.architecture.object.proxy import LocalObject

logger = logging.getLogger(__name__)

__all__ = []


class EventTransceiver(object):
    def __init__(self, web_server, object_manager, imported_promises_manager, exported_promises_manager):
        self.web_server = web_server
        self.object_manager = object_manager
        self.imported_promises_manager = imported_promises_manager
        self.exported_promises_manager = exported_promises_manager

    def __getattr__(self, name):
        if name.startswith("on_"):
            return functools.partial(self._be_observer, name[len("on_"):])

        raise AttributeError(name)

    def _be_observer(self, event, *args):
        args = list(args)

        if event in ["object_property_changed", "object_pad_connected", "object_pad_disconnected"]:
            if not isinstance(args[0], LocalObject):
                return

        if event == "object_property_changed":
            args[0] = args[0]._name

        logger.debug("Notifying everybody of event %s: %r", event, args)
        self.web_server.notify_my_event(event, args)

    def receive_remote_event(self, event, args):
        logger.debug("Received remote event %s: %r", event, args)

        if event == "exported_promise_resolved":
            self.imported_promises_manager.on_deferred_resolve(args[0], args[1], *args[2], **args[3])

        if event == "exported_promise_destroyed":
            self.imported_promises_manager.on_deferred_destroy(args[0])

        if event == "object_signal_emitted":
            self.object_manager.on_object_signal_emitted(args[0], args[1], *args[2], **args[3])

        if event == "object_property_changed":
            self.object_manager.on_object_property_changed(args[0], args[1], args[2], args[3])

        if event == "object_pad_connected":
            self.object_manager.on_object_pad_connected(args[0], args[1], args[2], args[3])

        if event == "object_pad_disconnected":
            self.object_manager.on_object_pad_disconnected(args[0], args[1], args[2], args[3])

        if event == "object_pad_value":
            self.object_manager.on_object_output_pad_value(args[0], args[1], args[2])
