# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object.pointer import ObjectPointer, ObjectPointerList, PropertyPointer, PropertyPointerList

logger = logging.getLogger(__name__)

__all__ = [b"object_pointer", b"object_pointer_list", b"property_pointer", b"property_pointer_list"]


def object_pointer(s):
    return ObjectPointer(s)


def object_pointer_list(s):
    return ObjectPointerList(map(object_pointer, _split_list(s)))


def property_pointer(s):
    object, property = s.split(".")
    return PropertyPointer(ObjectPointer(object), property)


def property_pointer_list(s):
    return PropertyPointerList(map(property_pointer,  _split_list(s)))


def _split_list(s):
    return map(lambda x: x.strip(), s.split(","))
