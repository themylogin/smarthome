# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Subscriber(object):
    def receive_event(self, id, datetime, source_name, event_name, kwargs):
        pass
