# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import functools
import logging
import parallel

from smarthome.architecture.object import Object

logger = logging.getLogger(__name__)

__all__ = [b"ParallelPort"]


class ParallelPort(Object):
    INPUTS = ("Error", "Selected", "PaperOut", "Busy", "Acknowledge")
    OUTPUTS = ["DataStrobe", "InitOut", "Select"]

    def create(self):
        self.parallel_lock = self.lock()

        for input in self.INPUTS:
            self._create_property(input)

        for output in self.OUTPUTS:
            self._create_property(output)
            self._set_property_setter(output, functools.partial(self._set_output, output), receive_after=True)

        for i in range(8):
            name = "Data%d" % i
            self._create_property(name)
            self._set_property_setter(name, functools.partial(self._set_data_output, i), receive_after=True)

    def init(self):
        with self.parallel_lock:
            self.parallel = parallel.Parallel()

            for i in range(8):
                self.receive_property("Data%d" % i, False)

    def poll(self):
        with self.parallel_lock:
            for input in self.INPUTS:
                self.receive_property(input, getattr(self.parallel, "getIn%s" % input)())

    def _set_output(self, output, value):
        with self.parallel_lock:
            getattr(self.parallel, "set%s" % output)(value)

    def _set_data_output(self, i, value):
        with self.parallel_lock:
            data_value = self.parallel.getData()
            if value:
                data_value |= (1 << i)
            else:
                data_value &= ~(1 << i)
            self.parallel.setData(data_value)
