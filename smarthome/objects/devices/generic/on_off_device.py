# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, prop, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer

logger = logging.getLogger(__name__)

__all__ = [b"OnOffDevice"]


class OnOffDevice(Object):
    args = {"invert": Arg(bool, False),
            "property": Arg(property_pointer)}

    def create(self):
        pass

    def init(self):
        self.receive_property("on", self.args["property"] ^ self.args["invert"])

    @prop(toggleable=True)
    def get_on(self):
        return self.args["property"] ^ self.args["invert"]

    @prop(toggleable=True)
    def set_on(self, value):
        self.args["property"] = value ^ self.args["invert"]

    @on_prop_changed("property")
    def handle_property_changed(self, value):
        self.receive_property("on", value ^ self.args["invert"])
