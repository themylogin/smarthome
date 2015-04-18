# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"Datastore"]


class Datastore(object):
    def __init__(self, database, key_path):
        self.database = database
        self.key_path = key_path

    def set_default_value(self, key, val):
        if key not in self:
            self[key] = val

    def __contains__(self, key):
        try:
            self[key]
        except KeyError:
            return False
        else:
            return True

    def __getitem__(self, key):
        with self.database as d:
            dd = d
            for k in self.key_path:
                if k not in dd:
                    dd[k] = {}
                dd = dd[k]

            if key in dd:
                return key
            else:
                raise KeyError(key)

    def __setitem__(self, key, val):
        with self.database as d:
            dd = d
            for k in self.key_path:
                if k not in dd:
                    dd[k] = {}
                dd = dd[k]

            dd[key] = val
