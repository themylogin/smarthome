# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
import serial
import time

from smarthome.architecture.object import Object
from smarthome.architecture.object.args import Arg
from smarthome.objects.utils.device import find_device

logger = logging.getLogger(__name__)

__all__ = [b"SerialBitVector"]


class SerialBitVector(Object):
    args = {"device": Arg(str),
            "baudrate": Arg(int),
            "length": Arg(int)}

    MANUAL_POLL_INTERVAL = 2
    WRITE_REACTION_TIMEOUT = 2

    def create(self):
        self.serial_lock = self.lock()

        for i in range(self.args["length"]):
            name = "bit%d" % i
            self._create_property(name)
            self._set_property_setter(name, functools.partial(self._set_bit, i), receive_after=True)

    def init(self):
        with self.serial_lock:
            self.serial = serial.Serial(find_device(self.args["device"]), self.args["baudrate"])

            self.last_recv = 0
            self.poll()

    def poll(self):
        with self.serial_lock:
            if self.serial.inWaiting() > self.args["length"]:
                self._read_device()
            elif time.time() - self.last_recv > self.MANUAL_POLL_INTERVAL:
                self.serial.flushInput()
                self.serial.write("?\n")
                self._read_device()

    def _set_bit(self, bit, value):
        if self.get_property("bit%d" % bit) != value:
            with self.serial_lock:
                self.serial.write("t%d\n" % (bit + 1))

            wait_started_at = time.time()
            while time.time() - wait_started_at < self.WRITE_REACTION_TIMEOUT:
                if self.get_property("bit%d" % bit) == value:
                    return
                else:
                    time.sleep(0.01)

            raise IOError("Vector have not reacted to writing")

    def _read_device(self):
        self._process_device_input(self.serial.readline().strip())
        self.last_recv = time.time()

    def _process_device_input(self, s):
        for c in s:
            if c not in ["0", "1"]:
                raise ValueError("Unknown character: 0x%x in string: [%s]" % (
                    ord(c), ", ".join(["0x%x" % ord(c) for c in s]),
                ))

        bits = map(bool, map(int, s))
        if len(bits) != self.args["length"]:
            raise ValueError("Read only %d bits (%s), expected %d" % (
                len(bits), bits, len(self.args["length"]),
            ))

        for i, bit in enumerate(bits):
            self.receive_property("bit%d" % i, bit)
