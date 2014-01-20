from datetime import datetime
import logging
from Queue import Queue
import time

import prctl
from sqlalchemy import create_engine
from sqlalchemy import Column
from sqlalchemy import BigInteger, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import create_session, scoped_session
from architecture.thread import start_thread
from smarthome.architecture.subscriber import Subscriber
from smarthome.outside_world import serialize


class SqlPublisher(Subscriber):
    def __init__(self, dsn):
        self.dsn = dsn

        self.query_queue = Queue()

        start_thread(self._loop, "sql")

    def receive_event(self, source_name, event_name, kwargs):
        self.query_queue.put(Event.__table__.insert().values(
            datetime=datetime.now(),
            source=source_name,
            event=event_name,
            kwargs=serialize(kwargs),
        ))

    def _loop(self):
        while True:
            try:
                db = scoped_session(lambda: create_session(create_engine(self.dsn)))

                while True:
                    query = self.query_queue.get()
                    try:
                        db.execute(query)
                    except:
                        self.query_queue.put(query)
                        raise

            except Exception, e:
                logging.getLogger(__name__).exception("Exception")
                time.sleep(5)

Base = declarative_base()

class Event(Base):
    __tablename__       = "event"

    id                  = Column(BigInteger, primary_key=True)
    datetime            = Column(DateTime())
    source              = Column(String(length=255))
    event               = Column(String(length=255))
    kwargs              = Column(Text())
