# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.primitives.remote_bit import RemoteBit


class BitVectorInputError(Exception):
    pass


class BitVector(Object):
    def __init__(self, bits_number):
        self.bits_number = bits_number

        self.bits = [self.create_child_object("[%d]" % i, RemoteBit, setter=self._create_setter(i))
                     for i in range(self.bits_number)]

        self.write_queue = self.create_queue()

    def _create_setter(self, bit):
        def setter(value):
            self.write_queue.put((bit, value))
        return setter

    def _receive_bit(self, bit, value):
        if self.bits[bit].properties["value"] != value:
            self.bits[bit].properties.access("value").receive(value)
