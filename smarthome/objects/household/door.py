# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer

logger = logging.getLogger(__name__)

__all__ = [b"Door"]


class Door(Object):
    args = {"open_value": Arg(bool, True),
            "property": Arg(property_pointer)}

    def create(self):
        self._create_property("open")
        self._create_property("closed")

    def init(self):
        self.handle_property_changed(self.args["property"])

    @on_prop_changed("property")
    def handle_property_changed(self, value):
        self.receive_property("open", value == self.args["open_value"])
        self.receive_property("closed", value != self.args["open_value"])

        if self.get_property("open"):
            self.emit_signal("opened")
        else:
            self.emit_signal("closed")
