# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from evdev import InputDevice, categorize, ecodes

from smarthome.architecture.object import Object


class EvdevInput(Object):
    def __init__(self, path):
        self.path = path

        self.start_thread(self._device_loop)

    def _device_loop(self):
        while True:
            try:
                for event in InputDevice(self.path).read_loop():
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        self.dispatcher.receive_event(self, "%s %s" % (
                            key_event.keycode,
                            ("UP", "DOWN", "HOLD")[key_event.keystate],
                        ))
            except Exception, e:
                self.raise_error_and_sleep("Ошибка опроса клавиатуры: %s" % repr(e))
