# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
from threading import RLock
import time

logger = logging.getLogger(__name__)

__all__ = [b"DebouncedPropertyChangeObserver"]


class DebouncedPropertyChangeObserver(object):
    def __init__(self, container, observer, debounce_time):
        self.container = container
        self.observer = observer
        self.debounce_time = debounce_time

        self.lock = RLock()
        self.last_change = 0
        self.debounce_seq = 0
        self.last_debounce_end_old_value = None
        self.last_debounce_end_new_value = None

    def __call__(self, old_value, new_value):
        with self.lock:
            if time.time() - self.last_change > self.debounce_time:
                self._end_debounce(old_value, new_value, True)
            else:
                self.last_change = time.time()
                self.debounce_seq += 1
                logger.debug("Starting debounce seq=%d", self.debounce_seq)
                self.container.worker_pool.run_task(functools.partial(self._debounce, self.debounce_seq, old_value,
                                                                      new_value))

    def _debounce(self, seq, old_value, new_value):
        time.sleep(self.debounce_time)

        with self.lock:
            if self.debounce_seq == seq:
                self._end_debounce(old_value, new_value)
            else:
                logger.debug("Debounce seq=%d is not final", seq)

    def _end_debounce(self, old_value, new_value, force_observer_call=False):
        with self.lock:
            self.last_change = time.time()
            self.debounce_seq = 0
            if (force_observer_call or
                    old_value != self.last_debounce_end_old_value or
                    new_value != self.last_debounce_end_new_value):
                self.last_debounce_end_old_value = old_value
                self.last_debounce_end_new_value = new_value
                self.observer(old_value, new_value)
