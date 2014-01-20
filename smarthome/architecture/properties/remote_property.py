# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from collections import namedtuple
import time

from smarthome.architecture.properties.property import Property

ExpectedReceipt = namedtuple("ExpectedReceipt", ["value", "expires_at", "kwargs"])


class RemoteProperty(Property):
    def __init__(self, dispatcher, owner, name, default_value, setter, setter_delay=5.0):
        super(RemoteProperty, self).__init__(dispatcher, owner, name, default_value)

        self.setter = setter
        self.setter_delay = setter_delay

        self.initialized = False
        self.expected_receipt = None

    def set(self, value, **kwargs):
        self.setter(value)

        self.expected_receipt = ExpectedReceipt(value=value, expires_at=time.time() + self.setter_delay, kwargs=kwargs)

    def receive(self, value):
        if not self.initialized:
            self.initialized = True
            self.value = value
            return

        if (self.expected_receipt and
            self.expected_receipt.value == value and
            self.expected_receipt.expires_at > time.time()):
            synthetic = True
            kwargs = self.expected_receipt.kwargs
        else:
            synthetic = False
            kwargs = {}

        self.expected_receipt = None

        super(RemoteProperty, self).set(value, synthetic=synthetic, **kwargs)
