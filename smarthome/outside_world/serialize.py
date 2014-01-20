# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import json


class SmarthomeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()

        try:
            return super(SmarthomeEncoder, self).default(obj)
        except TypeError:
            return repr(obj)


def serialize(obj):
    return SmarthomeEncoder().encode(obj)


def unserialize(s):
    return json.loads(s)
