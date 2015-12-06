# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import OrderedDict
import time

from smarthome.architecture.object import Object, PropertyHasNoValueException, method, prop, input_pad, output_pad

__all__ = [b"RGB_LED_Controller"]


class RGB_LED_Controller(Object):
    def create(self):
        self._create_property("brightness", 1.0)
        self._set_property_writable("brightness")

        self._create_property("speed", 100)
        self._set_property_writable("speed")

        self.generators = OrderedDict([
            ("white",   ("светится белым", solid_color_generator(255, 255, 255))),
            ("red",     ("светится красным", solid_color_generator(255, 0, 0))),
            ("green",   ("светится зелёным", solid_color_generator(0, 255, 0))),
            ("blue",    ("светится синим", solid_color_generator(0, 0, 255))),
            ("glow",    ("переливается", glow_generator)),
            ("2ci",     ("ебашит", twoci_generator)),
        ])

    def init(self):
        self.set_generator(self.generators.keys()[0])
        self.pad_brightness = 1
        self.sleep = 0.01

    @prop(receive_after=True)
    def set_generator(self, generator):
        self.generator = self.generators[generator][1]()

    @method
    def next_generator(self):
        try:
            generator = self.get_property("generator")
        except PropertyHasNoValueException:
            generator = None

        keys = self.generators.keys()
        self.set_property("generator", keys[(keys.index(generator) + 1) % len(keys) if generator else 0])

    @input_pad("float", disconnected_value=1)
    def brightness(self, value):
        self.pad_brightness = value

    @prop(receive_after=True)
    def set_speed(self, speed):
        self.sleep = 1 / speed

    @output_pad("RGB")
    def pad(self):
        had_generator = False
        while True:
            if self.generator:
                had_generator = True
                yield map(self._brightness_to_pwm,
                          map(lambda x: x * self.pad_brightness * self.get_property("brightness"),
                              self.generator.next()))
            elif had_generator:
                had_generator = False
                yield 0, 0, 0

            sleep_for = 1.0 / self.get_property("speed")
            wake_up_at = time.time() + sleep_for
            while time.time() < wake_up_at:
                time.sleep(min(sleep_for, 0.1))

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
