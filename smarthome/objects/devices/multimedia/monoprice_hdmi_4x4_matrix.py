# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import serial
import time

from smarthome.architecture.object import Object
from smarthome.architecture.object.args import Arg
from smarthome.objects.utils.device import find_device

__all__ = [b"Monoprice_HDMI_4x4_Matrix"]


class Monoprice_HDMI_4x4_Matrix(Object):
    args = {"device": Arg(str)}

    def create(self):
        for output in range(1, 5):
            property_name = "output_%d" % output
            self._create_property(property_name)
            self._set_property_setter(property_name, functools.partial(self._set_output, output), receive_after=True)

        self.serial_lock = self.lock()

    def init(self):
        with self.serial_lock:
            self.serial = serial.Serial(find_device(self.args["device"]), 9600)

    def _set_output(self, output, input):
        if input not in range(1, 5):
            raise ValueError("Input number should be in range from 1 to 4")

        with self.serial_lock:
            for attempt in range(5):
                code = (output - 1) * 4 + (input - 1)
                self.serial.write(b"".join(map(chr, [code, 255 - code, 0xd5, 0x7b])))
                time.sleep(0.2)
