# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta

from themyutils.restful_api.clients import RestfulApiPoller

from smarthome.architecture.object import Object
from smarthome.architecture.properties.read_only_property import ReadOnlyProperty


class GuestsWatcher(Object):
    def __init__(self, api_url, front_door, speech_synthesizer):
        self.api_url = api_url
        self.front_door = front_door
        self.speech_synthesizer = speech_synthesizer

        self.properties.create("guests", ReadOnlyProperty, default_value=[])
        self.properties.create("expected_guests", ReadOnlyProperty, default_value=[])

        self.last_front_door_closed_at = datetime.min
        self.dispatcher.connect_event(self.front_door, "closed", self._on_front_door_closed)

        self.start_thread(self._guests_thread)

    def _guests_thread(self):
        first_start = True
        for data in RestfulApiPoller(self.api_url + "/guests"):
            bye_guests = set(self.properties["guests"] + self.properties["expected_guests"])
            for guest in data["guests"]:
                title = guest["user"]["title"]

                if title in bye_guests:
                    bye_guests.discard(title)
                else:
                    if (not first_start and
                        len(guest["user"]["visits"]) > 0 and
                        "no_welcome_postpone" in guest["came"]["data"] and
                        datetime.now() - self.last_front_door_closed_at > timedelta(minutes=5)):
                        self.properties.access("expected_guests").receive(self.properties["expected_guests"] + [title])
                    else:
                        self.speech_synthesizer.say("В умном доме гость. Привет, %s!" % title)
                        self.properties.access("guests").receive(self.properties["guests"] + [title])

            for title in bye_guests:
                self.speech_synthesizer.say("Пока, %s!" % title)
                self.properties.access("guests").receive([g for g in self.properties["guests"]
                                                          if g != title])
                self.properties.access("expected_guests").receive([g for g in self.properties["expected_guests"]
                                                                   if g != title])

            first_start = False

    def _on_front_door_closed(self):
        self.last_front_door_closed_at = datetime.now()

        for title in self.properties["expected_guests"]:
            self.speech_synthesizer.say("В умном доме гость. Привет, %s!" % title)
            self.properties.access("guests").receive(self.properties["guests"] + [title])
            self.properties.access("expected_guests").receive([g for g in self.properties["expected_guests"]
                                                               if g != title])
