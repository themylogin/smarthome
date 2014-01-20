# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import glob
import termios
import time

import serial
from smarthome.interfaces.bit_vector import BitVector, BitVectorInputError


class SerialBitVector(BitVector):
    expected_device_errors = (IOError, termios.error, BitVectorInputError)

    def __init__(self, device_mask, bits_number):
        super(SerialBitVector, self).__init__(bits_number)

        self.device_mask = device_mask

        self.device = None
        self.start_thread(self._device_loop)

    def _device_loop(self):
        while True:
            self.device = self._open_device()
            if self.device:
                self._do_device_loop()

    def _open_device(self):
        devices = glob.glob(self.device_mask)
        if devices:
            error = None
            for device in devices:
                try:
                    device = serial.Serial(device, 9600)
                    self.recover_from_error()
                    return device
                except self.expected_device_errors, e:
                    error = e
            self.raise_error_and_sleep("Ошибка открытия последовательного порта: %s" % repr(error))
            return None
        else:
            self.raise_error_and_sleep("Не найдено ни одного устройства: %s" % self.device_mask)
            return None

    def _do_device_loop(self):
        try:
            self.device.flushInput()
            self.device.write("?\n")
        except self.expected_device_errors, e:
            self.raise_error_and_sleep("Ошибка последовательного порта: %s" % repr(e))
            return

        while True:
            try:
                if self.device.inWaiting() > self.bits_number:
                    self._process_device_input(self.device.readline().strip())
            except self.expected_device_errors, e:
                self.raise_error_and_sleep("Ошибка последовательного порта: %s" % repr(e))
                return

            while not self.write_queue.empty():
                bit, new_value = self.write_queue.get()

                if self.bits[bit].properties["value"] != new_value:
                    try:
                        self.device.write("t%d\n" % (bit + 1))
                        self._process_device_input(self.device.readline().strip())
                    except self.expected_device_errors, e:
                        self.raise_error_and_sleep("Ошибка последовательного порта: %s" % repr(e))
                        return

            time.sleep(0.01)

    def _process_device_input(self, s):
        for c in s:
            if c not in ["0", "1"]:
                raise BitVectorInputError("Неизвестный символ: 0x%x в строке: [%s]" % (
                    ord(c), ", ".join(["0x%x" % ord(c) for c in s]),
                ))

        bits = map(bool, map(int, s))
        if len(bits) != len(self.bits):
            raise BitVectorInputError("Прочитано только %d бит (%s), ожидалось %d" % (
                len(bits), bits, len(self.bits),
            ))

        for i, bit in enumerate(bits):
            self._receive_bit(i, bit)
