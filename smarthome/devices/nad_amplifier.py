# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import socket

from smarthome.architecture.object import Object
from smarthome.architecture.patterns.loops import Loop
from smarthome.architecture.properties.write_only_property import WriteOnlyProperty


class NadAmplifierLoop(Loop):
    def execute(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.parent.host, self.parent.port))
        s.sendall(command)
        s.close()

    def execute_error(self, e, command):
        return "Ошибка отправки команды: %s" % repr(e)


class NadAmplifier(Object):
    def __init__(self, host, port=6789):
        self.host = host
        self.port = port

        self.properties.create("on", WriteOnlyProperty, default_value=None,
                               setter=lambda value: self._set_boolean_property("Main.Power", value))
        self.properties.create("muted", WriteOnlyProperty, default_value=None,
                               setter=lambda value: self._set_boolean_property("Main.Mute", value))
        self.properties.create("speaker_a_on", WriteOnlyProperty, default_value=None,
                               setter=lambda value: self._set_boolean_property("Main.SpeakerA", value))
        self.properties.create("speaker_b_on", WriteOnlyProperty, default_value=None,
                               setter=lambda value: self._set_boolean_property("Main.SpeakerB", value))
        self.properties.create("source", WriteOnlyProperty, default_value=None,
                               setter=lambda value: self._set_property("Main.Source", value))

        self.nad_amplifier_loop = NadAmplifierLoop(self)

    def _set_boolean_property(self, name, value):
        self._set_property(name, "On" if value else "Off")

    def _set_property(self, name, value):
        self._execute_command("%s=%s" % (name, value))

    def _execute_command(self, command):
        self.nad_amplifier_loop("\r%s\r" % command)

    def increase_volume(self):
        self._execute_command("Main.Volume+")

    def decrease_volume(self):
        self._execute_command("Main.Volume-")

    def toggle(self):
        self._execute_command("Main.Power+")

    def toggle_mute(self):
        self._execute_command("Main.Mute+")

    def toggle_output_a(self):
        self._execute_command("Main.SpeakerA+")

    def toggle_output_b(self):
        self._execute_command("Main.SpeakerB+")

    def toggle_source(self):
        self._execute_command("Main.Source+")
