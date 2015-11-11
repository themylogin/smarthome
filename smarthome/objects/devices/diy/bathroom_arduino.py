# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
import re

from smarthome.architecture.object import Object
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer

__all__ = [b"Nucleo_RGB_LED"]


class Bathroom_Arduino(Object):
    args = {"serial": Arg(object_pointer)}

    def create(self):
        self._create_property("movement")
        self._create_property("humidity")
        self._create_property("temperature")

    def init(self):
        self.averages = defaultdict(list)
        self.thread(self._thread)

    def _thread(self):
        while True:
            d = self.args["serial"].readline().rstrip()

            m = re.match("(PIR|Humidity|Temperature): ([0-9\.]+)", d)
            if m:
                if m.group(1) == "PIR":
                    self.receive_property("movement", True if m.group(2) == "1" else False)
                elif m.group(1) == "Humidity":
                    self._average_property("humidity", float(m.group(2)), 30, 0.4)
                elif m.group(1) == "Temperature":
                    self._average_property("temperature", float(m.group(2)), 30, 0.2)

    def _average_property(self, name, value, period, min_delta):
        if not self._properties[name]["has_value"]:
            self.receive_property(name, value)

        self.averages[name].append(value)
        if len(self.averages[name]) == period:
            new_value = sum(self.averages[name]) / len(self.averages[name])
            self.averages[name] = []

            if abs(self._properties[name]["value"] - new_value) >= min_delta:
                self.receive_property(name, new_value)

