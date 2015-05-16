# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import os
import Queue
import threading
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response
from werkzeug.wsgi import SharedDataMiddleware

import themyutils.json

from smarthome.architecture.object.proxy import LocalObject, UnavailableObject
from smarthome.architecture.object.result import PromiseResult
from smarthome.server.web_server.helpers import *

logger = logging.getLogger(__name__)


class WebServer(object):
    def __init__(self, container, host, port):
        self.container = container
        self.host = host
        self.port = port

        self.gevent = None
        self.WebSocketError = None

        self.task_waiters = {}
        self.task_waiters_lock = threading.Lock()
        self.task_results = {}
        self.container.worker_pool.add_task_observer(self)

        self.my_events_waiters_queues = []

        self.errors_change_waiters = []
        self.on_object_error_changed = lambda *args: self._notify_waiters(self.errors_change_waiters)
        self.container.object_manager.add_object_error_observer(self)

        self.properties_change_waiters = []
        self.on_object_property_changed = lambda *args: self._notify_waiters(self.properties_change_waiters)
        self.on_object_property_appeared = lambda *args: self._notify_waiters(self.properties_change_waiters)
        self.container.object_manager.add_object_property_observer(self)

        self.pad_connection_change_waiters = []
        self.on_object_pad_connected = lambda *args: self._notify_waiters(self.pad_connection_change_waiters)
        self.on_object_pad_disconnected = lambda *args: self._notify_waiters(self.pad_connection_change_waiters)
        self.container.object_manager.add_object_pad_connection_observer(self)

        self.url_map = Map([
            Rule("/internal/my_possessions", endpoint="my_possessions"),
            Rule("/internal/my_events", endpoint="my_events"),

            Rule("/control", endpoint="control"),
            Rule("/objects", endpoint="watch_objects"),

            Rule("/", endpoint="index"),
            Rule("/write_frontend_database", endpoint="write_frontend_database")
        ])

    def serve_forever(self):
        app = self.wsgi_app
        app = SharedDataMiddleware(app, {b"/static": os.path.join(os.path.dirname(__file__), b"static")})

        import gevent
        from geventwebsocket import WebSocketError
        from geventwebsocket.handler import WebSocketHandler

        self.gevent = gevent
        self.WebSocketError = WebSocketError
        return gevent.pywsgi.WSGIServer((self.host, self.port), app, handler_class=WebSocketHandler).serve_forever()

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        try:
            response = self.dispatch_request(request)
            response.headers.add(b"Access-Control-Allow-Origin", "*")
        except HTTPException as e:
            response = e
        return response(environ, start_response)

    def dispatch_request(self, request):
        endpoint, values = self.url_map.bind_to_environ(request.environ).match()
        return getattr(self, "execute_%s" % endpoint)(request, **values)

    def create_waiter(self):
        waiter = self.gevent.get_hub().loop.async()
        waiter.start(lambda: None)
        return waiter

    def wait(self, waiter):
        return self.gevent.get_hub().wait(waiter)

    def _notify_waiters(self, waiters):
        for waiter in waiters:
            waiter.send()

    def on_task_complete(self, task_id, result):
        with self.task_waiters_lock:
            waiter = self.task_waiters.pop(task_id, None)
            if waiter:
                self.task_results[task_id] = result
                waiter.send()

    def notify_my_event(self, event, args):
        for waiter, queue in self.my_events_waiters_queues:
            queue.put({"event": event, "args": args})
            waiter.send()

    @json_response
    def execute_my_possessions(self, request):
        return {"objects": self._dump_objects(lambda object: isinstance(object, LocalObject))}

    @json_response
    def execute_my_events(self, request):
        ws = request.environ.get("wsgi.websocket")
        if ws is None:
            raise MethodNotAllowed("This endpoint supports only websockets requests")

        waiter = self.create_waiter()
        queue = Queue.Queue()
        self.my_events_waiters_queues.append((waiter, queue))

        try:
            while True:
                self.wait(waiter)
                while not queue.empty():
                    ws.send(themyutils.json.dumps(queue.get()))
        except self.WebSocketError:
            pass
        finally:
            self.my_events_waiters_queues.remove((waiter, queue))

            if not ws.closed:
                ws.close()

        return Response()

    @json_response
    def execute_control(self, request):
        ws = request.environ.get("wsgi.websocket")
        if ws is None:
            return self._process_control(themyutils.json.loads(request.get_data()))

        try:
            while True:
                ws.send(themyutils.json.dumps(self._process_control(themyutils.json.loads(ws.receive()))))
        except self.WebSocketError:
            pass
        finally:
            if not ws.closed:
                ws.close()

        return Response()

    def _process_control(self, data):
        waiter = self.create_waiter()
        with self.task_waiters_lock:
            task_id = self.container.worker_pool.run_task(lambda: self._process_control_command(data))
            self.task_waiters[task_id] = waiter

        self.wait(waiter)
        result = self.task_results.pop(task_id)

        if isinstance(result, PromiseResult):
            self.container.exported_promises_manager.manage(result.uuid, result.promise.deferred)

        return result.serialize()

    def _process_control_command(self, data):
        command = data["command"]
        args = data["args"]

        if command == "get_property":
            object = self.container.object_manager.objects.get(args["object"])
            return getattr(object, args["property"])

        if command == "set_property":
            object = self.container.object_manager.objects.get(args["object"])
            return setattr(object, args["property"], args["value"])

        if command == "call_method":
            object = self.container.object_manager.objects.get(args["object"])
            method = getattr(object, args["method"])
            d = args["args"]

            if "*args" in d:
                args = d.pop("*args")
            else:
                args = []
            if "**kwargs" in d:
                kwargs = d.pop("**kwargs")
                if len(d) > 0:
                    raise BadRequest("You can't have both named args and **kwargs in method call")
            else:
                kwargs = d

            return method(*args, **kwargs)

        if command == "connect_pad":
            dst_object = self.container.object_manager.objects.get(args["dst_object"])
            return dst_object.connect_to_pad(args["dst_pad"], args["src_object"], args["src_pad"])

        if command == "disconnect_pad":
            dst_object = self.container.object_manager.objects.get(args["dst_object"])
            return dst_object.disconnect_from_pad(args["dst_pad"], args["src_object"], args["src_pad"])

    @json_response
    def execute_watch_objects(self, request):
        ws = request.environ.get("wsgi.websocket")
        if ws is None:
            return self._dump_objects()

        waiter = self.create_waiter()
        self.errors_change_waiters.append(waiter)
        self.properties_change_waiters.append(waiter)
        self.pad_connection_change_waiters.append(waiter)

        ws.send(themyutils.json.dumps(self._dump_objects()))

        try:
            while True:
                self.wait(waiter)
                ws.send(themyutils.json.dumps(self._dump_objects()))
        except self.WebSocketError:
            pass
        finally:
            self.errors_change_waiters.remove(waiter)
            self.properties_change_waiters.remove(waiter)
            self.pad_connection_change_waiters.remove(waiter)

            if not ws.closed:
                ws.close()

        return Response()

    def _dump_objects(self, filter=None):
        return {object_name: {"inspection": object.inspect(),
                              "properties_values": object.dump_properties(),
                              "incoming_pad_connections": object.dump_incoming_pad_connections(),
                              "errors": {key: error.format()
                                         for key, error in (self.container.object_manager.objects_errors[object_name]
                                                            or {}).iteritems()}}
                for object_name, object in self.container.object_manager.objects.iteritems()
                if not isinstance(object, UnavailableObject) and (filter is None or filter(object))}

    def execute_index(self, request):
        with open(os.path.join(os.path.dirname(__file__), b"templates", b"index.html"), b"r") as f:
            return Response(f.read().replace(b"{{ database }}",
                                             themyutils.json.dumps(self.container.shared_database.data.get("frontend", {}))),
                            content_type=b"text/html; charset=utf-8")

    def execute_write_frontend_database(self, request):
        with self.container.shared_database as data:
            data["frontend"] = themyutils.json.loads(request.get_data())
        return Response()
