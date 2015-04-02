# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object.pointer import *
from smarthome.architecture.object.proxy import UnavailableObject

logger = logging.getLogger(__name__)

__all__ = [b"ArgsBag"]


class ArgsBag(object):
    def __init__(self, args, object_manager):
        self.args = args
        self.object_manager = object_manager

    def __getitem__(self, key):
        value = self.args[key]

        if isinstance(value, ObjectPointer):
            return self._get_object(value)

        if isinstance(value, ObjectPointerList):
            return map(self._get_object, value)

        if isinstance(value, PropertyPointer):
            return getattr(self._get_object(value.object_pointer), value.name)

        return value

    def _get_object(self, object_pointer):
        return self.object_manager.objects.get(object_pointer.name, UnavailableObject(object_pointer.name))

    def __setitem__(self, key, val):
        value = self.args[key]

        if isinstance(value, PropertyPointer):
            setattr(self._get_object(value.object_pointer), value.name, val)
            return

        raise KeyError("Can't set ArgsBag item %s that is not a PropertyPointer" % key)
