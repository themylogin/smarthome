# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import os

logger = logging.getLogger(__name__)

__all__ = [b"DATA_DIR"]

DATA_DIR = os.path.join(os.path.dirname(__file__), b"..", b"data")
