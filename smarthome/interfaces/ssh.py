# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import paramiko

from smarthome.architecture.object import Object
from smarthome.architecture.patterns.loops import LoopWithInit, PingMixin


class SshLoop(LoopWithInit, PingMixin):
    def init(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(self.parent.host, **self.parent.kwargs)

    def init_error(self, e):
        return "Ошибка подключения по SSH: %s" % repr(e)

    def execute(self, command, on_success, on_error):
        stdin, stdout, stderr = self.connection.exec_command(command)
        stdin.close()
        on_success("".join(stdout.readlines()), "".join(stderr.readlines()))

    def execute_error(self, e, command, on_success, on_error):
        on_error(e)
        return "Ошибка выполнения команды по SSH: %s" % repr(e)

    def ping(self):
        stdin, stdout, stderr = self.connection.exec_command("uptime")
        stdin.close()
        stdout.readlines()
        stderr.readlines()


class Ssh(Object):
    def __init__(self, host, **kwargs):
        self.host = host
        self.kwargs = kwargs

        self.ssh_loop = SshLoop(self)

    def execute_command(self, command, on_success=lambda stdout, stderr: None, on_error=lambda exception: None):
        self.ssh_loop(command, on_success, on_error)
