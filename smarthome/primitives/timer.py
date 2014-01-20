# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime, timedelta
import logging
import os
import time
import traceback

from smarthome.architecture.object import Object

logger = logging.getLogger(__name__)


class Timer(Object):
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback

        filename, line = traceback.extract_stack(limit=2)[0][0:2]
        self.title = "Timer at %s:%d" % (os.path.basename(filename), line)

        self.callback_at = None
        self.callback_at_lock = self.create_lock()

        self.started = False
        self.started_at = None

        self.start_thread(self._thread, self.title)

    def start(self):
        self.callback_at_lock.acquire()

        now = datetime.now()

        self.callback_at = now + timedelta(seconds=self.timeout)

        self.started = True
        self.started_at = now

        self.callback_at_lock.release()

    def stop(self):
        self.callback_at_lock.acquire()

        self.callback_at = None

        self.started = False
        self.started_at = None

        self.callback_at_lock.release()

    def _thread(self):
        while True:
            self.callback_at_lock.acquire()

            if self.callback_at and self.callback_at <= datetime.now():
                logger.debug("%s timed out", self.title)

                self.callback()

                self.callback_at = None

                self.started = False
                self.started_at = None

            self.callback_at_lock.release()

            time.sleep(0.1)
