# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Property(object):
    def __init__(self, dispatcher, owner, name, default_value=None):
        self.dispatcher = dispatcher
        self.owner = owner
        self.name = name

        self.value = default_value

    def get(self):
        return self.value

    def set(self, value, **kwargs):
        if value != self.value:
            old_value = self.value
            self.value = value

            self.dispatcher.receive_event(
                self.owner, "%s changed" % self.name,
                old_value=old_value, value=self.value, **kwargs
            )
