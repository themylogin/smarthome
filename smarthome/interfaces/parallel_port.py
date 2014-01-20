# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import parallel
import time

from smarthome.architecture.object import Object
from smarthome.primitives.bit import Bit
from smarthome.primitives.read_only_bit import ReadOnlyBit


class ParallelPort(Object):
    def __init__(self):
        self.parallel = parallel.Parallel()

        self.inputs = {}
        for input in ["Error", "Selected", "PaperOut", "Busy", "Acknowledge"]:
            self.inputs[input] = self.create_child_object(
                "inputs[%s]" % input,
                ReadOnlyBit, default_value=self._get_status_line_state(input)
            )

        self.outputs = {}
        for output in ["DataStrobe", "InitOut", "Select"]:
            self.outputs[output] = self.create_child_object(
                "outputs[%s]" % output,
                Bit, default_value=None
            )
            self.dispatcher.connect_event(
                self.outputs[output], "value changed",
                self._create_output_setter(output)
            )

        self.start_thread(self._device_loop)

    def _get_status_line_state(self, output):
        return getattr(self.parallel, "getIn%s" % output)()

    def _create_output_setter(self, output):
        def setter(value, **kwargs):
            getattr(self.parallel, "set%s" % output)(value)
        return setter

    def _device_loop(self):
        while True:
            for output, bit in self.inputs.iteritems():
                bit.properties.access("value").receive(self._get_status_line_state(output))

            time.sleep(0.01)
