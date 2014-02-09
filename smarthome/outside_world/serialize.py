# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import themyutils.json


def serialize(o):
    return themyutils.json.dumps(o)


def unserialize(s):
    return themyutils.json.loads(s)
