# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.property import Property


class WriteOnlyProperty(Property):
    def __init__(self, dispatcher, owner, name, default_value, setter):
        super(WriteOnlyProperty, self).__init__(dispatcher, owner, name, default_value)

        self.setter = setter

    def get(self):
        return self.value

    def set(self, value, **kwargs):
        self.setter(value)

        super(WriteOnlyProperty, self).set(value, **kwargs)
