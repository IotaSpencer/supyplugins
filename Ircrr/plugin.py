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
import supybot.conf as conf
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Ircrr')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

import CloudFlare
import re

def get_cf():
    email = conf.supybot.plugins.Ircrr.api.email()
    key = conf.supybot.plugins.Ircrr.api.key()
    cf_send = CloudFlare.CloudFlare(email=email, token=key, raw=True)
    return cf_send
    
class Ircrr(callbacks.Plugin):
    """Allows access to the Cloudflare (tm) API to
        manage Round Robins"""
    threaded = True
    class rr(callbacks.Commands):
        zone_id = conf.supybot.plugins.Ircrr.rr.zone_id()
        zone_name = conf.supybot.plugins.Ircrr.rr.zone()
        pattern = re.compile(r"\b(\w+)\s*:\s*([^\s]+)")
        
        # @param subdomain - the name of the rr
        # @param rtype - the type of record this is
        # @param content - the IP or hostname
        def add(self, irc, msg, args, subdomain, rtype, content):
            """<name> <type(A,AAAA,CNAME)> <content(IP, Hostname)>
            
            add a entry to a round robin under the given subdomain name.
            """
            cf_send = get_cf()
            zone = self.zone_name
            
            name = subdomain+'.'+zone
            if rtype.upper() not in ('A','AAAA','CNAME'):
                irc.error('Invalid Round Robin record type.', prefixNick=False)
            
            body = {'name': name, 'content': content, 'type': rtype}
            response = cf_send.zones.dns_records.post(self.zone_id, data = body)
            response = response.get('result')
            if response:
                irc.reply("Record added, Name: %(name)s Content: %(content)s Type: %(type)" % response, prefixNick=False)
            else:
                irc.error("Failure", prefixNick=False)
        add = wrap(add, ['admin', 'something', 'something', 'something'])
        
        def rem(self, irc, msg, args, record_id):
            """<record id>
            
            removes a record from the round robin"""
            cf_send = get_cf()
            zone = self.zone_id
            
            response = cf_send.zones.dns_records.delete(zone, record_id)
            try:
                id = response['result']['id']
                irc.reply('Record ID %s removed' % id, prefixNick=False)
            except KeyError:
                pass
                
        rem = wrap(rem, ['admin', 'something'])
        
        def get(self, irc, msg, args, subdomain, extra):
            """<rr subdomain>
            
            lists out the entries in a round robin of the given subdomain"""
            cf_send = get_cf()
            zone = self.zone_id
            zone_name = self.zone_name
            body = {'name': subdomain+'.'+zone_name}
            if extra != None:
                options = dict(self.pattern.findall(extra))
                body.update(options)
                
            dns_records = cf_send.zones.dns_records.get(zone, params = body)
            dns_records = dns_records.get('result')
            irc.replies(['%(id)s / %(name)s / %(type)s / %(content)s' % dns_record for dns_record in dns_records], prefixNick=False)
        get = wrap(get, ['admin', 'something', optional('text')])
        
Class = Ircrr