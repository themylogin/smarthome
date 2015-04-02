# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import avahi
import dbus
import logging

logger = logging.getLogger(__name__)

__all__ = [b"ZeroconfService"]


class ZeroconfService(object):
    def __init__(self, name, bus):
        self.name = name
        self.bus = bus

        self.entry_group = None

        self.avahi_server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                                           avahi.DBUS_INTERFACE_SERVER)
        self.avahi_server.connect_to_signal("StateChanged", self._on_avahi_server_state_changed)
        self._on_avahi_server_state_changed(self.avahi_server.GetState())

    def _on_avahi_server_state_changed(self, state):
        if state == avahi.SERVER_RUNNING:
            self._add_service()

    def _add_service(self):
        if self.entry_group is None:
            self.entry_group = dbus.Interface(self.bus.get_object(avahi.DBUS_NAME, self.avahi_server.EntryGroupNew()),
                                              avahi.DBUS_INTERFACE_ENTRY_GROUP)

        self.entry_group.AddService(avahi.IF_UNSPEC,
                                    avahi.PROTO_UNSPEC,
                                    dbus.UInt32(0),
                                    "smarthome-%s" % self.name,
                                    "_http._tcp",
                                    "",
                                    "",
                                    dbus.UInt16(46408),
                                    avahi.string_array_to_txt_array(""))
        self.entry_group.Commit()
