# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import os
import threading

import themyutils.json

logger = logging.getLogger(__name__)

__all__ = [b"Database"]


class Database(object):
    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                f.write(b"{}")

        with open(self.path, "r") as f:
            self.data = themyutils.json.loads(f.read())

        self.lock = threading.Lock()

    def __enter__(self):
        self.lock.acquire()
        return self.data

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            with open(self.path, "w") as f:
                f.write(themyutils.json.dumps(self.data))
        finally:
            self.lock.release()
