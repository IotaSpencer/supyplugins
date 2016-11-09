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
    _ = PluginInternationalization('Oper')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x
import supybot.ircmsgs as ircmsgs
import re
import supybot.log as log
from itertools import *
import string
from strgen import StringGenerator as sg

class OperError():
    InputError = "An error has occured in your input."
    ReasonOverload =    "Number of reasons given is more than the number of users!"
    WrongChar =         "You've picked the wrong character for this response, try again."
    WrongSep =          "This character is not allowed to be used as a separator "  
class WrongSep(OperError):

        usedalot =  OperError.WrongSep + "(Used commonly in sentences)"
        isbracket = OperError.WrongSep + "(Used commonly as a bracket)"
        isquote =   OperError.WrongSep + "(Used as quote character)"
    
class Oper(callbacks.Plugin):
    """Oper Commands for ElectroCode"""
    threaded = True
    def getSubject(self, arg):
        subject = ""
        try:
            subject = arg.group(2)
            if subject == None:
                subject = ""
            else:
                subject = subject
        except AttributeError:
            subject = ""
        return subject
    def separator(self, irc, msg, args, character):
        """<character>
        Sets the separator for reasons in 'kill' and others to a certain character"""
        allowed_chars = "^*`+_"
        brackets = "[]{}()<>"
        usedalot = ".,"

        if character in allowed_chars:
            self.setRegistryValue('separator', value=character)
            irc.replySuccess()
        elif character in brackets:
            irc.error(WrongSep.isbracket, prefixNick=False)
        elif character in usedalot:
            irc.error(WrongSep.usedalot, prefixNick=False)
        else:
            irc.error(OperError.WrongSep, prefixNick=False)                
    separator = wrap(separator, ['letter'])
    def g(self, irc, msg, args, subject, message):
        """[@subject] <message>
        Sends a global notice / If '"@2+word subject" Some message' format is used, then subject allows multiple words."""
        caller = msg.nick
        subject = self.getSubject(subject)
        if subject != "":
            subject = "[%s] - " % (subject)
        irc.queueMsg(ircmsgs.notice("Global", "global %s%s (sent by %s)" % (subject, message, caller)))
    
    g = wrap(g, [optional(('matches', re.compile('^(@(.*))?$'), 'You should not see this, please notify an admin.')), 'text'])

    def kill(self, irc, msg, args, listofusers, messages):
        """user[,users...] [some reason[some more reasons^...]]
        Kills users given with reason given, if users > reasons, last reason is used on remaining users."""
        separator = self.registryValue('separator')
        users = listofusers.split(",")
        reasons = messages.split(separator)
        if len(reasons) > len(users):
            irc.error(OperError.ReasonOverload, prefixNick=False)
        elif len(users) >= len(reasons):    
            for user, reason in zip_longest(users, reasons, fillvalue=reasons[-1]):
                irc.queueMsg(ircmsgs.IrcMsg("kill %s :%s" % (user, reason)))
        else:
            irc.error(OperError.InputError, prefixNick=False)
    kill = wrap(kill, ['something', optional('text')])
    def passgen(self, irc, msg, args, length, template):
        """[length] [template]
        Generate a password. See 'charsets' for character groups."""
        
        if template == None:
            result = sg("[\w\d]{%s}" % (length)).render()
            irc.reply(result, prefixNick=False)
        elif template:
        		result = sg("%s" % (template)).render()
        		irc.reply(result, prefixNick=False)
        else:
        		irc.errorPossibleBug()
    passgen = wrap(passgen, [optional('int'), optional('text')])
    def charsets(self, irc, msg, args):
    		"""
    		Character code sets"""
    		sets = [
    				"\W: whitespace + punctuation",
						"\\a: ascii_letters",
						"\c: lowercase",
						"\d: digits",
						"\h: hexdigits",
						"\l: letters",
						"\o: octdigits",
						"\p: punctuation",
						"\\r: printable",
						"\s: whitespace",
						"\\u: uppercase",
						"\w: _ + letters + digits"
    		]
    		for line in sets:
    		    irc.reply(line, prefixNick=False, notice=True, private=True)
    charsets = wrap(charsets)    
Class = Oper


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
