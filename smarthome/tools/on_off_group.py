# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.complex_property import ComplexProperty


class OnOffGroup(Object):
    def __init__(self, devices):
        self.devices = devices
        self.saved_state = []

        self.properties.create("on", ComplexProperty, getter=self._get_on, setter=self._set_on)
        for device in self.devices:
            self.dispatcher.connect_event(device, "on changed",
                                          lambda **kwargs: self.properties.access("on").receive(self._get_on()))

    def _get_on(self):
        return {device.name: device.properties["on"] for device in self.devices if device.properties["on"]}

    def _set_on(self, value):
        if isinstance(value, bool):
            for device in self.devices:
                device.properties["on"] = value

        if isinstance(value, dict):
            for device in self.devices:
                device.properties["on"] = value.get(device.name, False)
