# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import alsaaudio
import numpy
import scipy
from scipy.signal import firwin

from smarthome.architecture.object import Object, prop

__all__ = [b"Volume_Meter"]


class Volume_Meter(Object):
    def create(self):
        self.numtaps = 101
        self.cutoff = 0.02
        self._update_filter()

        self._create_output_pad("volume", "float")
        self._create_output_pad("stereo_volume", "(float, float)")

    def init(self):
        self.thread(self._thread)

    @prop(receive_after=True)
    def set_numtaps(self, value):
        self.numtaps = value
        self._update_filter()

    @prop(receive_after=True)
    def set_cutoff(self, value):
        self.cutoff = value
        self._update_filter()

    def _update_filter(self):
        self.filter = firwin(self.numtaps, self.cutoff)

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

            lwave = scipy.convolve(lwave, self.filter, "same")
            rwave = scipy.convolve(rwave, self.filter, "same")

            lmean = numpy.abs(lwave).mean()
            rmean = numpy.abs(rwave).mean()
            mean = (lmean + rmean) / 2

            means = (means + [mean])[-1000:]
            max_mean = max(means)

            lvolume = lmean / max_mean
            rvolume = rmean / max_mean
            volume = (lvolume + rvolume) / 2

            self._write_output_pad("volume", volume)
            self._write_output_pad("stereo_volume", (lvolume, rvolume))
