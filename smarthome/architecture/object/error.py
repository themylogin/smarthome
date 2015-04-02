# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import traceback

logger = logging.getLogger(__name__)

__all__ = [b"create_object_error", b"ObjectError", b"ExceptionObjectError"]


def create_object_error(error):
    if (isinstance(error, tuple) and
            len(error) == 3 and
            issubclass(error[0], Exception) and
            isinstance(error[1], Exception) and
            error[2].__class__.__name__ == "traceback"):
        return ExceptionObjectError(error[0], error[1], error[2])
    else:
        return ObjectError(error)


class ObjectError(object):
    def __init__(self, value):
        self.value = value

    def format(self):
        return self.value


class ExceptionObjectError(object):
    def __init__(self, etype, value, traceback):
        self.etype = etype
        self.value = value
        self.traceback = traceback

    def format(self):
        return "".join(traceback.format_exception(self.etype, self.value, self.traceback))

    def __eq__(self, other):
        return isinstance(other, ExceptionObjectError) and other.format() == self.format()

    def __ne__(self, other):
        return not (self == other)
