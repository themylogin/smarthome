# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.read_only_property import ReadOnlyProperty


class OnOffGroup(Object):
    def __init__(self, devices):
        self.devices = devices
        self.saved_state = []

        self.properties.create("on", ReadOnlyProperty, default_value=self._calculate_on())
        for device in self.devices:
            self.dispatcher.connect_event(device, "on changed",
                                          lambda **kwargs: self.properties.access("on").receive(self._calculate_on()))

    def save_state(self):
        self.saved_state = [None] * len(self.devices)

        for i, device in enumerate(self.devices):
            self.saved_state[i] = device.properties["on"]

    def restore_state(self):
        for i, state in enumerate(self.saved_state):
            self.devices[i].properties["on"] = state

    def all_on(self):
        for device in self.devices:
            device.properties["on"] = True

    def all_off(self):
        for device in self.devices:
            device.properties["on"] = False

    def _calculate_on(self):
        return [device for device in self.devices if device.properties["on"]]
