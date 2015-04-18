# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import namedtuple
import logging

logger = logging.getLogger(__name__)

__all__ = [b"LogicExpression"]

LogicExpression = namedtuple("LogicExpression", ["expression", "properties_involved"])
