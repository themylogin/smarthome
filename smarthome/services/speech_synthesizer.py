# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import hashlib
import os
import re
import subprocess
import tempfile
import urllib
import urllib2

from smarthome.architecture.object import Object
from smarthome.architecture.patterns.loops import Loop


class SpeechSynthesizerLoop(Loop):
    def execute(self, phrase, language, kwargs):
        directory = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..",
                                                  "sound", "speech_synthesizer", language))

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
                request = urllib2.Request("http://translate.google.com/translate_tts", urllib.urlencode({
                    "q": chunk.encode("utf-8"),
                    "tl": language,
                }))
                request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.22 " +
                                                 "(KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22")
                response = urllib2.urlopen(request).read()

                tmp_filename = os.path.join(tmp_directory, "%d.mp3" % i)
                open(tmp_filename, "w").write(response)
                mp3s.append(tmp_filename)

            quiet_filename = "%s.quiet.wav" % filename
            subprocess.call(["avconv", "-i", "concat:%s" % "|".join(mp3s), "-ac", "2", quiet_filename.encode("utf-8")])
            subprocess.call(["sox", quiet_filename.encode("utf-8"), filename.encode("utf-8"), "gain", "-n"])
            os.unlink(quiet_filename.encode("utf-8"))

            map(os.unlink, mp3s)
            os.rmdir(tmp_directory)

        self.parent.sound_player.play_sound(filename, **kwargs)
        self.parent.dispatcher.receive_event(self.parent, "said", explanation="„%s“" % phrase)

    def execute_error(self, e, phrase, language, kwargs):
        return "Произошла ошибка при синтезе речи: %s" % repr(e)

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


class SpeechSynthesizer(Object):
    def __init__(self, sound_player):
        self.sound_player = sound_player

        self.loop = SpeechSynthesizerLoop(self)

    def say(self, phrase, language="ru", **kwargs):
        self.loop(phrase, language, kwargs)
