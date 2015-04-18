# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from gi.repository import Gtk, Gdk, GObject
import logging

from smarthome.architecture.object import Object, method, prop, on_prop_changed
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import property_pointer

logger = logging.getLogger(__name__)

__all__ = [b"SmoothOnOffDevice"]


class SmoothOnOffDevice(Object):
    args = {"property": Arg(property_pointer),
            "on_delay": Arg(int, None),
            "on_delay_format": Arg(unicode, ""),
            "off_delay": Arg(int, None),
            "off_delay_format": Arg(unicode, "")}

    def create(self):
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), style_provider,
                                                 Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def init(self):
        self.receive_property("on", self.args["property"])
        self._reset_timeout_data()

    def _reset_timeout_data(self):
        self.window = None
        self.label = None

        self.delay = None
        self.label_format = None
        self.value_when_finished = None

        self.timeout_id = None

    @prop(toggleable=True)
    def get_on(self):
        return self.args["property"]

    @prop(toggleable=True)
    def set_on(self, value):
        if self.timeout_id and self.value_when_finished != value:
            self.stop_timer()
            return

        if value == self.args["property"]:
            return

        if value:
            if self.args["on_delay"]:
                self._start_countdown(self.args["on_delay"], self.args["on_delay_format"], value)
            else:
                self.args["property"] = value
        else:
            if self.args["off_delay"]:
                self._start_countdown(self.args["off_delay"], self.args["off_delay_format"], value)
            else:
                self.args["property"] = value

    @on_prop_changed("property")
    def handle_property_changed(self, value):
        self.receive_property("on", value)

    def _start_countdown(self, *args, **kwargs):
        GObject.idle_add(lambda: self._do_start_countdown(*args, **kwargs))

    def _do_start_countdown(self, delay, label_format, value_when_finished):
        self.delay = delay
        self.label_format = label_format
        self.value_when_finished = value_when_finished

        self.window = Gtk.Window()

        self.window.set_decorated(False)
        self.window.set_position(Gtk.WindowPosition.CENTER)

        self.window.connect("delete_event", lambda: False)

        self.label = Gtk.Label()
        self.window.add(self.label)
        self._render_timer()
        self.label.show()

        self.window.connect("key-press-event", self._on_window_key_press)

        self.window.show()
        self.window.set_keep_above(True)
        self.window.set_modal(True)

        self.timeout_id = GObject.timeout_add(1000, self._decrease_timer)

    def _render_timer(self):
        text = self.label_format % self.delay
        self.window.set_title(text)
        self.label.set_text(text)

    def _on_window_key_press(self, widget, event):
        keyval = Gdk.keyval_name(event.keyval)
        if keyval == "Escape":
            self.stop_timer()

    def _decrease_timer(self):
        self.delay -= 1
        self._render_timer()

        if self.delay > 0:
            return True
        else:
            self.args["property"] = self.value_when_finished
            self.stop_timer()

    @method
    def stop_timer(self):
        if self.timeout_id:
            GObject.source_remove(self.timeout_id)

        if self.window:
            self.window.destroy()

        self._reset_timeout_data()

CSS = b"""
    *
    {
        color: inherit;
        font-size: inherit;
        background-color: initial;
        font-family: inherit;
        font-style: inherit;
        font-variant: inherit;
        font-weight: inherit;
        text-shadow: inherit;
        icon-shadow: inherit;
        box-shadow: initial;
        margin-top: initial;
        margin-left: initial;
        margin-bottom: initial;
        margin-right: initial;
        padding-top: initial;
        padding-left: initial;
        padding-bottom: initial;
        padding-right: initial;
        border-top-style: initial;
        border-top-width: initial;
        border-left-style: initial;
        border-left-width: initial;
        border-bottom-style: initial;
        border-bottom-width: initial;
        border-right-style: initial;
        border-right-width: initial;
        border-top-left-radius: initial;
        border-top-right-radius: initial;
        border-bottom-right-radius: initial;
        border-bottom-left-radius: initial;
        outline-style: initial;
        outline-width: initial;
        outline-offset: initial;
        background-clip: initial;
        background-origin: initial;
        background-size: initial;
        background-position: initial;
        border-top-color: initial;
        border-right-color: initial;
        border-bottom-color: initial;
        border-left-color: initial;
        outline-color:  initial;
        background-repeat: initial;
        background-image: initial;
        border-image-source: initial;
        border-image-repeat: initial;
        border-image-slice: initial;
        border-image-width: initial;
        engine: initial;
        gtk-key-bindings: initial;

        -GtkWidget-focus-line-width: 0;
        -GtkWidget-focus-padding: 0;
        -GtkNotebook-initial-gap: 0;
    }

    GtkWindow
    {
        background-color: rgb(17, 9, 15);
        font: Segoe UI 35;
    }

    GtkLabel
    {
        padding: 90px 100px;
    }
"""
