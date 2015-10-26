# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from setuptools import find_packages, setup

setup(
    name="smarthome",
    version="0.4.0",
    author="themylogin",
    author_email="themylogin@gmail.com",
    packages=find_packages(exclude=["tests"]),
    scripts=[],
    test_suite="nose.collector",
    url='http://github.com/themylogin/smarthome',
    description='Smart home server & client',
    long_description=open("README.md").read(),
    install_requires=[
        "appdirs",
        "gevent",
        "gevent-websocket",
        "ipaddress",
        "lxml",
        "paramiko",
        "pyephem",
        "pyserial",
        "python-prctl",
        "requests",
        "websocket-client",
        "werkzeug",
    ],
    setup_requires=[
        "nose>=1.0",
    ],
)
