# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
import functools
import logging
import sys
import time

from smarthome.architecture.object.error import create_object_error
from smarthome.architecture.object.pointer import PropertyPointer
from smarthome.architecture.object.proxy import *

from themyutils.oop.observable import Observable


logger = logging.getLogger(__name__)


class ObjectManager(Observable("object_error_observer", ["object_error_added", "object_error_removed"]),
                    Observable("object_signal_observer", ["object_signal_emitted"]),
                    Observable("object_property_observer", ["object_property_changed"]),
                    Observable("object_pad_connection_observer", ["object_pad_connected", "object_pad_disconnected"]),
                    Observable("object_pad_value_observer", ["object_pad_value"])):
    def __init__(self, peers_manager, worker_pool):
        self.peers_manager = peers_manager
        self.peers_manager.object_manager = self

        self.worker_pool = worker_pool

        self.objects = {}
        self.objects_errors = defaultdict(lambda: None)

        self.object_signal_connections = defaultdict(lambda: defaultdict(list))

    def set_objects(self, objects):
        self.objects = {name: LocalObject(object)
                        for name, object in objects.iteritems()}

        for object in objects.itervalues():
            object.create()

        for object in objects.itervalues():
            object.start()

    def on_peers_updated(self):
        unavailable_objects = set([name
                                   for name, object in self.objects.iteritems()
                                   if isinstance(object, RemoteObject)])
        for peer_name, peer in self.peers_manager.peers.iteritems():
            for object_name, object_description in peer.objects.iteritems():
                if isinstance(self.objects.get(object_name), LocalObject):
                    logger.error("Peer %s has object %s with same name as local object", peer_name, object_name)
                else:
                    logger.info("Discovered remote object %s on peer %s", object_name, peer_name)
                    self.objects[object_name] = RemoteObject(object_name, object_description, peer_name, self)

                unavailable_objects.discard(object_name)

        for object_name in unavailable_objects:
            logger.info("Object %s is now unavailable", object_name)
            self.objects[object_name] = UnavailableObject(object_name)

    def on_object_error(self, name, error):
        if not (self.objects_errors[name] is None and error is None):
            if error is None:
                logger.info("Removing object %s errors", name)
                self.objects_errors[name] = None
            else:
                if self.objects_errors[name] is None:
                    self.objects_errors[name] = {}

                for key, key_error in error.iteritems():
                    key_error_object = create_object_error(key_error)
                    old_error_object = self.objects_errors[name].get(key)
                    if key_error_object != old_error_object:
                        logger.info("Setting object %s error %s: %s", name, key, key_error_object.format())
                        self.objects_errors[name][key] = key_error_object

    def connect_object_signal(self, object_name, signal_name, callable):
        self.object_signal_connections[object_name][signal_name].append(callable)

    def on_object_signal_emitted(self, object_name, signal_name, *args, **kwargs):
        for callable in self.object_signal_connections[object_name][signal_name]:
            callable(*args, **kwargs)

        self.notify_object_signal_emitted(object_name, signal_name, args, kwargs)

    def on_object_property_changed(self, object_name, property_name, old_value, new_value):
        object = self.objects[object_name]

        if isinstance(object, RemoteObject):
            object._properties_values[property_name] = new_value

        self.notify_object_property_changed(object, property_name, old_value, new_value)

        for notified_object in self.objects.itervalues():
            if isinstance(notified_object, LocalObject):
                notified_object = notified_object._object
                for args_bag_property_key, property_pointer in notified_object.args.args.iteritems():
                    if isinstance(property_pointer, PropertyPointer):
                        if (property_pointer.object_pointer.name == object_name and
                            property_pointer.name == property_name):
                            for observer in notified_object._property_change_observers[args_bag_property_key]:
                                observer(old_value, new_value)

    def on_object_pad_connected(self, src_object, src_pad, dst_object, dst_pad):
        self.notify_object_pad_connected(src_object, src_pad, dst_object, dst_pad)

    def on_object_pad_disconnected(self, src_object, src_pad, dst_object, dst_pad):
        self.notify_object_pad_disconnected(src_object, src_pad, dst_object, dst_pad)

    def on_object_output_pad_value(self, object_name, pad_name, value):
        for object in self.objects.itervalues():
            if isinstance(object, LocalObject):
                for pad, connections in object._object._incoming_pad_connections.iteritems():
                    if (object_name, pad_name) in connections:
                        self.worker_pool.run_task(functools.partial(self._write_object_pad, object._name, pad, value))

        if isinstance(self.objects[object_name], LocalObject):
            self.notify_object_pad_value(object_name, pad_name, value)

    def _write_object_pad(self, name, pad, value):
        try:
            self.objects[name].write_pad(pad, value)
        except:
            logger.info("Error writing to object %s pad %s", name, pad, exc_info=True)