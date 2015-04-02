# -*- coding=utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

import hashlib
import os
import re
import requests
import subprocess
import tempfile

from smarthome.architecture.object import Object, method
from smarthome.architecture.object.args import Arg
from smarthome.architecture.object.args.types import object_pointer
from smarthome.common import DATA_DIR

__all__ = [b"SpeechSynthesizer"]


class SpeechSynthesizer(Object):
    args = {"sound_player": Arg(object_pointer)}

    def create(self):
        pass

    def init(self):
        pass

    @method
    def say(self, phrase, language="ru", interrupt=False):
        directory = os.path.normpath(os.path.join(DATA_DIR, "sound", "speech_synthesizer", language))

        if len(phrase) > 128:
            filename = os.path.join(directory, phrase[:64] + "..." +
                                               hashlib.md5(phrase.encode("utf-8")).hexdigest() + ".wav")
        else:
            filename = os.path.join(directory, phrase + ".wav")

        if not os.path.exists(filename.encode("utf-8")):
            if not os.path.exists(directory):
                os.makedirs(directory)

            mp3s = []
            tmp_directory = tempfile.mkdtemp()
            for i, chunk in enumerate(self._split_text_into_chunks(phrase)):
                response = requests.get("http://translate.google.com/translate_tts",
                                        params={"q": chunk.encode("utf-8"),
                                                "tl": language},
                                        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 " +
                                                               "(KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22"})
                if response.status_code != requests.codes.ok:
                    response.raise_for_status()

                tmp_filename = os.path.join(tmp_directory, "%d.mp3" % i)
                open(tmp_filename, "w").write(response.content)
                mp3s.append(tmp_filename)
                print tmp_filename

            quiet_filename = "%s.quiet.wav" % filename
            subprocess.call(["avconv", "-i", "concat:%s" % "|".join(mp3s), "-ac", "2", quiet_filename.encode("utf-8")])
            subprocess.call(["sox", quiet_filename.encode("utf-8"), filename.encode("utf-8"), "gain", "-n"])
            os.unlink(quiet_filename.encode("utf-8"))

            map(os.unlink, mp3s)
            os.rmdir(tmp_directory)

        return self.args["sound_player"].play(filename, interrupt)

    def _split_text_into_chunks(self, text, chunk_max_length=80):
        chunk = []
        for word in re.split("\s+", text):
            chunk_with_this_word = chunk + [word]
            if sum(map(len, chunk_with_this_word)) + (len(chunk_with_this_word) - 1) > chunk_max_length:
                yield " ".join(chunk)
                chunk = [word]
            else:
                chunk = chunk_with_this_word
        if chunk:
            yield " ".join(chunk)
