# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import os

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer
from smarthome.common import DATA_DIR

logger = logging.getLogger(__name__)

__all__ = [b"DoorBell"]


class DoorBell(Object):
    args = {"sound_player": Arg(object_pointer),
            "files": Arg(unicode),
            "reset_sequence_timeout": Arg(int)}

    def create(self):
        self.files = map(lambda s: os.path.join(DATA_DIR, s.strip()), self.args["files"].split(","))

        self.index = 0
        self.playing = False
        self.reset_sequence = self.timer("reset_sequence", self.args["reset_sequence_timeout"], self._reset)

    def init(self):
        pass

    @method
    def ring(self):
        if self.playing:
            return

        self.reset_sequence.stop()
        self.args["sound_player"].play(self.files[self.index], interrupt=True).on_finish(self._set_not_playing)
        self.index += 1
        self.index %= len(self.files)
        self.playing = True
        self.reset_sequence.start()

    def _reset(self):
        self.index = 0

    def _set_not_playing(self):
        self.playing = False
