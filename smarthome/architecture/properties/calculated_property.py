# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.read_only_property import ReadOnlyProperty


class CalculatedProperty(ReadOnlyProperty):
    def __init__(self, dispatcher, owner, name, calculator):
        super(CalculatedProperty, self).__init__(dispatcher, owner, name, calculator())
        self.calculator = calculator

    def get(self):
        return self.calculator()
