# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from mock import Mock
import unittest

from smarthome.architecture.object.datastore import Datastore


class DatabaseMock(dict):
    def __init__(self, *args, **kwargs):
        super(DatabaseMock, self).__init__(*args, **kwargs)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class DatastoreReadTestCase(unittest.TestCase):
    def setUp(self):
        self.database = DatabaseMock()
        self.datastore = Datastore(self.database, ("datastore", "hdmi_matrix"))

    def test_does_not_contain_key(self):
        with self.assertRaises(KeyError):
            self.datastore["_property_output_1"]

    def test_contains_key(self):
        self.database["datastore"] = {"hdmi_matrix": {"_property_output_1": 1}}

        self.assertEqual(self.datastore["_property_output_1"], 1)

    def test_distinguishes_keys(self):
        self.database["datastore"] = {"hdmi_matrix": {"_property_output_1": 1,
                                                      "_property_output_2": 2}}

        self.assertEqual(self.datastore["_property_output_1"], 1)
        self.assertEqual(self.datastore["_property_output_2"], 2)
        with self.assertRaises(KeyError):
            self.datastore["_property_output_3"]
