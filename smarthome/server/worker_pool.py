# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import Queue
import sys
import threading
import uuid

from themyutils.oop.observable import Observable
from themyutils.threading import start_daemon_thread

from smarthome.architecture.deferred import Promise
from smarthome.architecture.object.result import ExceptionResult, PromiseResult, ValueResult

logger = logging.getLogger(__name__)

__all__ = [b"WorkerPool"]


class WorkerPool(Observable("task_observer", ["task_complete"])):
    def __init__(self):
        self.total_workers = 0
        self.busy_workers = 0
        self.workers_lock = threading.Lock()
        self.queue = Queue.Queue()

    def run_task(self, task):
        with self.workers_lock:
            if not (self.busy_workers < self.total_workers):
                logger.info("Starting worker #%d", self.total_workers)
                start_daemon_thread(self._worker)
                self.total_workers += 1

        task_id = uuid.uuid1()
        self.queue.put((task_id, task))
        return task_id

    def _worker(self):
        while True:
            task_id, task = self.queue.get()

            with self.workers_lock:
                self.busy_workers += 1

            try:
                result = task()
                if isinstance(result, Promise):
                    result = PromiseResult(result)
                else:
                    result = ValueResult(result)
            except:
                logger.info("Exception in worker_pool", exc_info=True)
                result = ExceptionResult(sys.exc_info())
            self.notify_task_complete(task_id, result)

            with self.workers_lock:
                self.busy_workers -= 1
