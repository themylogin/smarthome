# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import datetime
import ephem

from smarthome.architecture.object import Object
from smarthome.architecture.properties.calculated_property import CalculatedProperty

class Sun(Object):
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

        self.properties.create("is_shining", CalculatedProperty, self._calculate_is_shining)

    def _calculate_is_shining(self):
        observer = ephem.Observer()
        observer.date = datetime.datetime.utcnow()
        observer.lat = self.latitude
        observer.long = self.longitude

        sun = ephem.Sun()
        sun.compute(observer)

        return observer.next_setting(sun).datetime() < observer.next_rising(sun).datetime()
