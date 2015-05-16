# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import threading

logger = logging.getLogger(__name__)

__all__ = [b"Deferred", b"Promise"]


class Deferred(object):
    def __init__(self, container, events):
        self.container = container

        self.events = {event: {"resolved": False,
                               "callbacks": []}
                       for event in events}
        self.events_lock = threading.Lock()

        self.promises = []
        self.destroy_callbacks = []

    def __getattr__(self, name):
        if name.startswith("on_"):
            event = name[len("on_"):]
            if event in self.events:
                def bind_event(callback):
                    with self.events_lock:
                        if self.events[event]["resolved"]:
                            self.perform_callback(event, callback)
                        else:
                            self.events[event]["callbacks"].append(callback)
                        return self
                return bind_event
            else:
                raise AttributeError("Deferred/Promise does not support event %s" % event)

        if name.startswith("resolve_"):
            event = name[len("resolve_"):]
            if event in self.events:
                def resolve_event(*args, **kwargs):
                    with self.events_lock:
                        self.events[event]["resolved"] = True
                        self.events[event]["resolved_args"] = args
                        self.events[event]["resolved_kwargs"] = kwargs
                        for callback in self.events[event]["callbacks"]:
                            self._perform_callback(event, callback)
                        return self
                return resolve_event
            else:
                raise AttributeError("Deferred/Promise does not support event %s" % event)

        return super(Deferred, self).__getattribute__(name)

    def _perform_callback(self, event, callback):
        self.container.worker_pool.run_task(lambda: callback(*self.events[event]["resolved_args"],
                                                             **self.events[event]["resolved_kwargs"]))

    def promise(self):
        promise = Promise(self)
        self.promises.append(promise)
        return promise

    def on_destroy(self, callback):
        self.destroy_callbacks.append(callback)

    def destroy(self):
        for callback in self.destroy_callbacks:
            callback()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.destroy()


class Promise(object):
    def __init__(self, deferred):
        self.deferred = deferred

    def __getattr__(self, name):
        if name.startswith("on_"):
            return getattr(self.deferred, name)

        return super(Promise, self).__getattribute__(name)
