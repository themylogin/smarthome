# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging
import pika
import re
import time

import themyutils.json
from themyutils.threading import start_daemon_thread

from smarthome.architecture.object import Object
from smarthome.architecture.object.args import Arg

logger = logging.getLogger(__name__)

__all__ = []


class AmqpSubscriber(Object):
    args = {"exchange": Arg(str),
            "routing_keys": Arg(str)}

    def create(self):
        pass

    def init(self):
        start_daemon_thread(self._pika_thread)

    def _pika_thread(self):
        while True:
            try:
                mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
                mq_channel = mq_connection.channel()

                mq_channel.exchange_declare(exchange=self.args["exchange"], type="topic")

                for routing_key in filter(None, map(lambda s: s.strip(), re.split("[\s,]+", self.args["routing_keys"]))):
                    logger.debug("SUBSCRIBE TO %s", routing_key)
                    result = mq_channel.queue_declare(exclusive=True)
                    queue_name = result.method.queue

                    mq_channel.queue_bind(exchange=self.args["exchange"], queue=queue_name, routing_key=routing_key)
                    mq_channel.basic_consume(self._post_signal, queue=queue_name, no_ack=True)

                mq_channel.start_consuming()
            except Exception as e:
                self.set_error("AMQP error: %r" % e)
                time.sleep(1)

    def _post_signal(self, ch, method, properties, body):
        self.emit_signal(method.routing_key, **themyutils.json.loads(body))
