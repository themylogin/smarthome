# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer

logger = logging.getLogger(__name__)

__all__ = [b"Button"]


class Button(Object):
    args = {"property": Arg(property_pointer),
            "released_state": Arg(bool)}

    def create(self):
        pass

    def init(self):
        pass

    @on_prop_changed("property")
    def handle_property_changed(self, value):
        if value == self.args["released_state"]:
            self.emit_signal("released")
        else:
            self.emit_signal("pressed")
