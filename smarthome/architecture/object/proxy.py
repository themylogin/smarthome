# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
import functools
import logging
import sys

from smarthome.architecture.deferred import Deferred, Promise
from smarthome.architecture.object.result import *

logger = logging.getLogger(__name__)

__all__ = [b"LocalObject", b"RemoteObject", b"RemoteException", b"UnavailableObject"]


class ProxyObject(object):
    def __init__(self, name):
        self._name = name

    def __getattr__(self, name):
        if self.has_property(name):
            return self.get_property(name)

        if self.has_method(name):
            return self.get_method(name)

        raise AttributeError("Neither property nor method %s exists on object %s" % (name, self._name))

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
        else:
            if self.has_property(name):
                self.set_property(name, value)
            else:
                raise AttributeError("Property %s does not exist on object %s" % (name, self._name))

    def has_property(self, name):
        raise NotImplementedError

    def get_property(self, name):
        raise NotImplementedError

    def set_property(self, name, value):
        raise NotImplementedError

    def has_method(self, name):
        raise NotImplementedError

    def get_method(self, name):
        raise NotImplementedError

    def get_input_pad(self, name):
        raise NotImplementedError

    def get_output_pad(self, name):
        raise NotImplementedError

    def connect_to_pad(self, pad, src_object, src_pad):
        raise NotImplementedError

    def disconnect_from_pad(self, pad, src_object, src_pad):
        raise NotImplementedError

    def write_pad(self, name, value):
        raise NotImplementedError

    def inspect(self):
        raise NotImplementedError

    def dump_properties(self):
        raise NotImplementedError

    def dump_pad_connections(self):
        raise NotImplementedError


class LocalObject(ProxyObject):
    def __init__(self, object):
        super(LocalObject, self).__init__(object._name)
        self._object = object

    def has_property(self, name):
        return name in self._object._properties

    def get_property(self, name):
        return self._object.get_property(name)

    def set_property(self, name, value):
        self._object.set_property(name, value)

    def has_method(self, name):
        return name in self._object._methods

    def get_method(self, name):
        return functools.partial(self._object.call_method, name)

    def get_input_pad(self, name):
        return self._object._input_pads.get(name)

    def get_output_pad(self, name,):
        return self._object._output_pads.get(name)

    def connect_to_pad(self, pad, src_object, src_pad):
        self._object.connect_to_pad(pad, src_object, src_pad)

    def disconnect_from_pad(self, pad, src_object, src_pad):
        self._object.disconnect_from_pad(pad, src_object, src_pad)

    def write_pad(self, name, value):
        return self._object.write_pad(name, value)

    def inspect(self):
        return {"class": self._object.__class__.__name__,
                "properties": self._object._properties.keys(),
                "methods": self._object._methods,
                "input_pads": {name: {k: pad[k] for k in ["interface"]}
                               for name, pad in self._object._input_pads.iteritems()},
                "output_pads": {name: {k: pad[k] for k in ["interface"]}
                                for name, pad in self._object._output_pads.iteritems()}}

    def dump_properties(self):
        return {property_name: property["value"]
                for property_name, property in self._object._properties.iteritems()}

    def dump_incoming_pad_connections(self):
        return self._object._incoming_pad_connections


class RemoteException(Exception):
    pass


class RemoteObject(ProxyObject):
    def __init__(self, container, peer_name, name, description):
        super(RemoteObject, self).__init__(name)
        self._inspection = description["inspection"]
        self._properties_values = description["properties_values"]
        self._incoming_pad_connections = defaultdict(set, map(lambda (k, v): (k, set(v)),
                                                              description["incoming_pad_connections"].items()))
        self._container = container
        self._peer_name = peer_name

    def has_property(self, name):
        return name in self._inspection["properties"]

    def get_property(self, name):
        return self._control("get_property", {"object": self._name, "property": name})

    def set_property(self, name, value):
        return self._control("set_property", {"object": self._name, "property": name, "value": value})

    def has_method(self, name):
        return name in self._inspection["methods"]

    def get_method(self, name):
        return lambda *args, **kwargs: self._control("call_method", {"object": self._name,
                                                                     "method": name,
                                                                     "args": {"*args": args, "**kwargs": kwargs}})

    def get_input_pad(self, name):
        return self._inspection["input_pads"].get(name)

    def get_output_pad(self, name,):
        return self._inspection["output_pads"].get(name)

    def connect_to_pad(self, dst_pad, src_object, src_pad):
        return self._control("connect_pad", {"src_object": src_object,
                                             "src_pad": src_pad,
                                             "dst_object": self._name,
                                             "dst_pad": dst_pad})

    def disconnect_from_pad(self, dst_pad, src_object, src_pad):
        return self._control("disconnect_pad", {"src_object": src_object,
                                                "src_pad": src_pad,
                                                "dst_object": self._name,
                                                "dst_pad": dst_pad})

    def write_pad(self, name, value):
        raise TypeError("You should not write to remote object pads")

    def _control(self, command, args):
        try:
            with self._container.peer_manager.control_connection(self._peer_name) as connection:
                result = Result.unserialize(connection.control(command, args))
        except:
            raise RemoteException("Exception while communication with remote peer %s" % self._peer_name)
        else:
            if isinstance(result, ExceptionResult):
                raise RemoteException(result.data)
            if isinstance(result, PromiseResult):
                deferred = Deferred(self._container, result.events)
                self._container.imported_promises_manager.manage(result.uuid, deferred)
                return Promise(deferred)
            if isinstance(result, ValueResult):
                return result.value

    def inspect(self):
        return self._inspection

    def dump_properties(self):
        return self._properties_values

    def dump_incoming_pad_connections(self):
        return self._incoming_pad_connections


class UnavailableObjectException(Exception):
    pass


class UnavailableObject(ProxyObject):
    def has_property(self, name):
        return True

    def get_property(self, name):
        raise UnavailableObjectException(self._name)

    def set_property(self, name, value):
        raise UnavailableObjectException(self._name)

    def has_method(self, name):
        return True

    def get_method(self, name):
        def method(*args, **kwargs):
            raise UnavailableObjectException(self._name)

        return method

    def get_input_pad(self, name):
        raise UnavailableObjectException(self._name)

    def get_output_pad(self, name):
        raise UnavailableObjectException(self._name)

    def connect_to_pad(self, pad, src_object, src_pad):
        raise UnavailableObjectException(self._name)

    def disconnect_from_pad(self, pad, src_object, src_pad):
        raise UnavailableObjectException(self._name)

    def write_pad(self, name, value):
        raise UnavailableObjectException(self._name)

    def inspect(self):
        return {"class": "Unknown",
                "properties": [],
                "methods": [],
                "input_pads": {},
                "output_pads": {}}

    def dump_properties(self):
        return {}
