# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.config_parser import ConfigParserException
from smarthome.config_parser.common import parse_constant, parse_logic_expression


def bind_events(xml, dispatcher, policy=None):
    for event_xml in xml.xpath("/smarthome/on"):
        bind_event(event_xml, dispatcher, policy)


def bind_event(event_xml, dispatcher, policy=None):
    kwargs = dict(event_xml.attrib)

    source = dispatcher.objects[kwargs["object"]]
    del kwargs["object"]

    event = kwargs["event"]
    del kwargs["event"]

    kwargs = {k: parse_constant(v) for k, v in kwargs.iteritems()}

    dispatcher.connect_event(source, event, create_handler(event_xml.getchildren(), dispatcher), policy, kwargs)


def create_handler(actions_xml, dispatcher):
    actions = [create_action(action_xml, dispatcher) for action_xml in actions_xml]
    def handler(**kwargs):
        for action in actions:
            action(**kwargs)

    return handler


def create_action(action_xml, dispatcher):
    if action_xml.tag == "call":
        kwargs = dict(action_xml.attrib)

        object = dispatcher.objects[kwargs["object"]]
        del kwargs["object"]

        method = getattr(object, kwargs["method"])
        del kwargs["method"]

        call_kwargs = {}
        for k, v in kwargs.iteritems():
            if k.endswith("-expression"):
                k = k[:-len("-expression")]
                call_kwargs[k] = parse_logic_expression(v, dispatcher)
            else:
                call_kwargs[k] = (lambda c: lambda **kwargs: c)(parse_constant(v))

        def action(**action_kwargs):
            method(**{k: v(**action_kwargs) for k, v in call_kwargs.iteritems()})

        return action

    if action_xml.tag == "set":
        kwargs = dict(action_xml.attrib)

        object = dispatcher.objects[kwargs["object"]]
        del kwargs["object"]

        property = kwargs["property"]
        del kwargs["property"]

        expression = parse_logic_expression(kwargs["value"], dispatcher)

        def action():
            object.properties[property] = expression()

        return action

    raise ConfigParserException("Неизвестное действие: %s" % action_xml.tag)
