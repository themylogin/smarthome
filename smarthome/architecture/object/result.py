# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import traceback
from uuid import uuid4

logger = logging.getLogger(__name__)

__all__ = [b"Result", b"ExceptionResult", b"PromiseResult", b"ValueResult"]


class ResultUnserializeError(Exception):
    pass


class Result(object):
    def serialize(self):
        return {
            "class": self.__class__.__name__,
            "data": self.serialize_impl(),
        }

    @classmethod
    def unserialize(cls, serialized):
        g = globals()
        result_cls = g.get(serialized["class"])
        if result_cls and issubclass(result_cls, cls):
            return result_cls.unserialize_impl(serialized["data"])

        raise ResultUnserializeError()

    def serialize_impl(self):
        raise NotImplementedError

    @classmethod
    def unserialize_impl(cls, serialized):
        raise NotImplementedError


class ExceptionResult(Result):
    def __init__(self, exc_info=None, data=None):
        self.data = data or {"class": exc_info[0],
                             "value": repr(exc_info[1]),
                             "traceback": "".join(traceback.format_exception(*exc_info))}

    def serialize_impl(self):
        return self.data

    @classmethod
    def unserialize_impl(cls, serialized):
        return cls(None, serialized)


class PromiseResult(Result):
    def __init__(self, promise=None, uuid=None, events=None):
        self.promise = promise
        self.uuid = uuid or uuid4()
        self.events = events or promise.deferred.events.keys()

    def serialize_impl(self):
        return {"uuid": self.uuid,
                "events": self.events}

    @classmethod
    def unserialize_impl(cls, serialized):
        return cls(None, serialized["uuid"], serialized["events"])


class ValueResult(Result):
    def __init__(self, value):
        self.value = value

    def serialize_impl(self):
        return self.value

    @classmethod
    def unserialize_impl(cls, serialized):
        return cls(serialized)
