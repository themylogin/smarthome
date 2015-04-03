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

from smarthome.architecture.object.pointer import ObjectPointer, ObjectPointerList, PropertyPointer
from smarthome.common import DATA_DIR
from smarthome.config.parser.objects import get_objects
from smarthome.server.database import Database
from smarthome.server.imported_promises_manager import ImportedPromisesManager
from smarthome.server.exported_promises_manager import ExportedPromisesManager
from smarthome.server.object_manager import ObjectManager
from smarthome.server.peer_manager import PeerManager
from smarthome.server.web_server import WebServer
from smarthome.server.web_server.event_transceiver import EventTransceiver
from smarthome.server.worker_pool import WorkerPool
from smarthome.zeroconf.service import ZeroconfService

from themyutils.threading import start_daemon_thread

GObject.threads_init()
dbus.mainloop.glib.threads_init()
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(asctime)s [%(name)s] %(message)s")
logging.getLogger("smarthome.server.web_server.event_transceiver.object_pad_value").setLevel(logging.INFO)

my_name = platform.node()

dbus_loop = dbus.mainloop.glib.DBusGMainLoop()
bus = dbus.SystemBus(mainloop=dbus_loop)

database = Database(os.path.join(DATA_DIR, "database.json"))

imported_promises_manager = ImportedPromisesManager()
exported_promises_manager = ExportedPromisesManager()

peer_manager = PeerManager(my_name, bus, imported_promises_manager)

worker_pool = WorkerPool()

object_manager = ObjectManager(peer_manager, worker_pool)

web_server = WebServer("0.0.0.0", 46408, database, object_manager, exported_promises_manager)

event_transceiver = EventTransceiver(web_server, object_manager, imported_promises_manager, exported_promises_manager)
object_manager.add_object_signal_observer(event_transceiver)
object_manager.add_object_property_observer(event_transceiver)
object_manager.add_object_pad_connection_observer(event_transceiver)
object_manager.add_object_pad_value_observer(event_transceiver)
exported_promises_manager.add_exported_promises_observer(event_transceiver)
peer_manager.event_transceiver = event_transceiver

config = etree.parse(open(os.path.join(os.path.dirname(__file__), "../config_%s.xml" % my_name)))

objects = {name: cls(name, args, object_manager)
           for name, (cls, args) in get_objects(config).iteritems()}
object_manager.set_objects(objects)

start_daemon_thread(web_server.serve_forever)

zeroconf_service = ZeroconfService(my_name, bus)
start_daemon_thread(Gtk.main)

while True:
    time.sleep(1)
