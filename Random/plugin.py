###
# Copyright (c) 2017, Ken Spencer
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import random

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.log as log

import string
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Random')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Random(callbacks.Plugin):
    """A collection of commands that return a random value. This is more of a utility plugin than a standalone plugin."""
    threaded = True

    def lower_letters_in_range(self, irc, msg, args, start_letter, end_letter):
        """<start_letter> <end_letter>"""
        if start_letter in string.ascii_lowercase and end_letter in string.ascii_lowercase:
            start_index = string.ascii_lowercase.find(start_letter)
            end_index = string.ascii_lowercase.find(end_letter)
            assert start_index != -1
            assert end_index != -1
            assert start_letter < end_letter
            return string.ascii_lowercase[start_index:end_index]


    def upper_letters_in_range(self, irc, msg, args, start_letter, end_letter):
        """<start_letter> <end_letter>"""
        if start_letter in string.ascii_uppercase and end_letter in string.ascii_uppercase:
            start_index = string.ascii_uppercase.find(start_letter)
            end_index = string.ascii_uppercase.find(end_letter)
            assert start_index != -1
            assert end_index != -1
            assert start_letter < end_letter
            return string.ascii_uppercase[start_index:end_index]


    def randint(self, irc, msg, args, start_int, end_int):
        """[<int> <int>]
        Returns a random integer for the range (-1000-1000 if range not given)"""
        if start_int and end_int:
            try:
                rstart = start_int
                rend = end_int
                rint = random.randint(rstart, rend)
                irc.reply(rint, prefixNick=False)
            except TypeError as e:
                irc.error("Couldn't generate a number. Reason: %s" % e)
                log.debug("%s" % e)
                return
            except ValueError as e:
                irc.error("invalid input -> %s" % e)
                log.debug("%s" % e)
                return
        else:
            rint = random.randint(-1000,1000)
            irc.reply(rint, prefixNick=False)
    randint = wrap(randint, [optional('int'), optional('int')])

    def randualpha(self, irc, msg, args, start_letter, end_letter):
        """[<letter> <letter>]
        Returns a random uppercase letter from the English Alphabet (A-Z if range not given)"""
        if start_letter and end_letter:
            try:
                end = end_letter
                start = start_letter
                letter = random.choice(self.upper_letters_in_range(start, end))
                irc.reply(letter, prefixNick=False)
            except TypeError as e:
                irc.error("Couldn't generate a letter. Reason: %s" % e)
                log.debug("%s" % e)
            except ValueError as e:
                irc.error("Numbers are to be used in the command 'Random randint'")
            except AssertionError:
                irc.error("available letters are A-Z")
                return

        else:
            letters = string.ascii_uppercase
            letter = random.choice(letters)
            irc.reply(letter, prefixNick=False)
    randualpha = wrap(randualpha, [optional('letter'), optional('letter')])

    def randlalpha(self, irc, msg, args, start_letter, end_letter):
        """[<letter> <letter>]
        Returns a random lowercase letter from the English Alphabet (a-z if range not given)"""

        if start_letter and end_letter:
            try:
                end = end_letter
                start = start_letter
                letter = random.choice(self.lower_letters_in_range(start, end))
                irc.reply(letter, prefixNick=False)
            except ValueError as e:
                irc.error("Numbers are to be used in the command 'Random randint'")
                log.error("%s" % e)
                return
            except AssertionError:
                irc.error("available letters are a-z")
        else:
            letters = string.ascii_lowercase
            letter = random.choice(letters)
            irc.reply(letter, prefixNick=False)
    randlalpha = wrap(randlalpha, [optional('letter'), optional('letter')])
Class = Random


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
