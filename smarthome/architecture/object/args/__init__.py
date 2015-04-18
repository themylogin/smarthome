# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"Arg"]


class _NoDefaultValue(object):
    pass


def _bool_parser(s):
    return s.strip().lower() in ("1", "true", "yes")


class Arg(object):
    def __init__(self, type, default_value=_NoDefaultValue):
        if type is bool:
            type = _bool_parser

        self.type = type

        self.has_default_value = not isinstance(default_value, _NoDefaultValue)
        self.default_value = default_value
