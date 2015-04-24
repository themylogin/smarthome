# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from appdirs import user_data_dir
import logging
import os

logger = logging.getLogger(__name__)

__all__ = [b"DATA_DIR", b"UTILS_DIR", b"USER_DATA_DIR"]

DATA_DIR = os.path.join(os.path.dirname(__file__), b"..", b"data")
UTILS_DIR = os.path.join(os.path.dirname(__file__), b"..", b"utils")

USER_DATA_DIR = user_data_dir(b"smarthome")
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
