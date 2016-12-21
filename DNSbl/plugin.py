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
    _ = PluginInternationalization('DNSbl')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

import dns.resolver as dns
import ConfigParser
import supybot.conf as conf
import supybot.log as log

def rev(ip):
    ip = ip.split('.')
    ip.reverse()
    return ip
    
def makeIP(host):
    isIP = None
    if re.match(re.compile(r'[A-Za-z]+'), host):
        isIP = False
    else:
        isIP = True
    if isIP:
        return host
    else:
        try:
            mya = dns.query(host, 'A')
            reply = []
            for rdata in mya:
                reply.append(rdata)
            if len(reply) > 1:
                return -1
            elif len(reply) == 1:
                return reply
        except NXDOMAIN:
            return -1
        
        
class DNSbl(callbacks.Plugin):
    """DNS Blacklist checker"""
    threaded = True
    
    def check(self, irc, msg, args, ip, dnsbl):
        """<ip/host>
        
        Perform a dnsbl check
        """
        result = makeIP(ip)
        irc.reply(result)
        
    check = wrap(check, ['somethingWithoutSpaces', optional('somethingWithoutSpaces')])
    
    class dnsbl(callbacks.Commands):
        """
        Allows adding, removing, and listing of dnsbls
        """
        
        config = ConfigParser.ConfigParser()
        plugins_dir = conf.supybot.directories.plugins()
        cfgfile = plugins_dir[0]+'/DNSbl/local/bls.ini'

        
        def add(self, irc, msg, args, blname, bl):
            """<name> <blacklist host>
            
            Adds a blacklist into the plugins config
            """
            config.read(self.cfgfile)
            config.set('blacklists', blname, bl)
            config.add_section(blname)
            
        add = wrap(add, ['admin', 'somethingWithoutSpaces', 'somethingWithoutSpaces'])
        
        def rem(self, irc, msg, args, bl):
            """<blacklist name>
            
            Remove a blacklist
            """
            
        rem = wrap(rem, ['admin', 'somethingWithoutSpaces'])
        
        def bls(self, irc, msg, args):
            """takes no arguments
            
            Lists the blacklists in use
            """
            config = self.config
            config.read(self.cfgfile)
            listbls = []
            for k,v in config.items('blacklists'):
                listbls.append('%s - %s' % (k, v))
            msg_bls = 'Blacklists: %s' % (' \xB7 '.join(listbls))
            irc.reply(msg_bls, prefixNick=False)
            
        bls = wrap(bls, ['admin'])
        
        def addrec(self, irc, msg, args, bl, record, rreply):
            """<blacklist name> <reply answer> <reply string>
            
            Add a reply for a record on the given blacklist
            """
            config = self.config
            config.read(self.cfgfile)
            config.set(bl, record, rreply)
        addrec = wrap(addrec, ['admin', 'somethingWithoutSpaces', 'somethingWithoutSpaces', 'text'])
        
        def remrec(self, irc, msg, args, bl, record):
            """<blacklist name> <reply answer>
            
            Removes a reply from the given blacklist
            """
            config = self.config
            config.read(self.cfgfile)
            try:
                if config.remove_option(bl, record):
                    irc.reply("Reply removed.", prefixNick=False)

Class = DNSbl


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
