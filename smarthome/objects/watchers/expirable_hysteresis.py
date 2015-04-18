# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime
import logging

from smarthome.architecture.object import Object, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import logic_expression

logger = logging.getLogger(__name__)

__all__ = [b"ExpirableHysteresis"]


class ExpirableHysteresis(Object):
    args = {"expression": Arg(logic_expression),
            "false_to_true_timeout": Arg(int),
            "false_to_true_interrupt_immediately": Arg(bool),
            "false_to_true_signal": Arg(str),
            "true_to_false_timeout": Arg(int),
            "true_to_false_interrupt_immediately": Arg(bool),
            "true_to_false_signal": Arg(str),
            "false_property": Arg(str),
            "true_property": Arg(str)}

    def create(self):
        self._create_property(self.args["false_property"])
        self._create_property(self.args["true_property"])

        self.wait_false_to_true_timer = self.timer("wait_false_to_true_timer",
                                                   self.args["false_to_true_timeout"],
                                                   self._set_true)
        self.wait_true_to_false_timer = self.timer("wait_true_to_false_timer",
                                                   self.args["true_to_false_timeout"],
                                                   self._set_false)

    def init(self):
        value = self.args["expression"]()

        self.receive_property(self.args["false_property"], not value)
        self.receive_property(self.args["true_property"], value)

        self.false_started_at = datetime.now() if not value else None
        self.true_started_at = datetime.now() if value else None

    def _set_true(self, at):
        if self.args["expression"]():
            self.receive_property(self.args["false_property"], False)
            self.receive_property(self.args["true_property"], True)

            self.emit_signal(self.args["false_to_true_signal"], start=self.false_started_at, end=at)

            self.true_started_at = at

    def _set_false(self, at):
        if not self.args["expression"]():
            self.receive_property(self.args["false_property"], True)
            self.receive_property(self.args["true_property"], False)

            self.emit_signal(self.args["true_to_false_signal"], start=self.true_started_at, end=at)

            self.false_started_at = at

    @on_prop_changed("expression")
    def on_expression_changed(self, value):
        if self.get_property(self.args["true_property"]):
            if self.wait_true_to_false_timer.started:
                if value:
                    if self.args["true_to_false_interrupt_immediately"]:
                        self.wait_true_to_false_timer.stop()
            else:
                if not value:
                    self.wait_true_to_false_timer.start()
        else:
            if self.wait_false_to_true_timer.started:
                if not value:
                    if self.args["false_to_true_interrupt_immediately"]:
                        self.wait_false_to_true_timer.stop()
            else:
                if value:
                    self.wait_false_to_true_timer.start()
