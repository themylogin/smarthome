# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import unittest

from smarthome.server.hotkey_manager import HotkeyManager


class GtkHotkeyTestCase(unittest.TestCase):
    def setUp(self):
        self.hotkey_manager = HotkeyManager(None)

    def test_modifiers(self):
        self.assertEqual(self.hotkey_manager._gtk_hotkey("A-W-BackSpace"), "<Alt><Super>BackSpace")
