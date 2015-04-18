# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime
import logging
from Queue import Queue
import socket
import time

import themyutils.json
from themyutils.threading import start_daemon_thread

from smarthome.architecture.object.proxy import LocalObject

logger = logging.getLogger(__name__)

__all__ = []


class ThemylogPublisher(object):
    def __init__(self, address_family, address_type, address):
        self.address_family = address_family
        self.address_type = address_type
        self.address = address
        self.queue = Queue()
        start_daemon_thread(self._pub_thread)

    def on_object_signal_emitted(self, object, signal, args, kwargs):
        if isinstance(object, LocalObject):
            self.pub(object._name, signal, {"args": args, "kwargs": kwargs})

    def on_object_property_changed(self, object, property_name, old_value, new_value):
        if isinstance(object, LocalObject):
            self.pub(object._name, "%s_changed" % property_name, {"value": new_value, "old_value": old_value})

    def pub(self, logger, msg, args):
        self.queue.put({"application": "smarthome",
                        "logger": logger,
                        "datetime": datetime.now(),
                        "level": logging.INFO,
                        "msg": msg,
                        "args": args,
                        "explanation": ""})

    def _pub_thread(self):
        while True:
            record = self.queue.get()

            while True:
                try:
                    s = socket.socket(self.address_family, self.address_type)
                    if self.address_type == socket.SOCK_STREAM:
                        s.connect(self.address)
                        s.send(themyutils.json.dumps(record))
                    if self.address_type == socket.SOCK_DGRAM:
                        s.sendto(themyutils.json.dumps(record), self.address)
                    s.close()
                except:
                    logger.error("Publication failed", exc_info=True)
                    time.sleep(1)
                else:
                    break
