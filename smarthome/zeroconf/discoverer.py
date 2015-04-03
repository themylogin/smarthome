# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import avahi
from collections import namedtuple
import dbus
import dbus.mainloop.glib
import gobject
import ipaddress
import logging
import Queue
import threading

logger = logging.getLogger(__name__)

__all__ = [b"Service", b"ZeroconfException", b"ServiceDiscoverer", b"SynchronousServiceDiscoverer",
           b"ServiceDiscoveryResult"]

Service = namedtuple("Service", ["name", "url"])


class ZeroconfException(Exception):
    pass


class ServiceDiscoverer(object):
    def __init__(self, bus, on_resolved=None, on_removed=None, on_error=None):
        self.bus = bus
        self.on_resolved = on_resolved or (lambda service: None)
        self.on_removed = on_removed or (lambda name: None)
        self.on_error = on_error or (lambda error_message: None)

        self.avahi_server = dbus.Interface(bus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                                           avahi.DBUS_INTERFACE_SERVER)

        self.service_browser = dbus.Interface(
            self.bus.get_object(
                avahi.DBUS_NAME,
                self.avahi_server.ServiceBrowserNew(
                    avahi.IF_UNSPEC,
                    avahi.PROTO_UNSPEC,
                    "_http._tcp",
                    "local",
                    dbus.UInt32(0)
                )
            ),
            avahi.DBUS_INTERFACE_SERVICE_BROWSER
        )
        self.service_browser.connect_to_signal("ItemNew", self._on_new_item)
        self.service_browser.connect_to_signal("ItemRemove", self._on_remove_item)

    def _on_new_item(self, interface, protocol, name, type, domain, flags):
        logger.debug("New item: %s", name)

        self.avahi_server.ResolveService(interface, protocol, name, type, domain, avahi.PROTO_UNSPEC,
                                         dbus.UInt32(0), reply_handler=self._on_service_resolved,
                                         error_handler=self._on_error)

    def _on_remove_item(self, interface, protocol, name, type, domain, flags):
        logger.debug("Remove item: %s", name)
        if self._is_smarthome_service(name):
            self.on_removed(self._service_name(name))

    def _on_service_resolved(self, interface, protocol, name, type, domain, host, aprotocol, address, port, txt, flags):
        if self._is_smarthome_service(name):
            name = self._service_name(name)
            address = ipaddress.ip_address(address)
            netloc = "%s:%d" % ("[%s]" % address if address.version == 6 else "%s" % address, port)
            logger.debug("Resolved service '%s' at %s", name, netloc)
            if address.version == 4:
                self.on_resolved(Service(name, "http://%s" % netloc))

    def _on_error(self, error_message):
        logger.error("Unable to resolve service: %s", error_message)
        self.on_error(error_message)

    def _is_smarthome_service(self, name):
        return name.startswith("smarthome-")

    def _service_name(self, name):
        return name[len("smarthome-"):]


class SynchronousServiceDiscoverer(object):
    def __init__(self, discover_timeout=None):
        self.discover_timeout = discover_timeout

        self.main_loop = None
        self.queue = Queue.Queue()

    def discover(self):
        gobject.threads_init()
        dbus.mainloop.glib.threads_init()

        dbus_thread = threading.Thread(target=self._dbus_discover)
        dbus_thread.daemon = True
        dbus_thread.start()

        try:
            service = self.get_next_service()
        except Queue.Empty:
            raise ZeroconfException("Discover timeout")
        else:
            return ServiceDiscoveryResult(service, self)

    def _dbus_discover(self):
        dbus_loop = dbus.mainloop.glib.DBusGMainLoop()
        bus = dbus.SystemBus(mainloop=dbus_loop)
        self.main_loop = gobject.MainLoop()
        resolver = ServiceDiscoverer(bus, on_resolved=self._on_service_resolved, on_error=self._on_error)
        self.main_loop.run()

    def get_next_service(self):
        service_or_error = self.queue.get(timeout=self.discover_timeout)
        if isinstance(service_or_error, Service):
            return service_or_error
        else:
            raise ZeroconfException(service_or_error)

    def _on_service_resolved(self, service):
        self.queue.put(service)

    def _on_error(self, error):
        self.queue.put(error)

    def close(self):
        if self.main_loop is not None:
            gobject.idle_add(self.main_loop.quit)
            self.main_loop = None


class ServiceDiscoveryResult(object):
    def __init__(self, first_service, discoverer):
        self.first_service = first_service
        self.discoverer = discoverer

    def __iter__(self):
        yield self.first_service
        while True:
            try:
                yield self.discoverer.get_next_service()
            except Queue.Empty:
                self.close()
                break

    def close(self):
        self.discoverer.close()
