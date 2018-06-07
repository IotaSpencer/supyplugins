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

    def __init__(self, irc):
        self.__parent = super(Vote, self)
        self.__parent.__init__(irc)
        self.pollFile = conf.supybot.directories.data.dirize('polls.yml')
        try:
            self.polls = yaml.load(open(self.pollFile, 'r'), Loader=yamlordereddictloader.Loader)

        except FileNotFoundError as e:
            log.warning("Couldn't open file: %s" % e)
            raise

    def _vote(self, irc, channel, voter, pid, yaynay):
        switch = False
        new = True
        if yaynay:
            if yaynay == 'yay':
                if voter in self.polls[channel][pid]['yays']:
                    new = False
                    irc.reply('Cannot create duplicate votes, only switch vote')
                    return False
                elif voter in self.polls[channel][pid]['nays']:
                    new = False
                    switch = True
                    self.polls[channel][pid]['yays'].append(voter)
                    self.polls[channel][pid]['nays'].remove(voter)
                    irc.reply("Switched vote for %s to %s" % (voter, yaynay))
                    with open(self.pollFile, 'w+') as f:
                        yaml.dump(self.polls, f, default_flow_style=False)
                    return True
            if yaynay == 'nay':
                if voter in self.polls[channel][pid]['nays']:
                    new = False
                    irc.reply('Cannot create duplicate votes, only switch vote')
                    return False
                elif voter in self.polls[channel][pid]['yays']:
                    new = False
                    switch = True
                    self.polls[channel][pid]['yays'].remove(voter)
                    self.polls[channel][pid]['nays'].append(voter)
                    irc.reply("Switched vote for %s to %s" % (voter, yaynay))
                    with open(self.pollFile, 'w+') as f:
                        yaml.dump(self.polls, f, default_flow_style=False)
                    return True
        if new:
            self.polls[channel][pid][yaynay + 's'].append(voter)
        with open(self.pollFile, 'w') as f:
            yaml.dump(self.polls, f, default_flow_style=False)

    def _dump(self, obj):
        with open(self.pollFile, 'w') as f:
            yaml.dump(obj, f, default_flow_style=False)

    def reloadpolls(self, irc, msg, args):
        """<takes no arguments>
        Reloads the Polls file.
        """
        try:
            self.polls = yaml.load(open(self.pollFile, 'r'), Loader=yamlordereddictloader.Loader)

        except FileNotFoundError as e:
            log.warning("Couldn't open file: %s" % e)
            raise

    def listpolls(self, irc, msg, args, channel):
        """<takes no arguments>
        Lists current polls.
        """
        if channel and msg.args[0] in irc.state.channels:
            if self.polls is None:
                self.polls = []
            if self.polls is []:
                irc.reply("No Polls.")
            for idx, entry in enumerate(self.polls[channel]):
                entry_string = []
                question = entry['question']
                yays = entry['yays']
                nays = entry['nays']
                added_by = entry['added_by']
                # concluded = entry['concluded']
                entry_string.append("%d: %s" % (idx, question))
                entry_string.append("Yays: %s" % (' '.join(yays) if yays != [] else 'none'))
                entry_string.append("Nays: %s" % (' '.join(nays) if nays != [] else 'none'))
                entry_string.append("Question asked by %s" % added_by)
                irc.reply(' / '.join(entry_string), notice=True, private=True, prefixNick=False)

        else:
            try:
                if ircdb.checkCapability(msg.prefix, 'admin') or ircdb.checkCapability(msg.prefix, 'owner'):
                    if self.polls is None:
                        self.polls = []
                    if self.polls is []:
                        irc.reply("No Polls.")
                    for idx, entry in enumerate(self.polls[channel]):
                        entry_string = []
                        question = entry['question']
                        yays = entry['yays']
                        nays = entry['nays']
                        added_by = entry['added_by']
                        # concluded = entry['concluded']
                        entry_string.append("%d: %s" % (idx, question))
                        entry_string.append("Yays: %s" % (' '.join(yays) if yays != [] else 'none'))
                        entry_string.append("Nays: %s" % (' '.join(nays) if nays != [] else 'none'))
                        entry_string.append("Question asked by %s" % added_by)
                        irc.reply(' / '.join(entry_string), notice=True, private=True, prefixNick=False)
                else:
                    irc.errorInvalid(channel, 'argument')

            except KeyError:
                return
    listpolls = wrap(listpolls, ['channel'])

    def poll(self, irc, msg, args, channel, subject):
        """<subject...>
        Add a poll.
        """
        if msg.nick in irc.state.channels[channel].ops:
            if self.polls is None:
                self.polls = {}
            if channel not in self.polls.keys():
                self.polls[channel] = []
            self.polls[channel].append({
                'question': subject,
                'yays': [],
                'nays': [],
                'concluded': False,
                'added_by': msg.nick})
            self._dump(self.polls)
            irc.reply("Poll added. %s" % subject)

    poll = wrap(poll, ['onlyInChannel', 'text'])

    def vote(self, irc, msg, args, channel, pid, yaynay):
        """<id> <yay/nay>
        Vote on a poll.
        """
        if yaynay not in ['yay', 'nay']:
            irc.error("Valid Answers are 'yay' or 'nay'.")
            return

        if channel in self.polls.keys():
            if self.polls[channel][pid]['concluded']:
                irc.reply("Poll #%s is finished, it does not accept updates." % pid)
                return
            if self._vote(irc, channel, msg.nick, pid, yaynay):
                irc.reply("Successfully voted on %s" % self.polls[channel][pid]['question'])
            else:
                log.debug('Not dumping due to no change.')
        else:
            irc.error("'%s' has no polls." % channel)
    vote = wrap(vote, ['onlyInChannel', 'nonNegativeInt', 'something'])

    def conclude(self, irc, msg, args, channel, pid):
        """<id>
        Marks a poll as finished. This is limited to channel ops.
        """
        if msg.nick in irc.state.channels[channel].ops:
            if channel in self.polls.keys():
                try:
                    self.polls[channel][pid]['concluded'] = True
                    self._dump(self.polls)
                except IndexError:
                    irc.error("'%s' does not have a poll with that index.")
                except KeyError:
                    irc.error("This may be a bug with the bot or poll file, please submit an issue at\
                     <https://github.com/IotaSpencer/supyplugins> with all pertinent information.")
        else:
            irc.error("Access Denied.")
    conclude = wrap(conclude, ['onlyInChannel', 'nonNegativeInt'])

    def finished(self, irc, msg, args, channel):
        """<takes no arguments>
        Lists finished polls.
        """
        for idx, entry in enumerate(self.polls[channel]):
            if entry['concluded']:
                irc.reply(" #{} / {} / {} / {} / {}".format(idx,
                                                            entry['question'],
                                                            entry['yays'],
                                                            entry['nays'],
                                                            entry['added_by']))
    finished = wrap(finished, ['onlyInChannel'])

    def rempoll(self, irc, msg, args, channel, pid):
        """<id>
        Removes a poll entirely.
        """
        if msg.nick in irc.state.channels[channel].ops:
            del self.polls[channel][pid]
        self._dump(self.polls)
    rempoll = wrap(rempoll, ['onlyInChannel', 'nonNegativeInt'])

Class = Vote


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
