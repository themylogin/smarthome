# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.read_only_property import ReadOnlyProperty
from smarthome.primitives.timer import Timer

class OwnerWatcher(Object):
    def __init__(self, front_door, keys_holder, speech_synthesizer):
        self.front_door = front_door
        self.keys_holder = keys_holder
        self.speech_synthesizer = speech_synthesizer

        self.properties.create("at_home", ReadOnlyProperty, default_value=self.keys_holder.properties["has_keys"])
        self.properties.create("is_leaving", ReadOnlyProperty, default_value=False)

        self.signal_property_values("at_home", {True: "came", False: "left"})
        self.dispatcher.explain_property(self, "at_home", self._explain_at_home)

        self.dispatcher.connect_event(self.front_door, "opened", self._on_front_door_opened)
        self.dispatcher.connect_event(self.front_door, "closed", self._on_front_door_closed)

        self.dispatcher.connect_event(self.keys_holder, "put", self._on_keys_put)

        self.leave_timer = Timer(15, self._on_leave_timer_timeout)

    def _explain_at_home(self, value, **kwargs):
        if value:
            return "Хозяин дома"
        else:
            return "Хозяин не дома"

    def _on_front_door_opened(self):
        self.properties.access("at_home").receive(True)

    def _on_front_door_closed(self):
        if not self.keys_holder.properties["has_keys"]:
            self.leave_timer.start()

    def _on_keys_put(self):
        self.leave_timer.stop()
        self.properties.access("at_home").receive(True)

        if self.properties["is_leaving"]:
            self.properties.access("is_leaving").receive(False)
            self.speech_synthesizer.say("Самоликвидация остановлена", interrupt=True)

    def _on_leave_timer_timeout(self):
        self.properties.access("is_leaving").receive(True)
        self.speech_synthesizer.say("Умный дом опустел. Запускается процесс самоликвидации. " +
                                    "Десять. Девять. Восемь. Семь. Шесть. Пять. Четыре. Три. Два. Один.",
                                    interrupt=True, on_finish=self._on_left)

    def _on_left(self):
        if self.properties["is_leaving"]:
            self.properties.access("is_leaving").receive(False)
            self.properties.access("at_home").receive(False)
