# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
from werkzeug.wrappers import Response

import themyutils.json

logger = logging.getLogger(__name__)

__all__ = [b"json_response"]


def json_response(meth):
    @functools.wraps(meth)
    def wrapper(*args, **kwargs):
        return Response(themyutils.json.dumps(meth(*args, **kwargs)), mimetype="application/json")
    return wrapper
