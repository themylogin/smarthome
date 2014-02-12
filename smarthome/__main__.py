# -*- coding: utf-8 -*-
import logging
from lxml import etree
import os

from themylog.client import setup_logging_handler

from smarthome.architecture.dispatcher import Dispatcher
from smarthome.architecture.thread import set_thread_title, start_thread
from smarthome.config_parser.objects import create_objects
from smarthome.config_parser.events import bind_events
from smarthome.config_parser.keep import keep_properties
from smarthome.config_parser.policies import apply_policies
from smarthome.outside_world.themylog_publisher import ThemylogPublisher
from smarthome.outside_world.web_application import WebApplication

logging.getLogger("pika").setLevel(logging.WARNING)
setup_logging_handler("smarthome_daemon")

set_thread_title("main")

dispatcher = Dispatcher()

dispatcher.add_subscriber(ThemylogPublisher())

web_application = WebApplication(dispatcher)
start_thread(web_application.serve_forever, "web")

config = etree.parse(open(os.path.join(os.path.dirname(__file__), "../config.xml")))
create_objects(config, dispatcher)
bind_events(config, dispatcher)
keep_properties(config, dispatcher)
apply_policies(config, dispatcher)

dispatcher.process_events()
