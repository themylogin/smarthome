# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from smarthome.architecture.properties.property import Property


class PropertyCopy(Property):
    def __init__(self, dispatcher, owner, name, original_property,
                 direct_transform=lambda x: x, inverse_transform=lambda x: x):
        self.dispatcher = dispatcher
        self.owner = owner
        self.name = name

        self.original_property = original_property
        self.direct_transform = direct_transform
        self.inverse_transrofm = inverse_transform

        self.original_property.dispatcher.connect_event(
            self.original_property.owner, "%s changed" % self.original_property.name,
            lambda **kwargs: self.dispatcher.receive_event(self.owner, "%s changed" % self.name, **self._transform_kwargs(kwargs))
        )

    def get(self):
        return self.direct_transform(self.original_property.get())

    def set(self, value, **kwargs):
        return self.original_property.set(self.inverse_transrofm(value), **kwargs)

    def _transform_kwargs(self, kwargs):
        kwargs["value"] = self.direct_transform(kwargs["value"])
        kwargs["old_value"] = self.direct_transform(kwargs["old_value"])
        return kwargs
