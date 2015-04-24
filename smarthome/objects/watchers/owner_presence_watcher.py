# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import logging

from smarthome.architecture.object import Object, signal_handler
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer, object_pointer_list

logger = logging.getLogger(__name__)

__all__ = [b"OwnerPresenceWatcher"]


class OwnerPresenceWatcher(Object):
    args = {"front_door": Arg(object_pointer),
            "keys_holders": Arg(object_pointer_list),

            "leaving_timeout": Arg(int, 15),

            "speech_synthesizer": Arg(object_pointer),
            "everybody_leaving_message": Arg(unicode),
            "everybody_leaving_canceled_message": Arg(unicode)}

    KEYS_HOLDER_SUFFIX = "_keys_holder"

    def create(self):
        self.owners = set(map(self._keys_holder_owner, self.args["keys_holders"]))

        self._create_property("everybody_at_home")
        self._create_property("everybody_leaving")

        self._create_property("anybody_at_home")
        self._create_property("anybody_leaving")

        self._create_property("owners_at_home")
        self._create_property("owners_leaving")

        for owner in self.owners:
            self._create_property("%s_at_home" % owner)
            self._create_property("%s_leaving" % owner)

        self.everybody_leaving_timer = self.timer("everybody_leaving_timer",
                                                  15, self._on_everybody_leaving_timer_timeout)
        self.everybody_leaving_saying = False

    def init(self):
        self._set_at_home(set([self._keys_holder_owner(keys_holder)
                               for keys_holder in self.args["keys_holders"]
                               if keys_holder.get_property("has_keys")]))
        self._set_leaving(set())

    def _set_at_home(self, owners):
        return self.__set_state(owners, "at_home")

    def _set_leaving(self, owners):
        return self.__set_state(owners, "leaving")

    def __set_state(self, owners, state):
        if len(owners) == len(self.owners):
            self.receive_property("everybody_%s" % state, True)
        else:
            self.receive_property("everybody_%s" % state, False)

        if len(owners) > 0:
            self.receive_property("anybody_%s" % state, True)
        else:
            self.receive_property("anybody_%s" % state, False)

        self.receive_property("owners_%s" % state, owners)

        for owner in self.owners:
            if owner in owners:
                self.receive_property("%s_%s" % (owner, state), True)
            else:
                self.receive_property("%s_%s" % (owner, state), False)

    @signal_handler("front_door", "opened")
    def on_front_door_opened(self):
        self.receive_property("anybody_at_home", True)
        self._set_leaving(set())

    @signal_handler("front_door", "closed")
    def on_front_door_closed(self):
        people_wo_keys = set([self._keys_holder_owner(keys_holder)
                              for keys_holder in self.args["keys_holders"]
                              if not keys_holder.get_property("has_keys")])
        people_leaving = self.get_property("owners_at_home") & people_wo_keys

        if people_leaving == self.get_property("owners_at_home"):
            self._set_leaving(people_leaving)
            self.everybody_leaving_timer.start()
        else:
            self._set_at_home(self.get_property("owners_at_home") - people_leaving)

    @signal_handler("keys_holders", "keys_put")
    def on_keys_put(self, keys_holder):
        self.everybody_leaving_timer.stop()
        self._set_leaving(self.get_property("owners_leaving") - {self._keys_holder_owner(keys_holder)})
        self._set_at_home(self.get_property("owners_at_home") | {self._keys_holder_owner(keys_holder)})

        if self.everybody_leaving_saying:
            self.args["speech_synthesizer"].say(self.args["everybody_leaving_canceled_message"], interrupt=True)

    def _on_everybody_leaving_timer_timeout(self):
        self.everybody_leaving_saying = True
        self.args["speech_synthesizer"].\
            say(self.args["everybody_leaving_message"], interrupt=True).\
            on_complete(self._on_everybody_leaving_said_completely).\
            on_finish(self._on_everybody_leaving_said)

    def _on_everybody_leaving_said_completely(self):
        self._set_at_home(set())
        self._set_leaving(set())

    def _on_everybody_leaving_said(self):
        self.everybody_leaving_saying = False

    def _keys_holder_owner(self, keys_holder):
        if keys_holder._name.endswith(self.KEYS_HOLDER_SUFFIX):
            return keys_holder._name[:-len(self.KEYS_HOLDER_SUFFIX)]
        else:
            raise ValueError("Keys holder name must end with %s to be used with OwnerWatcher (%s does not)" % (
                self.KEYS_HOLDER_SUFFIX, keys_holder._name))
