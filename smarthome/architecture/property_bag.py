# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class PropertyBag:
    def __init__(self, dispatcher, owner):
        self.dispatcher = dispatcher
        self.owner = owner

        self.properties = {}

    def create(self, name, cls, *args, **kwargs):
        if name in self.properties:
            raise KeyError("Property already exists")

        self.properties[name] = cls(self.dispatcher, self.owner, name, *args, **kwargs)

    def access(self, name):
        return self.properties[name]

    def get(self, name, *args, **kwargs):
        return self.properties[name].get(*args, **kwargs)

    def set(self, name, value, *args, **kwargs):
        self.properties[name].set(value, *args, **kwargs)

    def __getitem__(self, name):
        return self.properties[name].get()

    def __setitem__(self, name, value):
        self.properties[name].set(value)

    def __iter__(self):
        for key in self.properties:
            yield key
