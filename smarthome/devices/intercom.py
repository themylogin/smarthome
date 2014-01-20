# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import errno
import fcntl
import os
import subprocess
import time

from smarthome.architecture.object import Object
from smarthome.interfaces.sound_player import SoundPlayer


class Intercom(Object):
    def __init__(self, receiver_bit, door_bit, input_device, output_device):
        self.receiver_bit = receiver_bit
        self.door_bit = door_bit
        self.input_device = input_device
        self.output_device = output_device

        self.output_player = self.dispatcher.create_object("%s.output_sound_player" % self.name,
                                                           SoundPlayer, self.output_device)

        self.receiver_bit.properties["value"] = False
        self.door_bit.properties["value"] = False

        self.dispatcher.explain_event(self, "door opened", lambda **kwargs: "Дверь в подъезд открыта")

        self.listener_output_queue = self.create_queue()
        self.start_thread(self._listener_thread)

    def take_receiver(self):
        self.receiver_bit.properties["value"] = True

    def put_receiver_down(self):
        self.receiver_bit.properties["value"] = False

    def play_sound(self, *args, **kwargs):
        self.output_player.play_sound(*args, **kwargs)

    def tell_listener(self, message):
        self.listener_output_queue.put(message)

    def open_door(self, on_complete=lambda: None):
        def open_door_thread():
            self.door_bit.properties["value"] = True
            time.sleep(1.0)
            self.door_bit.properties["value"] = False
            time.sleep(1.0)

            self.dispatcher.receive_event(self, "door opened")

            on_complete()

        self.start_thread(open_door_thread)

    def _listener_thread(self):
        listener = os.path.join(os.path.dirname(__file__), "..", "..",
                                "utils/intercom_listener/dist/Debug/GNU-Linux-x86/intercom_listener")

        while True:
            try:
                process = subprocess.Popen(
                    [listener, self.input_device],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                fd = process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                self.recover_from_error()

                while True:
                    process.poll()
                    if process.returncode is not None:
                        raise Exception("Процесс неожиданно завершился с кодом %d" % process.returncode)

                    input = None
                    try:
                        input = process.stdout.readline()
                    except IOError, e:
                        if e.errno != errno.EWOULDBLOCK:
                            raise
                    if input:
                        self.dispatcher.receive_event(self, "listener input", input=input.strip())

                    while not self.listener_output_queue.empty():
                        process.stdin.write(self.listener_output_queue.get() + "\n")

                    time.sleep(0.01)

            except Exception, e:
                self.raise_error_and_sleep("Ошибка прослушивания домофона: %s" % repr(e))
