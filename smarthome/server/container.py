# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

logger = logging.getLogger(__name__)

__all__ = [b"Container"]


class Container(object):
    def __init__(self):
        self.local_database = None
        self.shared_database = None

        self.imported_promises_manager = None
        self.exported_promises_manager = None

        self.worker_pool = None

        self.peer_manager = None
        self.object_manager = None

        self.web_server = None
        self.event_transceiver = None
