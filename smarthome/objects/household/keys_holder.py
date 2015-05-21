# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer

logger = logging.getLogger(__name__)

__all__ = [b"KeysHolder"]


class KeysHolder(Object):
    args = {"has_keys_value": Arg(bool, False),
            "property": Arg(property_pointer)}

    def create(self):
        self._create_property("has_keys")

    def init(self):
        self.handle_property_changed(self.args["property"])

    @on_prop_changed("property", debounce=1)
    def handle_property_changed(self, value):
        self.receive_property("has_keys", value == self.args["has_keys_value"])

        if self.get_property("has_keys"):
            self.emit_signal("keys_put")
        else:
            self.emit_signal("keys_taken")
