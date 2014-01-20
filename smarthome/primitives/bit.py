# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property import Property

class Bit(Object):
    def __init__(self, default_value):
        self.properties.create("value", Property, default_value=default_value)
