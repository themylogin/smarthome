# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import alsaaudio
import numpy
import scipy
from scipy.signal import firwin

from smarthome.architecture.object import Object

__all__ = [b"RGB_LED_Music_Controller"]


class RGB_LED_Music_Controller(Object):
    def create(self):
        pass

    def init(self):
        self.input = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
        self.input.setchannels(2)
        self.input.setrate(44100)
        self.input.setformat(alsaaudio.PCM_FORMAT_S16_LE)
        self.input.setperiodsize(1024)

        self._create_output_pad("RGpulse", "RGB")
        self._create_output_pad("stereo_volume", "stereo_volume")

        self.thread(self._thread)

    def _thread(self):
        filter = firwin(101, 0.02)
        means = []

        while True:
            l, data = self.input.read()

            wave = numpy.fromstring(data, dtype="int16")
            wave = wave - numpy.mean(wave)

            lwave = wave[0::2]
            rwave = wave[1::2]

            lwave = scipy.convolve(lwave, filter, "same")
            rwave = scipy.convolve(rwave, filter, "same")

            lmean = numpy.abs(lwave).mean()
            rmean = numpy.abs(rwave).mean()
            mean = (lmean + rmean) / 2

            means = (means + [mean])[-1000:]
            max_mean = max(means)

            lvolume = lmean / max_mean
            rvolume = rmean / max_mean
            volume = (lvolume + rvolume) / 2

            self._write_output_pad("RGpulse", (volume, volume, volume))
            self._write_output_pad("stereo_volume", (lvolume, rvolume))
