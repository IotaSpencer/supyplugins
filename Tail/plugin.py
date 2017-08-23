###
# Copyright (c) 2004-2005, Jeremiah Fincher
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
import supybot.ircutils as ircutils
import supybot.schedule as schedule
import supybot.callbacks as callbacks

import yaml
from yamlordereddictloader import Loader

class Tail(callbacks.Plugin):
    def __init__(self, irc):
        self.__parent = super(Tail, self)
        self.__parent.__init__(irc)
        self.files = {}
        period = self.registryValue('period')
        schedule.addPeriodicEvent(self._checkFiles, period, name=self.name())
        self.config = yaml.load(open(self.registryValue('configfile'), 'r'), Loader=Loader)
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

    def _checkFiles(self):
        self.log.debug('Checking files.')
        for filename in self.registryValue('files'):
            self._checkFile(filename)

    def _checkFile(self, filename):
        fd = self.files[filename]
        pos = fd.tell()
        line = fd.readline()
        while line:
            line = line.strip()
            if line:
                self._send(self.lastIrc, filename, line)
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
        fd.close()

    def _send(self, irc, identifier, filename, text):
        if self.registryValue('bold'):
            identifier = ircutils.bold(identifier)
        notice = self.registryValue('notice')
        payload = '\x02[\x0303%s\x03]\x02: %s' % (identifier, text)

    def add(self, irc, msg, args, filename, identifier, channel):
        """<filename> <identifier> <channel>

        Add FILENAME as IDENTIFIER for announcing in CHANNEL
        """
        try:
            self.config[filename] = {}
            self.config[filename]['identifier'] = identifier
            self.config[filename]['channel'] = channel
            yaml.dump(open(self.registryValue('configfile'), 'w'), self.config)
            self._add(filename)
        except EnvironmentError as e:
            irc.error(utils.exnToString(e))
            return
        irc.replySuccess()
    add = wrap(add, ['filename', 'something', 'channel'])

    def remove(self, irc, msg, args, identifier):
        """<identifier>

        Stops announcing the lines appended to <filename>.
        """
        try:
            self._remove(filename)
            irc.replySuccess()
        except KeyError:
            irc.error(format('I\'m not currently announcing %s.', filename))
    remove = wrap(remove, ['something'])


Class = Tail


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
