# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.config_parser.common import parse_logic_expression


def keep_properties(xml, dispatcher, policy=None):
    for keep_property_xml in xml.xpath("/smarthome/keep"):
        keep_property(keep_property_xml, dispatcher, policy)


def keep_property(keep_property_xml, dispatcher, policy):
    object = dispatcher.objects[keep_property_xml.attrib["object"]]
    property = object.properties.access(keep_property_xml.attrib["property"])

    properties_involved = []
    value = parse_logic_expression(keep_property_xml.attrib["value"], dispatcher,
                                   properties_involved=properties_involved)

    def create_handler(property, value):
        def handler(**kwargs):
            property.set(value())
        return handler

    for dependent_property in properties_involved:
        dispatcher.connect_event(dependent_property.owner, "%s changed" % dependent_property.name,
                                 create_handler(property, value), policy)
