# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import socket
import urlparse

logger = logging.getLogger(__name__)

__all__ = [b"parse_themylog"]


def get_themylog(config):
    themylog = config.xpath("/smarthome/themylog")
    if themylog:
        url = urlparse.urlparse(themylog[0].text)
        if url.scheme == "unix":
            return (socket.AF_UNIX, socket.SOCK_STREAM, url.path)
        if url.scheme == "tcp":
            return (socket.AF_INET, socket.SOCK_STREAM, (url.netloc.split(":")[0], int(url.netloc.split(":")[1])))
        if url.scheme == "udp":
            return (socket.AF_INET, socket.SOCK_DGRAM, (url.netloc.split(":")[0], int(url.netloc.split(":")[1])))
