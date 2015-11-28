# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from collections import defaultdict
from evdev import InputDevice, categorize, ecodes
import logging
import pyudev
import re
from select import select

from themyutils.threading import start_daemon_thread

from smarthome.server.hotkey.provider.base import BaseHotkeyProvider

logger = logging.getLogger(__name__)

__all__ = [b"LibevdevHotkeyProvider"]


class LibevdevHotkeyProvider(BaseHotkeyProvider):
    def __init__(self):
        self.hotkeys = defaultdict(list)

        context = pyudev.Context()

        self.input_devices = {}
        for device in context.list_devices(subsystem="input"):
            if device.device_node is not None:
                self._add_input_device(device)

        start_daemon_thread(self._input_devices_thread)

        self.pyudev_monitor = pyudev.Monitor.from_netlink(context)
        self.pyudev_monitor.filter_by("input")
        self.pyudev_observer = pyudev.MonitorObserver(self.pyudev_monitor, self._on_new_input_device_event)
        self.pyudev_observer.start()

    def bind(self, hotkey, func):
        self.hotkeys[hotkey].append(func)

    def unbind(self, hotkey):
        pass

    def _on_new_input_device_event(self, event, device):
        if event == "add":
            if device.device_node is not None:
                self._add_input_device(device)

    def _add_input_device(self, device):
        logger.info("Add input device: %s", device.device_node)

        try:
            input_device = InputDevice(device.device_node)
        except Exception:
            logger.error("Unable to initialize evdev input device for %s", device.device_node,
                         exc_info=True)
        else:
            self.input_devices[input_device.fd] = input_device

    def _input_devices_thread(self):
        pressed_keys = []
        keystroke_locked = False
        while True:
            r, w, x = select(self.input_devices, [], [], 1)

            for fd in r:
                try:
                    events = list(self.input_devices[fd].read())
                except Exception:
                    logger.warning("Input device has gone away", exc_info=True)
                    del self.input_devices[fd]
                    continue

                for event in events:
                    if event.type == ecodes.EV_KEY:
                        key_event = categorize(event)
                        keycode = key_event.keycode[0] if isinstance(key_event.keycode, list) else key_event.keycode
                        if key_event.keystate == key_event.key_up:
                            if pressed_keys and pressed_keys[-1] != keycode:
                                # Pressing Ctrl+Alt+D, releasing Alt, this is not Ctrl+D
                                keystroke_locked = True
                            pressed_keys = filter(lambda key: key != keycode, pressed_keys)
                            if len(pressed_keys) == 0:
                                keystroke_locked = False
                        elif key_event.keystate == key_event.key_down:
                            pressed_keys.append(keycode)
                        else:
                            continue
                        logger.debug("Currently pressed keys: %r, keystroke_locked: %r", pressed_keys, keystroke_locked)

                        if pressed_keys and not keystroke_locked:
                            hotkey = "-".join([re.sub(r"^(KEY_LEFT|KEY_RIGHT|KEY_)(.+)", "\\2", key).lower()
                                               for key in pressed_keys])
                            logger.debug("This is hotkey: %s", hotkey)

                            if hotkey in self.hotkeys:
                                logger.debug("Received hotkey %s", hotkey)
                                for callback in self.hotkeys[hotkey]:
                                    callback()
