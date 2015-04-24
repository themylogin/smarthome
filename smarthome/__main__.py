# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import dbus
import dbus.mainloop.glib
from gi.repository import GObject, Gtk
import logging
from lxml import etree
import os
import platform
import time

from smarthome.server import setup_server
from smarthome.zeroconf.service import ZeroconfService

from themyutils.threading import start_daemon_thread

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(asctime)s [%(name)s] %(message)s")
    logging.getLogger("geventwebsocket.handler").setLevel(logging.INFO)
    logging.getLogger("smarthome.server.web_server.event_transceiver.object_pad_value").setLevel(logging.INFO)
    logging.getLogger("smarthome.zeroconf.discoverer").setLevel(logging.INFO)

    GObject.threads_init()
    dbus.mainloop.glib.threads_init()

    name = platform.node()

    dbus_loop = dbus.mainloop.glib.DBusGMainLoop()
    bus = dbus.SystemBus(mainloop=dbus_loop)

    config = etree.parse(open(os.path.join(os.path.dirname(__file__), "../config_%s.xml" % name)))
    etree.strip_tags(config, etree.Comment)

    setup_server(name, bus, config)

    zeroconf_service = ZeroconfService(name, bus)

    start_daemon_thread(Gtk.main)

    while True:
        time.sleep(1)
