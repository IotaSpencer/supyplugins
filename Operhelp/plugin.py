###
# Copyright (c) 2016, Ken Spencer
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
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Operhelp')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

import supybot.ircmsgs as ircmsgs

class Operhelp(callbacks.Plugin):
    """Commands and helpers for #operhelp and #help"""
    threaded = True
    def sli(self, irc, msg, args):
        """
        Gives information on how to start a SLI(Session Limit Increase) request."""
        if "#" in msg.args[0]:
            channel = msg.args[0]
        else:
            channel = None
        if channel in ("#operhelp", "#help"):
            irc.reply("In order to start the process of getting a Session Limit Increase, you will need to make a post on the Support -> SLI forum, follow the template in the forum description. Also, do not make double posts, if you do not see your post on the way back out, its because the Support forum is set up to not show topics publically. Thank you!", private=True)
        else:
            irc.noReply()
    sli = wrap(sli)
    def helpme(self, irc, msg, args, what):
        """[what you need help with]
        Sends an alert to operators to notice #OperHelp activity"""
        if "#" in msg.args[0]:
            channel = msg.args[0]
        else:
            channel = "'private'"
            
        to_channels = [
        "#o",
        "#debug",
        "#a",
        "#Situation_Room"]
        if channel in ("#operhelp", "#help"):
            for chan in to_channels:
                irc.sendMsg(ircmsgs.privmsg(chan, "User %s (%s) has used '!helpme' in %s. [%s]" % (msg.nick, msg.prefix, channel, what)))
        else:
            irc.noReply()
                
    helpme = wrap(helpme, [optional('text')])
    def appeal(self, irc, msg, args):
        """
        Gives information on how to submit an appeal"""
        if "#" in msg.args[0]:
            channel = msg.args[0]
        else:
            channel = None
        if channel in ("#operhelp", "#help"):
            irc.reply("To submit a ban appeal, please send an appeal via ECode-Appeals on a supported network, or make a ban appeal post on the Support/Ban Appeal forum.")
            irc.reply("If you're currently banned from ElectroCode, but using this command, we highly suggest disconnecting from the network immediately after reading this, as connecting while banned, is obviously, 'ban evading', and is not tolerated, and as such will make your ban time longer. Thanks!")
    appeal = wrap(appeal)
Class = Operhelp


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
