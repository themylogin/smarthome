# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
import serial
import struct
import time

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property import Property
from smarthome.architecture.properties.read_only_property import ReadOnlyProperty


class LedStrip(Object):
    def __init__(self, title, path, default_generator="black"):
        self.title = title
        self.serial = serial.Serial(path, 9600)

        self.generators = OrderedDict([
            ("black",   ("выключена", solid_color_generator(0, 0, 0))),
            ("white",   ("светится белым", solid_color_generator(255, 255, 255))),
            ("red",     ("светится красным", solid_color_generator(255, 0, 0))),
            ("green",   ("светится зелёным", solid_color_generator(0, 255, 0))),
            ("blue",    ("светится синим", solid_color_generator(0, 0, 255))),
            ("glow",    ("переливается", glow_generator)),
            ("2ci",     ("ебашит", twoci_generator)),
        ])

        self.generator = self.generators[default_generator][1]()
        self.properties.create("generator", Property, default_generator)
        self.dispatcher.explain_property(self, "generator", self._explain_generator)

        self.properties.create("on", ReadOnlyProperty, False)
        self.dispatcher.connect_event(self, "generator changed", self._on_generator_changed)

        self.start_thread(self._generator_thread)

    def next_generator(self):
        keys = self.generators.keys()
        self.properties["generator"] = keys[(keys.index(self.properties["generator"]) + 1) % len(keys)]

    def _explain_generator(self, value, **kwargs):
        return self.title + u" " + self.generators[value][0]

    def _on_generator_changed(self, value, **kwargs):
        self.properties.access("on").receive(value != "black")
        self.generator = self.generators[value][1]()

    def _generator_thread(self):
        while True:
            r, g, b = self.generator.next()
            r_pwm, g_pwm, b_pwm = r * 4000 / 255, g * 4000 / 255, b * 4000 / 255
            self.serial.write(struct.pack(b"<HHH", r_pwm, g_pwm, b_pwm))
            time.sleep(0.01)


def solid_color_generator(r, g, b):
    def generator():
        while True:
            yield r, g, b
    return generator


def glow_generator():
    while True:
        for i in range(0, 256):
            yield 255 - i, i, 0
        for i in range(0, 256):
            yield 0, 255 - i, i
        for i in range(0, 256):
            yield i, 0, 255 - i


def twoci_generator():
    while True:
        for i in range(0, 256, 127):
            yield 255 - i, i, 0
        for i in range(0, 256, 127):
            yield 0, 255 - i, i
        for i in range(0, 256, 127):
            yield i, 0, 255 - i
