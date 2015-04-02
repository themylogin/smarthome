# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict
import time

from smarthome.architecture.object import Object, method, prop, output_pad

__all__ = [b"RGB_LED_Controller"]


class RGB_LED_Controller(Object):
    def create(self):
        self.generators = OrderedDict([
            ("white",   ("светится белым", solid_color_generator(255, 255, 255))),
            ("red",     ("светится красным", solid_color_generator(255, 0, 0))),
            ("green",   ("светится зелёным", solid_color_generator(0, 255, 0))),
            ("blue",    ("светится синим", solid_color_generator(0, 0, 255))),
            ("glow",    ("переливается", glow_generator)),
            ("2ci",     ("ебашит", twoci_generator)),
        ])

    def init(self):
        self.generator = None
        self.sleep = 0.01

    @prop(receive_after=True)
    def set_generator(self, generator):
        self.generator = self.generators[generator][1]() if generator else None

    @method
    def next_generator(self):
        generator = self.get_property("generator")
        if generator:
            keys = self.generators.keys()
            next_generator_index = keys.index(generator) + 1
            if next_generator_index < len(keys):
                next_generator = keys[next_generator_index]
            else:
                next_generator = None
        else:
            next_generator = "white"
        self.set_property("generator", next_generator)

    @prop(receive_after=True)
    def set_speed(self, speed):
        self.sleep = 1 / speed

    @output_pad("RGB")
    def pad(self):
        while True:
            if self.generator:
                yield map(self._brightness_to_pwm, self.generator.next())

            time.sleep(self.sleep)

    def _brightness_to_pwm(self, brightness):
        return brightness / 255


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