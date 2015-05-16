# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, prop, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer_list

logger = logging.getLogger(__name__)

__all__ = [b"OnOffDeviceGroup"]


class OnOffDeviceGroup(Object):
    args = {"properties": Arg(property_pointer_list)}

    def create(self):
        pass

    def init(self):
        self.receive_property("on", any(self.args["properties"]))

    @prop(toggleable=True)
    def get_on(self):
        return any(self.args["properties"])

    @prop(toggleable=True)
    def set_on(self, value):
        for i, property in enumerate(self.args["properties"]):
            self.args["properties"][i] = value

    @on_prop_changed("properties")
    def handle_property_changed(self, object, property, value):
        self.receive_property("on", any(self.args["properties"]))
