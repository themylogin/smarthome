# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime, timedelta
import functools
from threading import Lock
import time

__all__ = [b"Timer"]


class Timer(object):
    def __init__(self, worker_pool, logger, timeout, callback):
        self.worker_pool = worker_pool
        self.logger = logger
        self.timeout = timeout
        self.callback = callback

        self.started = False
        self.started_at = None
        self.callback_at = None
        self.lock = Lock()

    def start(self):
        with self.lock:
            self.callback_at = datetime.now() + timedelta(seconds=self.timeout)
            self.logger.info("Starting to time out at %r", self.callback_at)

            if not self.started:
                self.started = True
                self.started_at = datetime.now()
                self.worker_pool.run_task(self._process)

    def stop(self):
        with self.lock:
            if self.started:
                self.logger.info("Stop")

            self._reset()

    def _process(self):
        while True:
            with self.lock:
                if not self.started:
                    break

                if self.callback_at <= datetime.now():
                    self.logger.info("Timed out")

                    self.worker_pool.run_task(self.callback if self.callback.func_code.co_argcount == 0
                                              else functools.partial(self.callback, self.started_at))

                    self._reset()

            time.sleep(0.1)

    def _reset(self):
        self.started = False
        self.started_at = None
        self.callback_at = None
