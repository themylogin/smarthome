# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from smarthome.zeroconf.discoverer import SynchronousServiceDiscoverer


class discover_services(object):
    def __init__(self, discover_timeout=5):
        self.discoverer = SynchronousServiceDiscoverer(discover_timeout)

    def __enter__(self):
        return self.discoverer.discover()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.discoverer.close()
