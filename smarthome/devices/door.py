# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property_copy import PropertyCopy


class Door(Object):
    def __init__(self, bit, title, open_state=True):
        self.title = title

        self.properties.create(
            "open",
            PropertyCopy, bit.properties.access("value"),
            direct_transform=lambda state: state == open_state,
            inverse_transform=lambda state: state == open_state,
        )

        self.signal_property_values("open", {True: "opened", False: "closed"})
        self.dispatcher.explain_property(self, "open", self._explain_open)

    def _explain_open(self, value):
        if value:
            return "%s открыта" % self.title
        else:
            return "%s закрыта" % self.title
