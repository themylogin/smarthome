# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.devices.on_off_device import OnOffDevice


class Light(OnOffDevice):
    def __init__(self, bit, title):
        super(Light, self).__init__(bit, "Свет %s" % title)
