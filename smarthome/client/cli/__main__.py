# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import argparse
import functools
import logging
import getopt
import os
import requests
import sys

import themyutils.json

from smarthome.architecture.object.result import Result, ExceptionResult, PromiseResult, ValueResult
from smarthome.client import discover_services

logger = logging.getLogger(__name__)

__all__ = []


def process_string_arg(s):
    return s.decode("utf-8")


def call(args, unknown):
    call_kwargs, call_args = getopt.gnu_getopt(unknown, "", [o[2:] for o in unknown if o.startswith(b"--")])
    return control("call_method", {"object": args.object,
                                   "method": args.method,
                                   "args": {"*args": map(process_string_arg, call_args),
                                            "**kwargs": dict(((k[2:], process_string_arg(v)) for k, v in call_kwargs))}})


def control(command, args):
    sys.exit(run_on_service(functools.partial(do_control, command, args)))


def do_control(command, args, url):
    result = Result.unserialize(
        themyutils.json.loads(
            requests.post(url + "/control", data=themyutils.json.dumps({"command": command, "args": args})).text
        )
    )

    if isinstance(result, ExceptionResult):
        print result.data["traceback"]
        return 1

    if isinstance(result, ValueResult):
        print result.value
        return 0


def run_on_service(func):
    cachedir = os.path.expanduser("~/.cache/smarthome")
    if not os.path.exists(cachedir):
        os.mkdir(cachedir)

    cachefile = os.path.join(cachedir, "service.url")
    if os.path.exists(cachefile):
        url = open(cachefile, "r").read()
        try:
            return func(url)
        except:
            logging.error("Unable to communicate with cached service on URL %s", url, exc_info=True)
            os.unlink(cachefile)

    with discover_services() as services:
        for service in services:
            try:
                result = func(service.url)
            except:
                logging.error("Unable to communicate with service %s on URL %s", service.name, service.url,
                              exc_info=True)
            else:
                logging.info("Persisting service %s on URL %s as new default service", service.name, service.url)
                open(cachefile, "w").write(service.url)
                return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    call_parser = subparsers.add_parser("call")
    call_parser.add_argument("object")
    call_parser.add_argument("method")
    call_parser.set_defaults(func=call)

    args, unknown = parser.parse_known_args(sys.argv[1:])
    args.func(args, unknown)
