# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object.pointer import ObjectPointer, PropertyPointer

logger = logging.getLogger(__name__)

__all__ = []


def object_pointer(s):
    return ObjectPointer(s)


def property_pointer(s):
    object, property = s.split(".")
    return PropertyPointer(ObjectPointer(object), property)
