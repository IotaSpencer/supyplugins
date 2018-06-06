###
# Copyright (c) 2018, Ken Spencer
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.conf as conf
import supybot.callbacks as callbacks
import supybot.ircdb as ircdb
import supybot.log as log
import yaml
from collections import OrderedDict
import yamlordereddictloader

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Vote')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Vote(callbacks.Plugin):
    """Voting Plugin using yaml"""
    threaded = True

    def _vote(self, irc, voter, pid, yaynay):
        switch = False
        if yaynay:
            if yaynay == 'yay':
                if voter in self.polls[pid]['yays']:
                    irc.reply('Cannot create duplicate votes, only switch vote')
                    return
                elif voter in self.polls[pid]['nays']:
                    switch = True
                    self.polls[pid]['yays'].append(voter)
                    self.polls[pid]['nays'].remove(voter)
                    irc.reply("Switched vote for %s to %s" % (voter, yaynay))
            if yaynay == 'nay':
                if voter in self.polls[pid]['nays']:
                    irc.reply('Cannot create duplicate votes, only switch vote')
                    return
                elif voter in self.polls[pid]['yays']:
                    switch = True
                    self.polls[pid]['yays'].remove(voter)
                    self.polls[pid]['nays'].append(voter)
                    irc.reply("Switched vote for %s to %s" % (voter, yaynay))

        if not switch:
            self.polls[pid][yaynay + 's'].append(voter)
        with open(self.pollFile, 'w+') as f:
            yaml.dump(self.polls, f, default_flow_style=False)

    def _dump(self, obj):
        with open(self.pollFile, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False)

    def __init__(self, irc):
        self.__parent = super(Vote, self)
        self.__parent.__init__(irc)
        self.pollFile = conf.supybot.directories.data.dirize('polls.yml')
        try:
            self.polls = yaml.load(open(self.pollFile, 'r'), Loader=yamlordereddictloader.Loader)

        except FileNotFoundError as e:
            log.warning("Couldn't open file: %s" % e)
            raise

    def die(self, irc):
        self._dump(self.polls)

    def reloadpolls(self, irc, msg, args):
        """<takes no arguments>
        Reloads the Polls file.
        """
        try:
            self.polls = yaml.load(open(self.pollFile, 'r'), Loader=yamlordereddictloader.Loader)

        except FileNotFoundError as e:
            log.warning("Couldn't open file: %s" % e)
            raise

    def listpolls(self, irc, msg, args):
        """<takes no arguments>
        Lists current polls.
        """
        if msg.args[0] == self.registryValue('pollChannel') or msg.args[0] == '#Situation_Room':
            if self.polls is None:
                self.polls = []
            if self.polls is []:
                irc.reply("No Polls.")
            for idx, entry in enumerate(self.polls):
                print(entry)
                entry_string = []
                for key, value in entry.items():
                    print("{} => {}".format(key, value))
                    if key == 'question':
                        entry_string.append("%d: %s" % (idx, value))
                    if key == 'added_by':
                        entry_string.append("Question asked by %s" % value)
                    if key == 'yays':
                        entry_string.append("Yays: %s" % (' '.join(value) if value != [] else 'none'))
                    if key == 'nays':
                        entry_string.append("Nays: %s" % (' '.join(value) if value != [] else 'none'))

                print(entry_string)
                irc.reply(' / '.join(entry_string))
    listpolls = wrap(listpolls)

    def poll(self, irc, msg, args, subject):
        """<subject...>
        Add a poll.
        """
        if msg.args[0] == self.registryValue('pollChannel') or msg.args[0] == '#Situation_Room':
            if self.polls is None:
                self.polls = []
            self.polls.append({
                'question': subject,
                'yays': [],
                'nays': [],
                'concluded': False,
                'added_by': msg.nick})
            with open(self.pollFile, 'w+') as f:
                yaml.dump(self.polls, f)
    poll = wrap(poll, ['something'])

    def vote(self, irc, msg, args, pid, yaynay):
        """<id> <yay/nay>
        Vote on a poll.
        """
        voter = ''
        try:
            voter = ircdb.users.getUser(msg.prefix).name
        except KeyError:
            reply = [
                "I'm unable to look you up in my user database.",
                "If you're sure you have a user in my database please try '@nickauth auth' to authenticate."
                "If this doesn't work, then alert my owner, %s" % ircdb.users.getUser(1).name,
                ]
            irc.replies(reply, prefixer='Error: ')
        if yaynay not in ['yay', 'nay']:
            irc.error("Valid Answers are 'yay' or 'nay'.")
            return
        if self.polls[pid]['concluded']:
            irc.reply("Poll #%s is finished, it does not accept updates." % pid)
            return
        if self._vote(irc, voter, pid, yaynay):
            with open(self.pollFile, 'w+') as f:
                yaml.dump(self.polls, f)
        else:
            log.debug('Not dumping due to no change.')

    vote = wrap(vote, ['nonNegativeInt', 'something'])

    def conclude(self, irc, msg, args, pid):
        """<id>
        Marks a poll as finished.
        """

    conclude = wrap(conclude, ['nonNegativeInt'])

    def finished(self,irc,msg,args):
        """<takes no arguments>
        Lists finished polls.
        """
    finished = wrap(finished)

    def rempoll(self, irc, msg, args, pid):
        """<id>
        Removes a poll entirely.
        """

    rempoll = wrap(rempoll, ['admin', 'nonNegativeInt'])

Class = Vote


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
