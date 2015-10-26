# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import errno
import fcntl
import logging
import os
import prctl
import signal
import subprocess
import sys
import time

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer, property_pointer
from smarthome.common import UTILS_DIR

logger = logging.getLogger(__name__)

__all__ = [b"Intercom"]


class Intercom(Object):
    args = {"receiver_control": Arg(property_pointer),
            "door_control": Arg(property_pointer),
            "audio_input": Arg(unicode)}

    def create(self):
        self.tell_listener_queue = self.queue()
        self.thread(self._listener_thread)

    def init(self):
        self.args["receiver_control"] = False
        self.args["door_control"] = False

    @method
    def take_receiver(self):
        self.args["receiver_control"] = True

    @method
    def put_receiver_down(self):
        self.args["receiver_control"] = False

    @method
    def tell_listener(self, message):
        self.tell_listener_queue.put(message)

    @method
    def open_door(self):
        time.sleep(2.0)
        self.args["door_control"] = True
        time.sleep(1.0)
        self.args["door_control"] = False
        time.sleep(1.0)

    def _listener_thread(self):
        listener = os.path.join(UTILS_DIR, b"intercom_listener/dist/Debug/GNU-Linux-x86/intercom_listener")

        while True:
            try:
                process = subprocess.Popen([listener, self.args["audio_input"]], stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           preexec_fn=lambda: prctl.set_pdeathsig(signal.SIGKILL))

                fd = process.stdout.fileno()
                fl = fcntl.fcntl(fd, fcntl.F_GETFL)
                fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

                self.set_error(None)

                while True:
                    process.poll()
                    if process.returncode is not None:
                        raise Exception("Listener process returned code %d" % process.returncode)

                    try:
                        input = process.stdout.readline()
                    except IOError as e:
                        if e.errno != errno.EWOULDBLOCK:
                            raise
                    else:
                        if input:
                            self.emit_signal("listener_input", input=input.strip())

                    while not self.tell_listener_queue.empty():
                        process.stdin.write(self.tell_listener_queue.get() + "\n")

                    time.sleep(0.01)
            except:
                self.set_error({"listener_thread": sys.exc_info()})
                time.sleep(1)
