# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging

from smarthome.architecture.object.logic_expression import LogicExpression
from smarthome.architecture.object.pointer import *
from smarthome.architecture.object.proxy import UnavailableObject

logger = logging.getLogger(__name__)

__all__ = [b"ArgsBag"]


class ArgsBag(object):
    def __init__(self, object_manager, args):
        self.object_manager = object_manager
        self.args = args

    def __getitem__(self, key):
        value = self.args[key]

        if isinstance(value, ObjectPointer):
            return self._get_object(value)

        if isinstance(value, ObjectPointerList):
            return map(self._get_object, value)

        if isinstance(value, PropertyPointer):
            return self._get_property(value)

        if isinstance(value, PropertyPointerList):
            return _MutablePropertyPointerList(map(self._get_property, value),
                                               functools.partial(self._set_property_pointer_list_item, value))

        if isinstance(value, LogicExpression):
            return functools.partial(value.expression, self.object_manager)

        return value

    def _get_object(self, object_pointer):
        return self.object_manager.objects.get(object_pointer.name, UnavailableObject(object_pointer.name))

    def _get_property(self, object_property_pointer):
        return getattr(self._get_object(object_property_pointer.object_pointer), object_property_pointer.name)

    def _set_property_pointer_list_item(self, object_property_pointer, i, value):
        self._set_property(object_property_pointer[i], value)

    def _set_property(self, property_pointer, value):
        setattr(self._get_object(property_pointer.object_pointer), property_pointer.name, value)

    def __setitem__(self, key, val):
        value = self.args[key]

        if isinstance(value, PropertyPointer):
            self._set_property(value, val)
            return

        raise KeyError("Can't set ArgsBag item %s that is not a PropertyPointer" % key)


class _MutablePropertyPointerList(list):
    def __init__(self, values, setitem):
        super(_MutablePropertyPointerList, self).__init__(values)
        self.setitem = setitem

    def __setitem__(self, key, value):
        self.setitem(key, value)
