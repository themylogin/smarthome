# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.config_parser.common import parse_logic_expression
from smarthome.config_parser.events import bind_event
from smarthome.config_parser.keep import keep_property


def apply_policies(xml, dispatcher):
    for policy_xml in xml.xpath("/smarthome/policy"):
        condition = parse_logic_expression(policy_xml.attrib["condition"], dispatcher)

        for tag in policy_xml.getchildren():
            if tag.tag == "on":
                bind_event(tag, dispatcher, policy=condition)
            if tag.tag == "keep":
                keep_property(tag, dispatcher, policy=condition)
