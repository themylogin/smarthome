# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
import functools
import inspect
import logging
import Queue
import sys
import threading
import time
import types

from themyutils.threading import start_daemon_thread

from smarthome.architecture.deferred import Deferred
from smarthome.architecture.object.args.bag import ArgsBag
from smarthome.architecture.object.utils.timer import Timer


logger = logging.getLogger(__name__)

__all__ = [b"Object", b"method", b"signal_handler", b"prop", b"on_prop_changed", b"input_pad", b"output_pad"]


class Object(object):
    args = {}

    PROPERTY_QUERY_TIMEOUT = 5
    INIT_INTERVAL = 5
    POLL_INTERVAL = 0.01

    def __init__(self, name, args, object_manager):
        self._name = name
        self.args = ArgsBag(args, object_manager)
        self.__object_manager = object_manager

        for name, meth in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(meth, "smarthome_signal_handler"):
                object_or_objects = self.args[meth.smarthome_signal_handler_args_bag_object_key]
                signal = meth.smarthome_signal_handler_signal
                if isinstance(object_or_objects, list):
                    for object in object_or_objects:
                        self.connect_to_signal(object, signal, functools.partial(self._call_with_object,
                                                                                 meth, object._name))
                else:
                    self.connect_to_signal(object_or_objects, signal, meth)

        self._properties = {}
        for name, meth in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(meth, "smarthome_property"):
                property_name = meth.smarthome_property_name
                if property_name not in self._properties:
                    self._create_property(property_name)
                if hasattr(meth, "smarthome_property_getter"):
                    self._set_property_getter(property_name, meth)
                if hasattr(meth, "smarthome_property_querier"):
                    self._set_property_querier(property_name, meth)
                if hasattr(meth, "smarthome_property_setter"):
                    self._set_property_setter(property_name, meth, **self._property_attrs(meth, "setter_"))
                if hasattr(meth, "smarthome_property_toggleable"):
                    self._set_property_toggleable(property_name)

        self._property_change_observers = defaultdict(list)
        for name, meth in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(meth, "smarthome_property_change_observer"):
                self._property_change_observers[meth.smarthome_property_change_observer_args_bag_property_key].append(
                    self._wrap_property_change_observer(meth))

        self._methods = {name
                         for name, meth in inspect.getmembers(self, predicate=inspect.ismethod)
                         if hasattr(meth, "smarthome_method")}

        self._incoming_pad_connections = defaultdict(set)

        self._input_pads = {name: {"interface": meth.smarthome_input_pad_interface,
                                   "receiver": getattr(self, name),
                                   "has_initial_value": meth.smarthome_input_pad_has_initial_value,
                                   "initial_value": meth.smarthome_input_pad_initial_value,
                                   "has_disconnected_value": meth.smarthome_input_pad_has_disconnected_value,
                                   "disconnected_value": meth.smarthome_input_pad_disconnected_value}
                            for name, meth in inspect.getmembers(self, predicate=inspect.ismethod)
                            if hasattr(meth, "smarthome_input_pad")}
        self._output_pads = {name: {"interface": meth.smarthome_output_pad_interface,
                                    "generator": getattr(self, name)}
                             for name, meth in inspect.getmembers(self, predicate=inspect.ismethod)
                             if hasattr(meth, "smarthome_output_pad")}

        self.__initialized = False

        self.logger = logger.getChild(self._name)

    def _call_with_object(self, meth, object_name, *args, **kwargs):
        return meth(self.__object_manager.objects[object_name], *args, **kwargs)

    def _create_property(self, name, value=None):
        self._properties[name] = {"readable": False,
                                  "writable": False,
                                  "toggleable": False,
                                  "value": value}

    def _set_property_getter(self, name, getter):
        self._properties[name]["readable"] = True
        self._properties[name]["get"] = getter

    def _set_property_querier(self, name, querier):
        self._properties[name]["readable"] = True
        self._properties[name]["query"] = querier
        self._properties[name]["query_events"] = set()
        self._properties[name]["query_events_lock"] = self.lock()

    def _set_property_setter(self, name, setter, receive_before=False, receive_after=False):
        self._properties[name]["writable"] = True
        self._properties[name]["set"] = setter
        self._properties[name]["receive_before_set"] = receive_before
        self._properties[name]["receive_after_set"] = receive_after

    def _set_property_toggleable(self, name):
        self._properties[name]["toggleable"] = True

        method = lambda self: self.set_property(name, not self.get_property(name))
        method.smarthome_method = True
        method_name = "toggle_%s" % name
        setattr(self, method_name, types.MethodType(method, self))

        if hasattr(self, "_methods"):
            self._methods.add(method_name)

    def _property_attrs(self, meth, attr_prefix):
        attr_prefix = "smarthome_property_" + attr_prefix
        return {attr[len(attr_prefix):]: getattr(meth, attr)
                for attr in dir(meth)
                if attr.startswith(attr_prefix)}

    def _wrap_property_change_observer(self, meth):
        if meth.smarthome_property_change_observer_needs_old_value:
            def wrapped(old_value, new_value):
                return meth(new_value, old_value)
            return wrapped
        else:
            def wrapped(old_value, new_value):
                return meth(new_value)
            return wrapped

    def _create_output_pad(self, name, interface):
        self._output_pads[name] = {"interface": interface}

    def _write_output_pad(self, name, value):
        self.__object_manager.on_object_output_pad_value(self._name, name, value)

    def get_property(self, name):
        property = self._properties[name]

        if property["readable"]:
            if "get" in property :
                return self.__perform_action(lambda: self.__get_property(name))

        return self._properties[name]["value"]

    def set_property(self, name, value):
        if not self._properties[name]["writable"]:
            raise AttributeError("Property %s is read-only" % name)

        self.__perform_action(lambda: self.__set_property(name, value))

    def call_method(self, name, *args, **kwargs):
        return self.__perform_action(lambda: getattr(self, name)(*args, **kwargs))

    def connect_to_pad(self, pad, src_object, src_pad):
        src_pad_desc = self.__object_manager.objects[src_object].get_output_pad(src_pad)
        if src_pad_desc is None:
            raise ValueError("Object %s does not have pad %s" % (src_object, src_pad))

        dst_pad_desc = self.__object_manager.objects[self._name].get_input_pad(pad)
        if dst_pad_desc is None:
            raise ValueError("Object %s does not have pad %s" % (self._name, pad))

        if src_pad_desc["interface"] != dst_pad_desc["interface"]:
            raise ValueError("Pad %s interface %s does not conform to pad %s interface %s" % (
                src_pad, src_pad_desc["interface"], pad, dst_pad_desc["interface"]))

        connection = (src_object, src_pad)
        connections = self._incoming_pad_connections[pad]
        if connection in connections:
            raise ValueError("Object %s pad %s is already connected from object %s pad %s" % (
                self._name, pad, src_object, src_pad))
        connections.add(connection)

        self.__object_manager.on_object_pad_connected(src_object, src_pad, self._name, pad)

    def disconnect_from_pad(self, pad, src_object, src_pad):
        connection = (src_object, src_pad)
        connections = self._incoming_pad_connections[pad]
        if connection not in connections:
            raise ValueError("Pad connection does not exist")
        connections.remove(connection)

        dst_pad_desc = self.__object_manager.objects[self._name].get_input_pad(pad)
        if dst_pad_desc["has_disconnected_value"]:
            self.__object_manager.worker_pool.run_task(
                lambda: self.__object_manager._write_object_pad(self._name, pad, dst_pad_desc["disconnected_value"]))

        self.__object_manager.on_object_pad_disconnected(src_object, src_pad, self._name, pad)

    def write_pad(self, name, value):
        return self.__perform_action(lambda: self._input_pads[name]["receiver"](value))

    def __get_property(self, name):
        property = self._properties[name]
        value = self.__perform_action(property["get"])
        self.receive_property(name, value)
        return value

    def __set_property(self, name, value):
        property = self._properties[name]
        if property["receive_before_set"]:
            self.receive_property(name, value)
        property["set"](value)
        if property["receive_after_set"]:
            self.receive_property(name, value)

    def __perform_action(self, action):
        if not self.__initialized:
            try:
                self._init()
            except:
                self.__object_manager.on_object_error(self._name, {"initialization": sys.exc_info()})
                raise

        try:
            result = action()
        except:
            action_exc_info = sys.exc_info()
            try:
                self._init()
            except:
                self.__object_manager.on_object_error(self._name, {"initialization": sys.exc_info(),
                                                                   "action": action_exc_info})
                raise
            else:
                try:
                    result = action()
                except:
                    self.__object_manager.on_object_error(self._name, {"action": action_exc_info,
                                                                       "second_action_attempt": sys.exc_info()})
                    raise

        self.__object_manager.on_object_error(self._name, None)
        return result

    def receive_property(self, name, value):
        property = self._properties[name]

        old_value = property["value"]
        if value != old_value:
            property["value"] = value

            if "query" in property:
                with property["query_events_lock"]:
                    for event in property["query_events"]:
                        event.set()

            self.__object_manager.on_object_property_changed(self._name, name, old_value, value)

    def query_and_wait_for_property(self, name):
        property = self._properties[name]

        event = threading.Event()
        with property["query_events_lock"]:
            property["query_events"].add(event)

        property["query"]()

        result = event.wait(self.PROPERTY_QUERY_TIMEOUT)
        with property["query_events_lock"]:
            property["query_events"].remove(event)

        if result:
            return property["value"]
        else:
            self.__object_manager.on_object_error(self._name, {"property_query_timeout": name})
            raise ValueError("Timeout waiting for queried property value %s" % name)

    def connect_to_signal(self, object, signal, callable):
        self.__object_manager.connect_object_signal(object._name, signal, callable)

    def emit_signal(self, signal, *args, **kwargs):
        self.__object_manager.on_object_signal_emitted(self._name, signal, *args, **kwargs)

    def start(self):
        if self._try_init():
            self._on_start()
        else:
            self.logger.info("Unable to init object, forking initialization loop")
            start_daemon_thread(self._init_loop)

    def _try_init(self):
        try:
            self._init()
        except:
            self.__object_manager.on_object_error(self._name, {"initialization": sys.exc_info()})
            return False
        else:
            return True

    def _init(self):
        self.logger.debug("Initializing")
        self.init()
        self.__initialized = True

        for name, property in self._properties.iteritems():
            if property.get("query"):
                self.__object_manager.worker_pool.run_task(functools.partial(self.query_and_wait_for_property, name))

    def _init_loop(self):
        while True:
            if self._try_init():
                break
            else:
                time.sleep(self.INIT_INTERVAL)

    def _on_start(self):
        if hasattr(self, "poll"):
            self.logger.debug("Starting poll")
            start_daemon_thread(self._poll_loop)

        for name, pad in self._input_pads.iteritems():
            if pad["has_initial_value"]:
                self.__object_manager.worker_pool.run_task(functools.partial(pad["receiver"], pad["initial_value"]))

        for name, pad in self._output_pads.iteritems():
            generator = pad.get("generator")
            if generator:
                self.logger.debug("Starting output pad %s generator", name)
                start_daemon_thread(self._output_pad_loop, name, generator)

    def _poll_loop(self):
        while True:
            time.sleep(self.POLL_INTERVAL)

            if not self.__initialized:
                if not self._try_init():
                    time.sleep(self.INIT_INTERVAL)

            if self.__initialized:
                try:
                    self.poll()
                except:
                    self.__object_manager.on_object_error(self._name, {"polling": sys.exc_info()})

    def _output_pad_loop(self, name, generator):
        while True:
            try:
                for value in generator():
                    self._write_output_pad(name, value)
            except:
                self.__object_manager.on_object_error(self._name, {"output_pad_%s_loop" % name: sys.exc_info()})
            else:
                self.logger.warning("Output pad %s generator finished", name)

    def create(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def deferred(self, events):
        return Deferred(events, self.__object_manager)

    def event(self, *args, **kwargs):
        return threading.Event(*args, **kwargs)

    def lock(self):
        return threading.RLock()

    def queue(self, *args, **kwargs):
        return Queue.Queue(*args, **kwargs)

    def thread(self, *args, **kwargs):
        return start_daemon_thread(*args, **kwargs)

    def timer(self, name, timeout, callback):
        return Timer(self.__object_manager.worker_pool, self.logger.getChild(name), timeout, callback)


def method(meth):
    meth.smarthome_method = True
    return meth


def signal_handler(args_bag_object_key, signal):
    def decorator(meth):
        meth.smarthome_signal_handler = True
        meth.smarthome_signal_handler_args_bag_object_key = args_bag_object_key
        meth.smarthome_signal_handler_signal = signal
        return meth

    return decorator


def prop(*args, **kwargs):
    if len(args) > 0:
        if len(args) == 1 and callable(args[0]):
            return _do_prop(args[0], **kwargs)
        else:
            raise Exception("When @prop decorator is used with arguments, these arguments should be keyword arguments")
    else:
        if len(kwargs) > 0:
            return lambda meth: _do_prop(meth, **kwargs)
        else:
            raise Exception("@prop called without arguments")

def _do_prop(meth, toggleable=False, **kwargs):
    if meth.func_name.startswith("get_"):
        if meth.func_code.co_argcount != 1:
            raise TypeError("Property getter must not take arguments")

        meth.smarthome_property_getter = True
        meth.smarthome_property_name = meth.__name__[len("get_"):]

    elif meth.func_name.startswith("query_"):
        if meth.func_code.co_argcount != 1:
            raise TypeError("Property querier must not take arguments")

        meth.smarthome_property_querier = True
        meth.smarthome_property_name = meth.__name__[len("query_"):]

    elif meth.func_name.startswith("set_"):
        if meth.func_code.co_argcount != 2:
            raise TypeError("Property setter must take only one argument")

        meth.smarthome_property_setter = True
        _do_prop_attrs(meth, "setter_", kwargs)
        meth.smarthome_property_name = meth.__name__[len("set_"):]

    else:
        raise NameError("Property-decorated method names must start with get_ or set_")

    meth.smarthome_property = True

    if toggleable:
        meth.smarthome_property_toggleable = True

    return meth


def _do_prop_attrs(meth, prefix, attrs):
    for k, v in attrs.iteritems():
        setattr(meth, "smarthome_property_" + prefix + k, v)


def on_prop_changed(args_bag_property_key):
    def decorator(meth):
        if meth.func_code.co_argcount not in [2, 3]:
            raise TypeError("Property change observer should take exactly one or two arguments: value[, old_value]")

        meth.smarthome_property_change_observer = True
        meth.smarthome_property_change_observer_args_bag_property_key = args_bag_property_key
        meth.smarthome_property_change_observer_needs_old_value = meth.func_code.co_argcount == 3
        return meth

    return decorator


def input_pad(interface, **kwargs):
    def decorator(meth):
        meth.smarthome_input_pad = True
        meth.smarthome_input_pad_interface = interface
        meth.smarthome_input_pad_has_initial_value = "initial_value" in kwargs
        meth.smarthome_input_pad_initial_value = kwargs.get("initial_value")
        meth.smarthome_input_pad_has_disconnected_value = "disconnected_value" in kwargs
        meth.smarthome_input_pad_disconnected_value = kwargs.get("disconnected_value")
        return meth

    return decorator


def output_pad(interface):
    def decorator(meth):
        meth.smarthome_output_pad = True
        meth.smarthome_output_pad_interface = interface
        return meth

    return decorator
