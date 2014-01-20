# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import itertools
import operator

from smarthome.architecture.object import Object
from smarthome.primitives.timer import Timer


class SleepTracker(Object):
    def __init__(self, life_signs, fall_timeout, raise_timeout):
        self.has_life = lambda: reduce(operator.or_, [sign[0]() for sign in life_signs], False)

        for property in itertools.chain(*map(operator.itemgetter(1), life_signs)):
            self.dispatcher.connect_event(property.owner, "%s changed" % property.name, self._on_has_life_changed)

        self.wait_before_sleep = Timer(fall_timeout, self._on_wait_before_sleep_timeout)
        self.wait_after_sleep = Timer(raise_timeout, self._on_wait_after_sleep_timeout)

        self.sleep_started_at = None

    def _on_has_life_changed(self, **kwargs):
        if self.sleep_started_at:
            if self.wait_after_sleep.started:
                pass
            else:
                if self.has_life():
                    self.wait_after_sleep.start()
        else:
            if self.wait_before_sleep.started:
                if self.has_life():
                    self.wait_before_sleep.stop()
            else:
                if not self.has_life():
                    self.wait_before_sleep.start()

    def _on_wait_before_sleep_timeout(self):
        self.sleep_started_at = self.wait_before_sleep.started_at
        self.dispatcher.receive_event(self, "fall asleep", at=self.sleep_started_at)

    def _on_wait_after_sleep_timeout(self):
        if self.has_life():
            self.dispatcher.receive_event(self, "woke up", at=self.wait_after_sleep.started_at)
            self.dispatcher.receive_event(self, "sleep tracked", start=self.sleep_started_at,
                                                                 end=self.wait_after_sleep.started_at)
            self.sleep_started_at = None
