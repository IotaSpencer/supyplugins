# -*- coding: utf-8 -*-
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

import dns.exception as exception
import dns.resolver as dns
import yaml
import re

import supybot.conf as conf
import supybot.log as log


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
                return reply[0]
        except exception.DNSException:
            return None


class DNSbl(callbacks.Plugin):
    """DNS Blacklist checker"""
    threaded = True

    def _checkbl(self, ip, bl=None):
        cfgfile = conf.supybot.directories.data.dirize('bls.yml')
        config = yaml.load(file(cfgfile, 'r'))
        
        ip = ip.split('.')
        ip.reverse()
        ip = '.'.join(ip)
        
        enddict = {'zones': [],
                'detected_in': 0,
                'notdetected_in': 0,
                'replies': {},                    
                }
        if bl:
            bl = config['blacklists'][bl]
            recordstring = ip+'.'+bl
            try:
                for rdata in dns.query(recordstring, 'A'):
                    reply = str(rdata)
                    reply = reply.split('.')
                    reply = reply[3]
                    enddict['zones'] = bl
                    enddict['replies'][name] = config[name][reply]
            except exception.DNSException:
                return 'notlisted'
        else:
            result = []
            zones = []
            
            for name, blacklist in config['blacklists'].items():
                recordstring = ip+'.'+blacklist
                try:
                    for rdata in dns.query(recordstring, 'A'):
                        if type(rdata) == 'list':
                            return None
                        reply = str(rdata)
                        reply = reply.split('.')
                        reply = reply[3]
                        enddict['detected_in'] += 1
                        enddict['zones'].append(name)
                        enddict['replies'][name] = config[name][int(reply)]
                except exception.DNSException:
                    enddict['notdetected_in'] += 1
                    
        return enddict
        
    def check(self, irc, msg, args, ip, dnsbl):
        """<ip/host> [<dnsbl>]
        
        Perform a dnsbl check
        """
        cfgfile = conf.supybot.directories.data.dirize('bls.yml')
        config = yaml.load(file(cfgfile, 'r'))
        
        ip = makeIP(ip)
        result = self._checkbl(ip, dnsbl)
        if dnsbl:
            for name, reply in result['replies'].items():
                irc.reply("IP %s has been found in the requested blacklist. Its reply is '%s'" % (ip, reply))
        else:
            irc.reply("IP %s has been found in the following blacklists: %s" % (ip, ', '.join(result['zones'])), prefixNick=False)
            irc.reply("IP %s: listed: %s/%s unlisted: %s/%s" % (ip, result['detected_in'], len(config['blacklists']), result['notdetected_in'], len(config['blacklists'])), prefixNick=False)
            if result['replies']:
                for name, reply in result['replies'].items():
                    irc.reply("IP %s has been found in (%s) as a/an %s" % (ip, name, reply), prefixNick=False)
                
    check = wrap(check, ['somethingWithoutSpaces', optional('somethingWithoutSpaces')])
    
    class dnsbl(callbacks.Commands):
        """
        Allows adding, removing, and listing of dnsbls
        """
        cfgfile = conf.supybot.directories.data.dirize('bls.yml')

        def add(self, irc, msg, args, blname, bl):
            """<name> <blacklist host>
            
            Adds a blacklist into the plugins config\
            if it already exists it will be edited.
            """
            config = yaml.load(file(self.cfgfile, 'r'))


            config[blname] = []
            config['blacklists'][blname] = bl
            irc.reply("Blacklist %s added with host %s." % (blname, bl), prefixNick=False)
            irc.reply(yaml.dump(config))
            yaml.dump(config, file(self.cfgfile, 'w'), default_flow_style=False)

        add = wrap(add, ['admin', 'somethingWithoutSpaces', 'somethingWithoutSpaces'])
        
        def rem(self, irc, msg, args, bl):
            """<blacklist name>
            
            Remove a blacklist
            """
            config = yaml.load(file(self.cfgfile, 'r'))
            
            try:
                del config['blacklists'][bl]
                del config[bl]
                yaml.dump(config, file(self.cfgfile, 'w'), default_flow_style=False)
            except KeyError:
                irc.error("Blacklist %s did not exist." % bl)
                
        rem = wrap(rem, ['admin', 'somethingWithoutSpaces'])
        
        def bls(self, irc, msg, args):
            """takes no arguments
            
            Lists the blacklists in use
            """
            config = yaml.load(file(self.cfgfile, 'r'))
            
            listbls = []
            for k,v in config['blacklists'].items():
                listbls.append('%s - %s' % (k, v))
            msg_bls = 'Blacklists: %s' % (' \xB7 '.join(listbls))
            irc.reply(msg_bls, prefixNick=False)
            
        bls = wrap(bls, ['admin'])
        
        def addrec(self, irc, msg, args, bl, record, rreply):
            """<blacklist name> <reply answer> <reply string>
            
            Add a reply for a record on the given blacklist
            """
            config = yaml.load(file(self.cfgfile, 'r'))

            try:
                config[bl][record] = rreply
                irc.reply(config)
                
                yaml.dump(config, file(self.cfgfile, 'w'), default_flow_style=False)
            except KeyError:
                irc.error("That blacklist does not exist in the config.")
            
        addrec = wrap(addrec, ['admin', 'somethingWithoutSpaces', 'int', 'something'])
        
        def remrec(self, irc, msg, args, bl, record):
            """<blacklist name> <reply answer>
            
            Removes a reply from the given blacklist
            """
            config = yaml.load(file(self.cfgfile, 'r'))
            
            try:
                del config[bl][record]
                irc.reply("Reply removed.", prefixNick=False)
                yaml.dump(config, file(self.cfgfile, 'w'), default_flow_style=False)
            except KeyError:
                irc.error("Reply did not exist.")
        remrec = wrap(remrec, ['admin', 'somethingWithoutSpaces', 'somethingWithoutSpaces'])
        
        def listrecs(self, irc, msg, args, bl):
            """<blacklist name>
            
            Lists record replies for the given blacklist.
            """
            config = yaml.load(file(self.cfgfile, 'r'))

            records = []
            for k in sorted(config[bl].keys()):
                records.append('%s - %s' % (k, config[bl][k]))
            msg_bls = 'Records: %s' % (' \xB7 '.join(records))
            irc.reply(msg_bls, prefixNick=False)
            
        listrecs = wrap(listrecs, ['admin', 'somethingWithoutSpaces'])
        
Class = DNSbl
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79: