# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals


class Loop(object):
    def __init__(self, parent, thread_name=None):
        self.parent = parent

        self.queue = self.parent.create_queue()
        self.parent.start_thread(self._thread_target, thread_name)

    def _thread_target(self):
        while True:
            args, kwargs = self.queue.get()

            try:
                self.execute(*args)
            except Exception as e:
                self.parent.raise_error_and_sleep(self.execute_error(e, *args, **kwargs))

    def __call__(self, *args, **kwargs):
        self.queue.put((args, kwargs))

    def execute(self, *args, **kwargs):
        pass

    def execute_error(self, e, *args, **kwargs):
        pass


class LoopWithInit(Loop):
    def _thread_target(self):
        while True:
            try:
                self.init()
            except Exception as e:
                self.parent.raise_error_and_sleep(self.init_error(e))
            else:
                while True:
                    args, kwargs = self.queue.get()

                    try:
                        self.execute(*args, **kwargs)
                    except Exception, e:
                        try:
                            self.init()
                        except Exception as e:
                            self.parent.raise_error_and_sleep(self.init_error(e))
                        else:
                            try:
                                self.execute(*args, **kwargs)
                            except Exception as e:
                                self.parent.raise_error_and_sleep(self.execute_error(e, *args, **kwargs))

    def init(self):
        pass

    def init_error(self, e):
        pass
