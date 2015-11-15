# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import os

from themyutils.threading import start_daemon_thread

from smarthome.architecture.object.datastore import Datastore
from smarthome.common import USER_DATA_DIR
from smarthome.config.parser.objects import get_objects
from smarthome.config.parser.on import setup_ons
from smarthome.config.parser.routines import setup_routines
from smarthome.config.parser.themylog import get_themylog
from smarthome.objects.me import Me
from smarthome.server.container import Container
from smarthome.server.database import Database
from smarthome.server.imported_promises_manager import ImportedPromisesManager
from smarthome.server.exported_promises_manager import ExportedPromisesManager
from smarthome.server.hotkey_manager import HotkeyManager
from smarthome.server.object_manager import ObjectManager
from smarthome.server.peer_manager import PeerManager
from smarthome.server.remote_hotkey_manager import RemoteHotkeyManager
from smarthome.server.routine_manager import RoutineManager
from smarthome.server.themylog_publisher import ThemylogPublisher
from smarthome.server.web_server import WebServer
from smarthome.server.web_server.event_transceiver import EventTransceiver
from smarthome.server.worker_pool import WorkerPool

__all__ = [b"setup_server"]


def create_object(name, factory, container, args):
    return factory(container, name, args, Datastore(container.local_database, ("datastore", name)))


def setup_server(my_name, bus, config):
    container = Container()

    container.local_database = Database(os.path.join(USER_DATA_DIR, "local_database.json"))
    container.shared_database = Database(os.path.join(USER_DATA_DIR, "shared_database.json"))

    container.imported_promises_manager = ImportedPromisesManager()
    container.exported_promises_manager = ExportedPromisesManager()

    container.worker_pool = WorkerPool()

    container.peer_manager = PeerManager(container, my_name, bus)
    container.object_manager = ObjectManager(container)
    container.routine_manager = RoutineManager(container)
    container.hotkey_manager = HotkeyManager(container)
    container.remote_hotkey_manager = RemoteHotkeyManager(container)

    container.web_server = WebServer(container, "0.0.0.0", 46408)

    container.event_transceiver = EventTransceiver(container)
    container.exported_promises_manager.add_exported_promises_observer(container.event_transceiver)
    container.object_manager.add_object_error_observer(container.event_transceiver)
    container.object_manager.add_object_signal_observer(container.event_transceiver)
    container.object_manager.add_object_property_observer(container.event_transceiver)
    container.object_manager.add_object_pad_connection_observer(container.event_transceiver)
    container.object_manager.add_object_pad_value_observer(container.event_transceiver)

    themylog = get_themylog(config)
    if themylog:
        themylog_publisher = ThemylogPublisher(*themylog)
        container.object_manager.add_object_signal_observer(themylog_publisher)
        container.object_manager.add_object_property_observer(themylog_publisher)

    objects = {name: create_object(name, desc.cls, container, desc.args)
               for name, desc in get_objects(config).iteritems()}
    objects["_%s" % my_name] = create_object("_%s" % my_name, Me, container, {})
    container.object_manager.set_objects(objects)

    setup_ons(config, container)
    setup_routines(config, container)

    start_daemon_thread(container.web_server.serve_forever)
