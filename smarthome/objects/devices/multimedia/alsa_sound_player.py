# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import subprocess

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg

__all__ = [b"AlsaSoundPlayer"]


class AlsaSoundPlayer(Object):
    args = {"device": Arg(str)}

    def create(self):
        self.sound_queue = self.queue()
        self.current_sound = None
        self.thread(self._play_sounds)

    def init(self):
        pass

    @method
    def play(self, path, interrupt=False):
        if interrupt:
            while not self.sound_queue.empty():
                self.sound_queue.get_nowait()

            if self.current_sound is not None:
                try:
                    self.current_sound.kill()
                except:
                    self.logger.warning("Unable to kill current sound", exc_info=True)

        deferred = self.deferred(["finish", "interrupt", "complete"])
        self.sound_queue.put((path, deferred))
        return deferred.promise()

    def _play_sounds(self):
        while True:
            path, deferred = self.sound_queue.get()

            with deferred:
                self.current_sound = subprocess.Popen(["aplay",
                                                       "-D", self.args["device"],
                                                       "-N",
                                                       "-q",
                                                       path.encode("utf-8")])
                self.current_sound.communicate()

                deferred.resolve_finish()
                if self.current_sound.returncode == 0:
                    deferred.resolve_complete()
                else:
                    deferred.resolve_interrupt()

                self.current_sound = None
