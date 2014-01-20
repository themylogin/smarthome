# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import defaultdict
from Queue import Queue


class Dispatcher(object):
    def __init__(self):
        self.objects = {}

        self.property_explanations = defaultdict(dict)

        self.event_connections = defaultdict(lambda: defaultdict(list))
        self.event_explanations = defaultdict(dict)

        self.event_queue = Queue()

        self.subscribers = []

        self.errors = {}

    def add_subscriber(self, subscriber):
        self.subscribers.append(subscriber)

    def create_object(self, name, cls, *args, **kwargs):
        if name in self.objects:
            raise KeyError("Object already exists")

        self.objects[name] = cls.__new__(cls)
        self.objects[name].__before_init__(self, name)
        self.objects[name].__init__(*args, **kwargs)
        return self.objects[name]

    def explain_property(self, owner, name, explainer, explain_change_events=True):
        self.property_explanations[owner.name][name] = explainer
        if explain_change_events:
            self.explain_event(owner, "%s changed" % name, lambda **kwargs: explainer(kwargs["value"]))

    def connect_event(self, source, name, handler, policy=None, kwargs_filter={}):
        self.event_connections[source.name][name].append((handler, policy, kwargs_filter))

    def receive_event(self, source, name, **kwargs):
        self.event_queue.put((source, name, kwargs))

    def explain_event(self, source, name, explainer):
        self.event_explanations[source.name][name] = explainer

    def process_events(self):
        while True:
            source, name, kwargs = self.event_queue.get()

            explainer = self.event_explanations[source.name].get(name, None)
            if explainer:
                kwargs["explanation"] = explainer(**kwargs)

            for subscriber in self.subscribers:
                if hasattr(subscriber, "receive_event"):
                    subscriber.receive_event(source.name, name, kwargs)

                if "explanation" in kwargs:
                    if hasattr(subscriber, "receive_news"):
                        subscriber.receive_news(source.name, name, kwargs["explanation"])

            for handler, policy, kwargs_filter in self.event_connections[source.name][name]:
                if policy and not policy():
                    continue

                skip = False
                for key in kwargs_filter:
                    if kwargs[key] != kwargs_filter[key]:
                        skip = True
                        break
                if skip:
                    continue

                handler(**kwargs)

    def receive_error(self, object, text):
        self.receive_event(object, "error", text=text)

        self.errors[object.name] = text

        for subscriber in self.subscribers:
            if hasattr(subscriber, "receive_error"):
                subscriber.receive_error(object.name, text)

    def receive_recovery_from_error(self, object):
        self.receive_event(object, "recovered from error")

        if object.name in self.errors:
            del self.errors[object.name]

        for subscriber in self.subscribers:
            if hasattr(subscriber, "receive_error"):
                subscriber.receive_error(object.name, None)
