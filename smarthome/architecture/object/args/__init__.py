# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"Arg"]


class NoDefaultValue(object):
    pass


class Arg(object):
    def __init__(self, type=type, default_value=NoDefaultValue):
        self.type = type

        self.has_default_value = not isinstance(default_value, NoDefaultValue)
        self.default_value = default_value
