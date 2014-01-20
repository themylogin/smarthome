# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class ConfigParserException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
