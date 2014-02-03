# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime, timedelta
import time

from smarthome.architecture.object import Object
from smarthome.architecture.properties.read_only_property import ReadOnlyProperty


class BathroomFanManager(Object):
    def __init__(self, light, fan, min_light_time=180, max_fan_time=3600, time_multiplier=2):
        self.light = light
        self.fan = fan

        self.min_light_time = timedelta(seconds=min_light_time)
        self.max_fan_time = timedelta(seconds=max_fan_time)
        self.time_multiplier = time_multiplier

        self.properties.create("fan_will_be_powered_off_at", ReadOnlyProperty, default_value=None)

        self.dispatcher.connect_event(self.light, "on changed", self.on_light_on_changed)

        self.light_powered_on_at = None
        self.fan.properties["on"] = False

        self.start_thread(self._power_fan_off_thread)

    def on_light_on_changed(self, value, **kwargs):
        if value:
            self.light_powered_on_at = datetime.now()
        else:
            if self.light_powered_on_at:
                light_time = datetime.now() - self.light_powered_on_at
                self.light_powered_on_at = None

                if light_time > self.min_light_time:
                    if self.properties["fan_will_be_powered_off_at"]:
                        base = self.properties["fan_will_be_powered_off_at"]
                    else:
                        base = datetime.now()

                    self.fan.properties["on"] = True
                    self.properties.access("fan_will_be_powered_off_at").receive(base + min(
                        self.time_multiplier * light_time,
                        self.max_fan_time
                    ))

    def _power_fan_off_thread(self):
        while True:
            if (self.properties["fan_will_be_powered_off_at"] and
                self.properties["fan_will_be_powered_off_at"] <= datetime.now()):

                self.fan.properties["on"] = False
                self.properties.access("fan_will_be_powered_off_at").receive(False)

            time.sleep(1)
