# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.remote_property import RemoteProperty
from smarthome.primitives.bit import Bit

class RemoteBit(Bit):
    def __init__(self, setter):
        self.properties.create("value", RemoteProperty, default_value=None, setter=setter)
