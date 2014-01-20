# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property_copy import PropertyCopy


class KeysHolder(Object):
    def __init__(self, bit, has_keys_state=False):
        self.properties.create(
            "has_keys",
            PropertyCopy, bit.properties.access("value"),
            direct_transform=lambda state: state == has_keys_state,
            inverse_transform=lambda state: state == has_keys_state,
        )

        self.signal_property_values("has_keys", {True: "put", False: "taken"})
        self.dispatcher.explain_property(self, "has_keys", self._explain_has_keys)

    def _explain_has_keys(self, value):
        if value:
            return "Ключи висят"
        else:
            return "Ключи сняты"
