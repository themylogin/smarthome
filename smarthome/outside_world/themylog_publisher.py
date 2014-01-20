from datetime import datetime
import logging

from themylog.client import Client
from themylog.level import levels
from themylog.record import Record

from smarthome.architecture.subscriber import Subscriber

class ThemylogPublisher(Subscriber):
    def __init__(self, config=None):
        self.client = Client(config)

    def receive_event(self, source_name, event_name, kwargs):
        if "explanation" in kwargs:
            level = levels["info"]
            explanation = kwargs["explanation"]
        else:
            level = levels["debug"]
            explanation = event_name

        record = Record(datetime=datetime.now(),
                        application="smarthome",
                        logger=source_name,
                        level=level,
                        msg=event_name.replace(" ", "_"),
                        args=kwargs,
                        explanation=explanation)
        try:
            self.client.log(record)
        except:
            logging.getLogger(__name__).exception("Exception")
            pass
