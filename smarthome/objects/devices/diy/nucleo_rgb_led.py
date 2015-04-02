# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import struct

from smarthome.architecture.object import Object, input_pad
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer

__all__ = [b"Nucleo_RGB_LED"]


class Nucleo_RGB_LED(Object):
    args = {"nucleo": Arg(object_pointer),
            "number": Arg(int)}

    def create(self):
        pass

    def init(self):
        pass

    @input_pad("RGB", initial_value=(0, 0, 0), disconnected_value=(0, 0, 0))
    def RGB(self, (r, g, b)):
        self.args["nucleo"].write(struct.pack("<BBHHH", 0, self.args["number"], 4096 * r, 4096 * g, 4096 * b))
