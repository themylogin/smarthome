# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property_copy import PropertyCopy


class OnOffDevice(Object):
    def __init__(self, bit, title, gender="male"):
        self.properties.create("on", PropertyCopy, bit.properties.access("value"))

        self.title = title
        self.gender = {"male": 0, "female": 1, "neuter": 2, "plural": 3}[gender]

        self.dispatcher.explain_property(self, "on", self._explain_on)

    def _explain_on(self, value):
        if value:
            return ("%s включен", "%s включена", "%s включено", "%s включены")[self.gender] % self.title
        else:
            return ("%s выключен", "%s выключена", "%s выключено", "%s выключены")[self.gender] % self.title

    def toggle(self):
        self.properties["on"] = not self.properties["on"]
