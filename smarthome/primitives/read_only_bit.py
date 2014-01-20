# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.read_only_property import ReadOnlyProperty
from smarthome.primitives.bit import Bit

class ReadOnlyBit(Bit):
    def __init__(self, default_value):
        self.properties.create("value", ReadOnlyProperty, default_value=default_value)
