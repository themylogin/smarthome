# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import socket

from smarthome.interfaces.bit_vector import BitVector


class IpBitVector(BitVector):
    def __init__(self, local_host, local_port, remote_host, remote_port, bits_number,
                 forced_refresh_interval=60, refresh_timeout=5):
        super(IpBitVector, self).__init__(bits_number)

        self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
        self.socket.bind((local_host, local_port))
        self.socket.settimeout(forced_refresh_interval)

        self.remote_host = remote_host
        self.remote_port = remote_port

        self.refresh_timeout = refresh_timeout

        self.start_thread(self._network_read_loop, "read")
        self.start_thread(self._network_write_loop, "write")

    def _network_read_loop(self):
        while True:
            self._do_network_read_loop()

    def _do_network_read_loop(self):
        try:
            self._query_all_bits()
            self.recover_from_error()
        except socket.error as e:
            self.raise_error_and_sleep("Ошибка чтения из сети: %s" % repr(e))
            return

        while True:
            try:
                if self.bits_number > 1:
                    data, peer = self.socket.recvfrom(self.bits_number)
                else:
                    data, peer = self.socket.recvfrom(1)
                    data = "0%s" % data

                self._receive_bit(int(data[0]), bool(int(data[1])))
            except socket.timeout:
                try:
                    self._query_all_bits()
                except Exception as e:
                    self.raise_error_and_sleep("Ошибка чтения из сети: %s" % repr(e))
                    return
            except socket.error as e:
                self.raise_error_and_sleep("Ошибка чтения из сети: %s" % repr(e))
                return

    def _query_all_bits(self):
        for bit in range(self.bits_number):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.refresh_timeout)
            s.connect((self.remote_host, self.remote_port))
            if self.bits_number > 1:
                s.sendall("?%d" % bit)
            else:
                s.sendall("?")
            data, peer = s.recvfrom(1)
            self._receive_bit(bit, bool(int(data[0])))
            s.close()

    def _network_write_loop(self):
        while True:
            try:
                bit, new_value = self.write_queue.get()

                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(self.refresh_timeout)
                s.connect((self.remote_host, self.remote_port))
                if self.bits_number > 1:
                    s.sendall("%d%d" % (new_value, bit))
                else:
                    s.sendall("%d" % new_value)
                s.close()

                self.recover_from_error()
            except socket.error as e:
                self.raise_error_and_sleep("Ошибка записи в сеть: %s" % repr(e))
