# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from datetime import datetime
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule

from smarthome.outside_world.serialize import serialize, unserialize

class WebApplication(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher

        self.url_map = Map([
            Rule("/properties", endpoint="show_properties"),
            Rule("/call/<object>/<method>", endpoint="call_method"),
            Rule("/set/<object>/<property>", endpoint="set_property"),
            Rule("/simulate/<object>/<event>", endpoint="simulate_event"),
        ])

    def __call__(self, environ, start_response):
        return self._wsgi_app(environ, start_response)

    def _wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self._dispatch_request(request)
        response.headers.add(b"Access-Control-Allow-Origin", "*")
        return response(environ, start_response)

    def _dispatch_request(self, request):
        endpoint, values = self.url_map.bind_to_environ(request.environ).match()
        return getattr(self, "execute_%s" % endpoint)(request, **values)

    def execute_show_properties(self, request):
        properties = {}
        for object_name, object in self.dispatcher.objects.iteritems():
            properties[object_name] = {}
            for property_name in object.properties:
                properties[object_name][property_name] = object.properties[property_name]

        return Response(serialize(properties), mimetype="application/json")

    def execute_call_method(self, request, object, method):
        meth = getattr(self.dispatcher.objects[object], method)
        return Response(serialize(meth(**unserialize(request.form["kwargs"]))), mimetype="application/json")

    def execute_set_property(self, request, object, property):
        self.dispatcher.objects[object].properties[property] = unserialize(request.form["value"])
        return Response("")

    def execute_simulate_event(self, request, object, event):
        self.dispatcher.receive_event(self.dispatcher.objects[object], event, **unserialize(request.form["kwargs"]))
        return Response("")
