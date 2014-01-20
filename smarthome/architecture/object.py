# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from Queue import Queue
import threading
import time

import prctl
from smarthome.architecture.property_bag import PropertyBag
from smarthome.architecture.thread import start_thread


class Object(object):
    def __before_init__(self, dispatcher, name):
        self.dispatcher = dispatcher

        self.name = name
        self.properties = PropertyBag(self.dispatcher, self)

        self.error = None

    #

    def create_child_object(self, name, cls, *args, **kwargs):
        if name[0] != "[":
            name = "." + name
        return self.dispatcher.create_object(self.name + name, cls, *args, **kwargs)

    #

    def signal_property_values(self, property, values):
        def event_sender(value, **kwargs):
            if value in values:
                self.dispatcher.receive_event(self, values[value])

        self.dispatcher.connect_event(self, "%s changed" % property, event_sender)

    #

    def raise_error(self, error):
        if self.error != error:
            self.error = error
            self.dispatcher.receive_error(self, error)

    def raise_error_and_sleep(self, error, sleep=1.0):
        self.raise_error(error)
        time.sleep(sleep)

    def recover_from_error(self):
        if self.error:
            self.error = None
            self.dispatcher.receive_recovery_from_error(self)

    #

    def create_event(self):
        return threading.Event()

    def create_lock(self):
        return threading.Lock()

    def create_queue(self):
        return Queue()

    def start_thread(self, target, name=None):
        if hasattr(self, "name"):
            if name is not None:
                thread_name = "%s:%s" % (self.name, name)
            else:
                thread_name = self.name
        else:
            if name is not None:
                thread_name = name
            else:
                thread_name = "anonymous"

        start_thread(target, thread_name)

    #

    def __repr__(self):
        if hasattr(self, "name"):
            return "%s (%s)" % (self.name, self.__class__.__name__)
        else:
            return self.__class__.__name__
