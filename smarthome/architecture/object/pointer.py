# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"ObjectPointer", b"ObjectPointerList", b"PropertyPointer"]


class ObjectPointer(object):
    def __init__(self, name):
        self.name = name


class ObjectPointerList(list):
    pass


class PropertyPointer(object):
    def __init__(self, object_pointer, name):
        self.object_pointer = object_pointer
        self.name = name
