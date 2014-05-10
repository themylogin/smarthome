# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule

from smarthome.architecture.subscriber import Subscriber
from smarthome.outside_world.serialize import serialize, unserialize


class WebApplication(Subscriber):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
        self.dispatcher.add_subscriber(self)

        self.url_map = Map([
            Rule("/properties", endpoint="show_properties"),
            Rule("/call/<object>/<method>", endpoint="call_method"),
            Rule("/set/<object>/<property>", endpoint="set_property"),
            Rule("/simulate/<object>/<event>", endpoint="simulate_event"),
        ])

        self.gevent = None
        self.properties_asyncs = set()

    def receive_event(self, source_name, event_name, kwargs):
        for async in self.properties_asyncs.copy():
            async.send()

    def serve_forever(self):
        import gevent
        from geventwebsocket.handler import WebSocketHandler

        self.gevent = gevent
        return gevent.pywsgi.WSGIServer(("", 8000), self._wsgi_app, handler_class=WebSocketHandler).serve_forever()

    def _wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self._dispatch_request(request)
        response.headers.add(b"Access-Control-Allow-Origin", "*")
        return response(environ, start_response)

    def _dispatch_request(self, request):
        endpoint, values = self.url_map.bind_to_environ(request.environ).match()
        return getattr(self, "execute_%s" % endpoint)(request, **values)

    def execute_show_properties(self, request):
        if "wsgi.websocket" in request.environ:
            async = self.gevent.get_hub().loop.async()
            self.properties_asyncs.add(async)

            try:
                ws = request.environ["wsgi.websocket"]

                last_message = None
                while True:
                    message = serialize(self._get_properties())
                    if message != last_message:
                        last_message = message
                        ws.send(message)

                    self.gevent.get_hub().wait(async)
            finally:
                self.properties_asyncs.remove(async)
        else:
            return Response(serialize(self._get_properties()), mimetype="application/json")

    def _get_properties(self):
        properties = {}
        for object_name, object in self.dispatcher.objects.iteritems():
            properties[object_name] = {}
            for property_name in object.properties:
                properties[object_name][property_name] = object.properties[property_name]

        return properties

    def execute_call_method(self, request, object, method):
        meth = getattr(self.dispatcher.objects[object], method)
        return Response(serialize(meth(**unserialize(request.form["kwargs"]))), mimetype="application/json")

    def execute_set_property(self, request, object, property):
        self.dispatcher.objects[object].properties[property] = unserialize(request.form["value"])
        return Response("")

    def execute_simulate_event(self, request, object, event):
        self.dispatcher.receive_event(self.dispatcher.objects[object], event, **unserialize(request.form["kwargs"]))
        return Response("")
