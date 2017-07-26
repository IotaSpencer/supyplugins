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

import supybot.utils as utils
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.httpserver as httpserver
import supybot.ircmsgs as ircmsgs

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('MsgServer')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class ServerCallback(httpserver.SupyHTTPServerCallback):
    name = "MSG Server"
    defaultResponse = 'NotImplemented!'

    def doPost(self, handler, path, form):
        self.plugin
instance = None
class MsgServer(callbacks.Plugin):
    """Send Msgs to a self hosted service."""
    threaded = True

    def __init__(self, irc):
        # Some stuff needed by Supybot
        global instance
        self.__parent = super(MsgServer, self)
        instance = self
        callbacks.Plugin.__init__(self, irc)

        # registering the callback
        callback = ServerCallback()  # create an instance of the callback
        callback.plugin = self
        httpserver.hook('msgserver', callback)  # register the callback at `/msgserver`
        for cb in self.cbs:
            cb.plugin = self

    def die(self):
        # unregister the callback
        httpserver.unhook('msgserver')  # unregister the callback hooked at /supystory

        # Stuff for Supybot
        self.__parent.die()

    def info(self, irc, msg, args):
        """takes no arguments
        Returns info on the plugin."""

        author = irc.getCallback('MsgServer').classModule.__author__.__str__()

        irc.reply(author)

    def doHTTPMsg(self, msg):
        irc = world.getIrc(self.registryValue('adminNet'))
        irc.queueMsg(ircmsgs.privmsg('Iota', msg))
    info = wrap(info)
Class = MsgServer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
