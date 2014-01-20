# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.property import Property


class IntercomManager(Object):
    def __init__(self, intercom, default_welcome=True):
        self.intercom = intercom

        self.properties.create("welcome", Property, default_value=default_welcome)

        self.dispatcher.connect_event(self.intercom, "listener input", self.on_listener_input)

        self.dispatcher.explain_event(self, "call", lambda **kwargs: "Звонит домофон")
        self.dispatcher.explain_event(self, "code accepted", lambda **kwargs: "Умный домофон распознал код")
        self.dispatcher.explain_event(self, "code rejected", lambda **kwargs: "Умный домофон не распознал код")

    def on_listener_input(self, input):
        if input == "BELL":
            self.dispatcher.receive_event(self, "call")

            self.intercom.take_receiver()
            if self.properties["welcome"]:
                self._play_sound("sound/intercom/cat.wav", on_complete=self._open_door)
            else:
                self.intercom.tell_listener("LISTEN_FOR_CODE")

        if input == "CODE":
            self.dispatcher.receive_event("code accepted")
            self._play_sound("sound/intercom/cat.wav", on_complete=self._open_door)

        if input == "NO_CODE":
            self.dispatcher.receive_event("code rejected")
            self._play_sound("sound/intercom/kazakhstan.wav", on_complete=self._put_receiver_down)

    def _play_sound(self, path, on_complete=lambda: None):
        self.intercom.tell_listener("DO_NOT_LISTEN")
        self.intercom.play_sound(path, on_complete=on_complete)

    def _open_door(self):
        self.intercom.open_door(on_complete=self._put_receiver_down)

    def _put_receiver_down(self):
        self.intercom.put_receiver_down()
        self.intercom.tell_listener("LISTEN_FOR_BELL")
