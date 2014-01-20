# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.primitives.timer import Timer


class SouvlakiSpaceStationDoorBell(Object):
    sounds = ["sound/door_bell/souvlaki%d.wav" % i for i in range(1, 5)]

    def __init__(self, sound_player):
        self.sound_player = sound_player

        self.sound = 0
        self.timer = Timer(10, self._reset)

    def ring(self):
        self.timer.stop()
        self.sound_player.play_sound(self.sounds[self.sound], interrupt=True)

        if self.sound == 0:
            self.dispatcher.receive_event(self, "ring", explanation="Звонят в дверь")

        self.sound += 1
        self.sound %= len(self.sounds)
        self.timer.start()

    def _reset(self):
        self.sound = 0
