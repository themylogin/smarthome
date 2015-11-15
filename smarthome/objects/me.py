# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import subprocess

from smarthome.architecture.object import Object, method

logger = logging.getLogger(__name__)

__all__ = [b"Me"]


class Me(Object):
    def create(self):
        pass

    def init(self):
        pass

    @method
    def execute_command(self, command):
        return subprocess.check_output(command)
