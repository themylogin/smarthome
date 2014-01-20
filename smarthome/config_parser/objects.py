# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from functools import reduce
import importlib

from smarthome.config_parser import ConfigParserException
from smarthome.config_parser.common import parse_constant, extract_logic_expression_objects, parse_logic_expression


class ObjectPlaceholder(str):
    pass


class ExpressionPlaceholder(str):
    pass


def create_objects(xml, dispatcher):
    objects = {}
    for object_xml in xml.xpath("/smarthome/object"):
        kwargs = dict(object_xml.attrib)

        name = kwargs["name"]
        del kwargs["name"]

        class_name = kwargs["class"]
        del kwargs["class"]

        kwargs = {k: (False, v) for k, v in kwargs.iteritems()}

        for x in object_xml.getchildren():
            k, v = parse_object_child(x)
            if k in kwargs:
                raise ConfigParserException(u"Свойство %s указано повторно" % k)
            kwargs[k] = v

        if name in objects:
            raise ConfigParserException(u"Объект %s уже существует" % name)
        objects[name] = (class_name, kwargs)

    dependencies = {}
    for name, (class_name, kwargs) in objects.iteritems():
        constructor = getattr(
            importlib.import_module("smarthome.%s" % class_name),
            "".join([w.capitalize() for w in class_name.split(".")[1].split("_")])
        )

        dependencies[name] = set()
        kwargs = {k: resolve_type(v, objects.keys(), dependencies[name]) for k, v in kwargs.iteritems()}

        objects[name] = (constructor, kwargs)

    for layer in toposort(dependencies):
        for name in layer:
            constructor, kwargs = objects[name]
            dispatcher.create_object(name, constructor, **{k: resolve_objects(v, dispatcher)
                                                           for k, v in kwargs.iteritems()})


def parse_object_child(child_xml):
    name = child_xml.tag
    if child_xml.getchildren():
        type_resolved = False
        value = [parse_object_child(child)[1] for child in child_xml.getchildren()]
    else:
        if "type" in child_xml.attrib:
            type_resolved = True
            value = {
                "string": lambda value: value,
                "expression": lambda value: ExpressionPlaceholder(value),
            }[child_xml.attrib["type"]](child_xml.text)
        else:
            type_resolved = False
            value = child_xml.text
    return (name, (type_resolved, value))


def resolve_type((resolved, val), objects_list, dependencies):
    if isinstance(val, ExpressionPlaceholder):
        for name in extract_logic_expression_objects(val):
            dependencies.add(name)

    if resolved:
        return val

    if isinstance(val, list):
        return [resolve_type(x, objects_list, dependencies) for x in val]

    constant = parse_constant(val)
    if not isinstance(constant, basestring):
        return constant

    for name in objects_list:
        if val == name or (val.startswith(name) and val.split(name)[1] and val.split(name)[1][0] in ["[", "."]):
            dependencies.add(name)
            return ObjectPlaceholder(val)

    return val


def toposort(dependencies):
    extra_items_in_deps = reduce(set.union, dependencies.itervalues()) - set(dependencies.iterkeys())
    dependencies.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in dependencies.iteritems() if not dep)
        if not ordered:
            break
        yield ordered
        dependencies = {item: (dep - ordered) for item, dep in dependencies.iteritems() if item not in ordered}
    if dependencies:
        raise ConfigParserException("Среди следующих объектов существуют циклические зависимости: %s" %", ".join(dependencies))


def resolve_objects(val, dispatcher):
    if isinstance(val, list):
        return [resolve_objects(x, dispatcher) for x in val]

    if isinstance(val, ObjectPlaceholder):
        return dispatcher.objects[val]

    if isinstance(val, ExpressionPlaceholder):
        properties_involved = []
        expression = parse_logic_expression(val, dispatcher, properties_involved)
        return (expression, properties_involved)

    return val
