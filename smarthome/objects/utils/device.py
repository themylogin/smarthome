# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import glob
import logging
import subprocess

logger = logging.getLogger(__name__)


def find_device(query):
    args = query.replace(" ", "").split(",")

    mask = args.pop(0)
    strings = ["%s==\"%s\"" % (key if key.isupper() else "ATTRS{%s}" % key, value)
               for key, value in map(lambda s: s.split("=", 1), args)]

    for device in glob.glob(mask):
        info = subprocess.check_output(["udevadm", "info", "--name=%s" % device, "--attribute-walk"])
        if all(string in info for string in strings):
            logger.debug("For query %s found device %s", query, device)
            return device

    raise Exception("Device '%s' not found" % query)
