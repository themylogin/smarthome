# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import prctl
import threading


def start_thread(target, title):
    thread = threading.Thread(target=thread_target_with_title(target, title))
    thread.daemon = True
    thread.start()


def set_thread_title(title):
    prctl.set_name(title)


def thread_target_with_title(target, title):
    def target_with_title():
        set_thread_title(title)
        target()
    return target_with_title


def fork_thread(action):
    return lambda *args, **kwargs: start_thread(lambda: action(*args, **kwargs), action.__name__)
