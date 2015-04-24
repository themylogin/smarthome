# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import namedtuple
import logging
import requests
import sys
import threading
import time
from uuid import uuid4
import websocket

import themyutils.json
from themyutils.threading import start_daemon_thread

from smarthome.zeroconf.discoverer import ServiceDiscoverer

logger = logging.getLogger(__name__)


class Peer(namedtuple("Peer", ["manager", "http_url", "ws_url", "objects"])):
    pass


class PeerManager(object):
    def __init__(self, container, my_name, bus):
        self.container = container
        self.my_name = my_name

        self.service_discoverer = ServiceDiscoverer(bus,
                                                    on_resolved=self._on_peer_resolved,
                                                    on_removed=self._on_peer_removed,
                                                    on_error=self._on_error)

        self.peers = {}
        self.peers_events_connections = {}
        self.peers_control_connections = {}
        self.peers_control_connections_lock = threading.Lock()

    def notify_broken_peer(self, name, exc_info):
        logger.info("Notifying broken peer %s", name, exc_info=exc_info)

    def control_connection(self, name):
        peer = self.peers[name]

        with self.peers_control_connections_lock:
            if name not in self.peers_control_connections:
                self.peers_control_connections[name] = []

        return PeerControlConnection(peer.ws_url,
                                     self.peers_control_connections[name],
                                     self.peers_control_connections_lock)

    def _on_peer_resolved(self, service):
        if service.name != self.my_name:
            try:
                objects = requests.get(service.url + "/internal/my_objects").json()
            except Exception:
                logger.error("Unable to receive objects from peer %s", service.url, exc_info=True)
            else:
                self.peers[service.name] = Peer(self,
                                                service.url,
                                                service.url.replace("http://", "ws://"),
                                                objects)

                uuid = uuid4()
                self._remove_peers_connections_for_peer(service.name)
                self.peers_events_connections[uuid] = service.name
                start_daemon_thread(self._peer_connection_thread, uuid, service.name)

                self.container.object_manager.on_peers_updated()

    def _on_peer_removed(self, name):
        if name in self.peers:
            self._remove_peers_connections_for_peer(name)
            del self.peers[name]

            self.container.object_manager.on_peers_updated()

    def _on_error(self, error):
        logger.error("Service discoverer error: %s", error)

    def _remove_peers_connections_for_peer(self, peer_name):
        self.peers_events_connections = {id: name
                                         for id, name in self.peers_events_connections.iteritems()
                                         if name != peer_name}

    def _peer_connection_thread(self, uuid, peer_name):
        ws = None

        while uuid in self.peers_events_connections:
            try:
                if ws is None:
                    ws = websocket.create_connection(self.peers[peer_name].ws_url + "/internal/my_events")

                message = themyutils.json.loads(ws.recv())
                self.container.event_transceiver.receive_remote_event(message["event"], message["args"])
            except:
                self.notify_broken_peer(peer_name, sys.exc_info())
                ws = None
                time.sleep(1)


class PeerControlConnection(object):
    def __init__(self, url, pool, pool_lock):
        self.url = url
        self.pool = pool
        self.pool_lock = pool_lock

        self.connection = None

    def __enter__(self):
        with self.pool_lock:
            try:
                self.connection = self.pool.pop()
            except IndexError:
                logger.info("Creating new control connection: %s", self.url)
                self.connection = websocket.create_connection(self.url + "/control")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with self.pool_lock:
            self.pool.append(self.connection)

    def control(self, command, args):
        self.connection.send(themyutils.json.dumps({"command": command, "args": args}))
        return themyutils.json.loads(self.connection.recv())
