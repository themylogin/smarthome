# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import namedtuple
import logging
import requests
import threading
import time
import websocket

import themyutils.json
from themyutils.threading import start_daemon_thread

from smarthome.zeroconf.discoverer import ServiceDiscoverer

logger = logging.getLogger(__name__)


class Peer(namedtuple("Peer", ["manager", "http_url", "ws_url", "possessions"])):
    pass


class PeerManager(object):
    def __init__(self, container, my_name, bus):
        self.container = container
        self.my_name = my_name

        self.service_discoverer = ServiceDiscoverer(bus,
                                                    on_resolved=self._on_peer_resolved,
                                                    on_error=self._on_discoverer_error)

        self.peers = {}
        self.peers_control_connections = {}
        self.peers_control_connections_lock = threading.Lock()

    def _on_peer_resolved(self, service):
        if service.name == self.my_name:
            return

        if service.name in self.peers:
            logger.info("Connection with peer %s already exists", service.name)
            return

        try:
            possessions = requests.get(service.url + "/internal/my_possessions").json()
        except Exception:
            logger.error("Unable to receive possessions from peer %s, retrying in 1 second", service.url, exc_info=True)
            self.container.worker_pool.run_task(lambda: (time.sleep(1), self._on_peer_resolved(service)))
        else:
            self.peers[service.name] = Peer(self,
                                            service.url,
                                            service.url.replace("http://", "ws://"),
                                            possessions)

            start_daemon_thread(self._peer_connection_thread, service.name)

            self.container.object_manager.on_peers_updated()

    def _on_discoverer_error(self, error):
        logger.error("Service discoverer error: %s", error)

    def _peer_connection_thread(self, peer_name):
        ws = None
        while True:
            try:
                if ws is None:
                    ws = websocket.create_connection(self.peers[peer_name].ws_url + "/internal/my_events")

                message = themyutils.json.loads(ws.recv())
                self.container.event_transceiver.receive_remote_event(message["event"], message["args"])
            except:
                logger.error("An exception occured in peer %s connection thread", peer_name, exc_info=True)
                ws = None

                time.sleep(1)

    def control_connection(self, name):
        peer = self.peers[name]

        with self.peers_control_connections_lock:
            if name not in self.peers_control_connections:
                self.peers_control_connections[name] = []

        return PeerControlConnection(peer.ws_url,
                                     self.peers_control_connections[name],
                                     self.peers_control_connections_lock)


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
                self.__connect()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            with self.pool_lock:
                self.pool.append(self.connection)

    def control(self, command, args):
        try:
            return self.__do_control(command, args)
        except:
            logger.error("Peer control connection error, retrying", exc_info=True)
            try:
                self.__connect()
                return self.__do_control(command, args)
            except:
                self.connection = None
                raise

    def __connect(self):
        self.connection = websocket.create_connection(self.url + "/control")

    def __do_control(self, command, args):
        self.connection.send(themyutils.json.dumps({"command": command, "args": args}))
        return themyutils.json.loads(self.connection.recv())
