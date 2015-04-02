# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import struct

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer

__all__ = [b"Arduino_RGB_Addressable_LED_Strip"]


class Arduino_RGB_Addressable_LED_Strip(Object):
    args = {"arduino": Arg(object_pointer)}

    def create(self):
        pass

    def init(self):
        pass

    @method
    def set_height(self, height):
        self.args["arduino"].write(struct.pack("<BB", 0, height))
