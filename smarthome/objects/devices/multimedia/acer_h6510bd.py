# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import serial
import time

from smarthome.architecture.object import Object, method, prop
from smarthome.architecture.object.args import Arg
from smarthome.objects.utils.device import find_device

__all__ = [b"Acer_H6510BD"]


class Acer_H6510BD(Object):
    args = {"device": Arg(str)}

    def create(self):
        self.serial_lock = self.lock()

    def init(self):
        with self.serial_lock:
            self.serial = serial.Serial(find_device(self.args["device"]), 9600)
            self.serial.setDTR(False)

            query_times_out_at = time.time() + 1
            self.serial.write("* 0 Lamp ?\r")
            buffer = b""
            while time.time() < query_times_out_at:
                buffer += self.serial.read(self.serial.inWaiting())
                sendings = buffer.split(b"\r")
                if len(sendings) and not sendings[-1].endswith("\r"):
                    buffer = sendings.pop()
                else:
                    buffer = b""

                for sending in sendings:
                    if sending == "Lamp 1":
                        self.logger.info("Initialized with lamp powered on")
                        self.receive_property("on", True)
                        return

            self.logger.info("Initialized with lamp powered off")
            self.receive_property("on", False)
            self.serial.setDTR(True)

    @method
    def toggle_hdmi_source(self):
        self._execute_command("IR 050")

    @prop(toggleable=True, receive_after=True)
    def set_on(self, on):
        with self.serial_lock:
            if on:
                self.serial.setDTR(False)
                time.sleep(5)

                self._execute_command("IR 001")
            else:
                self._execute_command("IR 002")
                time.sleep(10)

                self.serial.setDTR(True)

    def _execute_command(self, command):
        with self.serial_lock:
            self.serial.write("* 0 %s\r" % command)
            time.sleep(0.1)
