###
# Copyright (c) 2004-2005, Jeremiah Fincher
# Copyright (c) 2017-, Ken Spencer
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
import supybot.world as world
import supybot.conf as conf
from supybot.commands import *
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs

import json


class Tail(callbacks.Plugin):
    def __init__(self, irc):
        self.__parent = super(Tail, self)
        self.__parent.__init__(irc)
        try:
            self.config = json.load(open(conf.supybot.directories.data.dirize(
                self.registryValue('configfile')), 'r'))
        except FileNotFoundError as e:
            self.log.warning("Couldn't open file: %s" % e)
            raise
        self.files = {}
        period = self.registryValue('period')
        schedule.addPeriodicEvent(self._checkfiles, period, name=self.name())
        for filename in self.config.keys():
            self._add(filename)

    def die(self):
        self.__parent.die()
        schedule.removeEvent(self.name())
        for fd in list(self.files.values()):
            fd.close()

    def __call__(self, irc, msg):
        irc = callbacks.SimpleProxy(irc, msg)
        self.lastIrc = irc
        self.lastMsg = msg

    def _checkfiles(self):
        self.log.debug('Checking files.')
        for filename in self.files.keys():
            self.log.debug('Checking {} ...'.format(filename))
            self._checkfile(filename)

    def _checkfile(self, filename):
        fd = self.files[filename]
        pos = fd.tell()
        line = fd.readline()
        while line:
            line = line.strip()
            if line:
                fdict = self.config[filename]
                for channet in fdict['channels']:
                    channel = channet.split(",")[1]
                    network = channet.split(",")[0]
                    self._send(self.lastIrc, fdict['identifier'], channel, line)
            pos = fd.tell()
            line = fd.readline()
        fd.seek(pos)

    def _add(self, filename):
        try:
            fd = open(filename, 'r')
        except EnvironmentError as e:
            self.log.warning('Couldn\'t open %s: %s', filename, e)
            raise
        fd.seek(0, 2) # 0 bytes, offset from the end of the file.
        self.files[filename] = fd

    def _remove(self, filename):
        fd = self.files.pop(filename)
        del self.config[filename]
        json.dump(self.config, open(self.registryValue('configfile'), 'w'))
        fd.close()

    def _send(self, irc, identifier, channel, text):
        if self.registryValue('bold'):
            identifier = ircutils.bold(identifier)
        notice = self.registryValue('notice')
        if notice:
            irc.queueMsg(ircmsgs.notice(channel, "%s: %s" % (identifier, text)))
        else:
            irc.queueMsg(ircmsgs.privmsg(channel, "%s: %s" % (identifier, text)))

    def add(self, irc, msg, args, filename, identifier, channet):
        """<filename> <identifier> <channel,network...>

        Add FILENAME as IDENTIFIER for announcing in
        Make sure the bot has rights to read whatever you tail.
        channels are written as #channel,network|#channel2,network2
        """
        try:
            self.config[filename] = {}
            self.config[filename]['identifier'] = identifier
            self.config[filename]['channels'] = channet
            json.dump(self.config, open(self.registryValue('configfile'), 'w'))
            self._add(filename)
        except EnvironmentError as e:
            irc.error(utils.exnToString(e))
            return
        irc.replySuccess()
    add = wrap(add, ['filename', 'something', many('something')])

    def remove(self, irc, msg, args, filename):
        """<filename>

        Stops announcing the lines appended to <filename>.
        """
        try:
            self._remove(filename)
            irc.replySuccess()
        except KeyError:
            irc.error(format('I\'m not currently announcing %s.', filename))
    remove = wrap(remove, ['filename'])


Class = Tail


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
