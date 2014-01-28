# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.property import Property


class ComplexProperty(Property):
    def __init__(self, dispatcher, owner, name, getter, setter):
        super(ComplexProperty, self).__init__(dispatcher, owner, name, getter())

        self.getter = getter
        self.setter = setter

    def get(self):
        return self.getter()

    def set(self, value, **kwargs):
        self.setter(value)

    def receive(self, value):
        super(ComplexProperty, self).set(value)
