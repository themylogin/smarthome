# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import serial

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg
from smarthome.objects.utils.device import find_device

__all__ = [b"SharedSerialPort"]


class SharedSerialPort(Object):
    args = {"device": Arg(str),
            "baudrate": Arg(int)}

    def create(self):
        self.serial_lock = self.lock()

    def init(self):
        with self.serial_lock:
            self.serial = serial.Serial(find_device(self.args["device"]), self.args["baudrate"])

    @method
    def write(self, bytes):
        with self.serial_lock:
            self.serial.write(bytes)

    @method
    def readline(self, *args, **kwargs):
        return self.serial.readline(*args, **kwargs)
