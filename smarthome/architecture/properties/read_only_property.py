# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.property import Property


class ReadOnlyProperty(Property):
    def __init__(self, dispatcher, owner, name, default_value):
        super(ReadOnlyProperty, self).__init__(dispatcher, owner, name, default_value)

    def set(self, value, **kwargs):
        raise AttributeError("Property is read-only")

    def receive(self, value):
        super(ReadOnlyProperty, self).set(value)
