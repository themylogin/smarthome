from datetime import datetime
import logging
from Queue import Queue
import time

import pika
import prctl
from architecture.thread import start_thread
from smarthome.architecture.subscriber import Subscriber
from smarthome.outside_world import serialize


class AmqpPublisher(Subscriber):
    def __init__(self, *args, **kwargs):
        self.connection_parameters = pika.ConnectionParameters(*args, **kwargs)

        self.publish_queue = Queue()

        start_thread(self._loop, "amqp")

    def receive_event(self, source_name, event_name, kwargs):
        self.publish_queue.put({
            "exchange"      : "smarthome_events",
            "routing_key"   : ".".join([source_name, event_name]),
            "body"          : serialize(kwargs),
        })

    def receive_news(self, source_name, event_name, text):
        self.publish_queue.put({
            "exchange"      : "smarthome_news",
            "routing_key"   : ".".join([source_name, event_name]),
            "body"          : serialize({"datetime": datetime.now(), "text": text}),
        })

    def receive_error(self, source_name, text):
        self.publish_queue.put({
            "exchange"      : "smarthome_errors",
            "routing_key"   : source_name,
            "body"          : serialize({"datetime": datetime.now(), "object": "source_name", "text": text}),
        })

    def _loop(self):
        while True:
            try:
                connection = pika.BlockingConnection(self.connection_parameters)

                channel = connection.channel()
                channel.exchange_declare(exchange="smarthome_events", type="topic")
                channel.exchange_declare(exchange="smarthome_news", type="topic")
                channel.exchange_declare(exchange="smarthome_errors", type="topic")

                while True:
                    connection.process_data_events()

                    if not self.publish_queue.empty():
                        kwargs = self.publish_queue.get()
                        channel.basic_publish(**kwargs)

                    time.sleep(0.01)

            except Exception, e:
                logging.getLogger(__name__).exception("Exception")
                time.sleep(1)
