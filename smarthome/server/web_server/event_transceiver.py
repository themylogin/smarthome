# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import functools

from smarthome.architecture.object.proxy import ProxyObject, LocalObject

logger = logging.getLogger(__name__)

__all__ = []


class EventTransceiver(object):
    def __init__(self, container):
        self.container = container

    def __getattr__(self, name):
        if name.startswith("on_"):
            return functools.partial(self._be_observer, name[len("on_"):])

        raise AttributeError(name)

    def _be_observer(self, event, *args):
        args = list(args)

        local_only_events = {"object_signal_emitted": 0,
                             "object_property_changed": 0,
                             "object_pad_connected": 2,
                             "object_pad_disconnected": 2,
                             "object_pad_value": 2}
        if event in local_only_events:
            if not isinstance(args[local_only_events[event]], LocalObject):
                return

        args = map(self._serialize_arg, args)

        logger.getChild(event).debug("Notifying: %r", args)
        self.container.web_server.notify_my_event(event, args)

    def _serialize_arg(self, arg):
        if isinstance(arg, ProxyObject):
            return arg._name

        return arg

    def receive_remote_event(self, event, args):
        logger.getChild(event).debug("Received: %r", args)

        if event == "exported_promise_resolved":
            self.container.imported_promises_manager.on_deferred_resolve(args[0], args[1], *args[2], **args[3])

        if event == "exported_promise_destroyed":
            self.container.imported_promises_manager.on_deferred_destroy(args[0])

        if event == "object_signal_emitted":
            self.container.object_manager.on_object_signal_emitted(args[0], args[1], **args[2])

        if event == "object_property_changed":
            self.container.object_manager.on_object_property_changed(args[0], args[1], args[2], args[3])

        if event == "object_pad_connected":
            self.container.object_manager.on_object_pad_connected(args[0], args[1], args[2], args[3])

        if event == "object_pad_disconnected":
            self.container.object_manager.on_object_pad_disconnected(args[0], args[1], args[2], args[3])

        if event == "object_pad_value":
            self.container.object_manager.on_object_output_pad_value(args[0], args[1], args[2])
