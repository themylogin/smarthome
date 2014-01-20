# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.object import Object
from smarthome.architecture.properties.write_only_property import WriteOnlyProperty


class AlsaOutput(Object):
    def __init__(self, ssh, output_name):
        self.ssh = ssh
        self.output_name = output_name

        self.properties.create("on", WriteOnlyProperty, default_value=False, setter=self._setter)

    def _setter(self, value):
        self.ssh.execute_command("amixer set %s %s" % (self.output_name, "unmute" if value else "mute"))

    def increase_volume(self, steps):
        self.ssh.execute_command("amixer set %s %d+" % (self.output_name, steps))

    def decrease_volume(self, steps):
        self.ssh.execute_command("amixer set %s %d-" % (self.output_name, steps))
