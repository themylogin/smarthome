# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import struct
import time

from smarthome.architecture.object import Object, input_pad
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer

__all__ = [b"STM32F103R8T6_RGB_LED"]


class STM32F103R8T6_RGB_LED(Object):
    args = {"serial": Arg(object_pointer)}

    def create(self):
        self.last_pad_write = 0
        self.r = 0
        self.g = 0
        self.b = 0

    def init(self):
        self.thread(self._thread)

    @input_pad("RGB", initial_value=(0, 0, 0), disconnected_value=(0, 0, 0))
    def RGB(self, (r, g, b)):
        self.r, self.g, self.b = r, g, b
        self._write()

    def _write(self):
        self.args["serial"].write(struct.pack("<HHH", 4000 * self.r, 4000 * self.g, 4000 * self.b))
        self.last_pad_write = time.time()

    def _thread(self):
        while True:
            try:
                if time.time() - self.last_pad_write >= 1:
                    self._write()
            except Exception:
                pass

            time.sleep(1)
