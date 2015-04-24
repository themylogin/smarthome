# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import namedtuple
import logging
import importlib
import inspect

from smarthome.architecture.object import Object

logger = logging.getLogger(__name__)
ObjectDesc = namedtuple("ObjectDesc", ["cls", "args"])

__all__ = [b"get_objects"]


def get_objects(xml):
    return {object_xml.tag: get_object_desc(object_xml)
           for object_xml in xml.xpath("/smarthome/objects/*")}


def get_object_desc(xml):
    args = dict(xml.attrib)

    module = importlib.import_module("smarthome.objects.%s" % args["class"])
    cls = get_object_class(module)
    del args["class"]

    return ObjectDesc(cls=cls, args=get_object_args(cls, args))


def get_object_class(module):
    return inspect.getmembers(module, lambda x: inspect.isclass(x) and x != Object and issubclass(x, Object))[0][1]


def get_object_args(cls, args):
    result = {}
    for k, v in cls.args.iteritems():
        if k in args:
            result[k] = v.type(args[k])
        elif v.has_default_value:
            result[k] = v.default_value
        else:
            raise AttributeError(k)
    return result
