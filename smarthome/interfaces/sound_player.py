# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os
import subprocess

from smarthome.architecture.object import Object
from smarthome.architecture.patterns.loops import Loop


class SoundPlayerLoop(Loop):
    def execute(self, path, on_finish, on_interrupt, on_complete):
        self.parent.current_sound_lock.acquire()
        self.parent.current_sound = subprocess.Popen(["aplay", "-D", self.parent.device, "-N", "-q",
                                                      path.encode("utf-8")])
        self.parent.current_sound_lock.release()

        self.parent.current_sound.communicate()

        on_finish()
        if self.parent.current_sound.returncode:
            on_interrupt()
        else:
            on_complete()


class SoundPlayer(Object):
    def __init__(self, device="default"):
        self.device = device

        self.current_sound = None
        self.current_sound_lock = self.create_lock()

        self.loop = SoundPlayerLoop(self)

    def play_sound(self, path, interrupt=False, on_finish=lambda: None,
                                                on_interrupt=lambda: None,
                                                on_complete=lambda: None):
        if interrupt:
            while not self.loop.queue.empty():
                self.loop.queue.get_nowait()

        self.loop(os.path.join(os.path.dirname(__file__), "..", "..", path), on_finish, on_interrupt, on_complete)

        if interrupt:
            self.current_sound_lock.acquire()
            try:
                self.current_sound.kill()
            except:
                pass
            self.current_sound_lock.release()
