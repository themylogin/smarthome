# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import alsaaudio
import math
import numpy
import scipy
from scipy.signal import butter, lfilter

from smarthome.architecture.object import Object, prop

__all__ = [b"Volume_Meter"]


class Volume_Meter(Object):
    def create(self):
        self.cutoff = 2000
        self._update_filter()

        self._create_output_pad("volume", "float")
        self._create_output_pad("stereo_volume", "(float, float)")

    def init(self):
        self.thread(self._thread)

    @prop(receive_after=True)
    def set_cutoff(self, value):
        self.cutoff = value
        self._update_filter()

    def _update_filter(self):
        self.filter = butter(5, self.cutoff / (44100 / 2))

    def _thread(self):
        self.input = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
        self.input.setchannels(2)
        self.input.setrate(44100)
        self.input.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.input.setperiodsize(1024)

        means = []
        while True:
            l, data = self.input.read()

            wave = numpy.fromstring(data, dtype="int16")
            wave = wave - numpy.mean(wave)

            lwave = wave[0::2]
            rwave = wave[1::2]

            lwave = lfilter(self.filter[0], self.filter[1], lwave)
            rwave = lfilter(self.filter[0], self.filter[1], rwave)

            lmean = numpy.abs(lwave).mean()
            rmean = numpy.abs(rwave).mean()
            mean = (lmean + rmean) / 2

            means = (means + [mean])[-1000:]
            max_mean = max(means)

            lvolume = lmean / max_mean
            rvolume = rmean / max_mean
            volume = (lvolume + rvolume) / 2

            volume = math.log10(1 + 9 * volume)
            volume = max(volume, 0.5)

            self._write_output_pad("volume", volume)
            self._write_output_pad("stereo_volume", (lvolume, rvolume))
