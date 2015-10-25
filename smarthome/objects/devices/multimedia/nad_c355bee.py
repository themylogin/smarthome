# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import serial
import termios
import time

from smarthome.architecture.object import Object, method, prop
from smarthome.architecture.object.args import Arg
from smarthome.objects.utils.device import find_device

__all__ = [b"NAD_C355BEE"]


class NAD_C355BEE(Object):
    args = {"device": Arg(str)}

    SOURCES = ("Tape2", "Tuner", "AUX", "Video", "CD", "Disc")
    BOOLEAN_PROPERTIES = {"Power": "power",
                          "Mute": "mute",
                          "SpeakerA": "speaker_a",
                          "SpeakerB": "speaker_b",
                          "Tape1": "tape1_monitor"}

    VOLUME_UP_TO_MAX = 34.5
    VOLUME_DOWN_TO_MIN = 38

    def create(self):
        for code, property_name in self.BOOLEAN_PROPERTIES.iteritems():
            self._create_property(property_name)
            self._set_property_querier(property_name, functools.partial(self._query, code))
            self._set_property_setter(property_name, functools.partial(self._set_bool, code))
            self._set_property_toggleable(property_name)

        self.serial_lock = self.lock()

        self.relative_volume = 0

    def init(self):
        with self.serial_lock:
            self.serial = serial.Serial(find_device(self.args["device"]), 115200)

            # Don't know why this is needed
            attr = termios.tcgetattr(self.serial.fd)
            termios.tcsetattr(self.serial.fd, termios.TCSANOW, attr)

    def poll(self):
        lines = []
        with self.serial_lock:
            waiting = self.serial.inWaiting()
            if waiting > 0:
                lines = map(lambda line: line.strip(), self.serial.read(waiting).split("\r\r"))

        for line in lines:
            line = line.strip()
            self.logger.debug("Read %s", line)

            if "=" in line:
                key, value = line.split("=", 1)
                if key == "Main.Source":
                    self.receive_property("source", value)
                elif key.startswith("Main."):
                    boolean_property = self.BOOLEAN_PROPERTIES.get(key[len("Main."):])
                    if boolean_property is not None:
                        self.receive_property(boolean_property, {"On": True, "Off": False}[value])

    @method
    def increase_volume(self):
        self._execute_command("Main.Volume+")
        self.relative_volume += 1.0

    @method
    def decrease_volume(self):
        self._execute_command("Main.Volume-")
        self.relative_volume -= self.VOLUME_UP_TO_MAX / self.VOLUME_DOWN_TO_MIN

    @method
    def save_volume(self):
        self.relative_volume = 0

    @method
    def restore_volume(self, precision=0.25):
        while abs(self.relative_volume) > precision:
            if self.relative_volume > 0:
                self.decrease_volume()
            else:
                self.increase_volume()
            time.sleep(0.5)

    @prop
    def query_source(self):
        self._query("Source")

    @prop
    def set_source(self, source):
        if source not in self.SOURCES:
            raise ValueError("Source must be one of %s" % ", ".join(self.SOURCES))

        self._execute_command("Main.Source=%s" % source)

    def _execute_command(self, command):
        with self.serial_lock:
            self.logger.debug("Writing %s", command)
            self.serial.write("\r%s\r" % command)
            time.sleep(0.1)

    def _query(self, name):
        self._execute_command("Main.%s?" % name)

    def _set_bool(self, name, val):
        self._execute_command("Main.%s=%s" % (name, "On" if val else "Off"))
