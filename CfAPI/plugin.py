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
    _ = PluginInternationalization('CfAPI')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

import CloudFlare
import re

class CfAPI(callbacks.Plugin):
    """Allows access to the Cloudflare (tm) API"""
    threaded = True

    def zones(self, irc, msg, args):
        """takes no arguments
        Lists the zones on the account."""
        email = conf.supybot.plugins.CfAPI.api.email()
        key = conf.supybot.plugins.CfAPI.api.key()
        cf_send = CloudFlare.CloudFlare(email=email, token=key)

        listofzones = cf_send.zones.get()
        zonelist = []
        for zone in listofzones:
            zone_id = zone['id']
            zone_name = zone['name']
            zonelist.append("%s(%s)" % (zone_name, zone_id))
        irc.reply("%s" % (u" \xB7 ".join(zonelist)), notice=True, private=True)
    zones = wrap(zones, ['admin'])

    class dns(callbacks.Commands):
        """
        Adds in commands pertaining to managing your dns records.
        """
        
        pattern = re.compile(r"\b(\w+)\s*:\s*([^\s]+)")
        def add(self, irc, msg, args, zone_id, data):
            """<zone id> \"<content(IP, TXT value)>\" <name(subdomain, etc.)> [data]

            Adds a record to the zone given.
            """
            email = conf.supybot.plugins.CfAPI.api.email()
            key = conf.supybot.plugins.CfAPI.api.key()
            cf_send = CloudFlare.CloudFlare(email=email, token=key)
            
            
            record = dict(self.pattern.findall(data))
            try:
                if int(record['ttl']) > 604800 or int(record['ttl']) < 0:
                    record['ttl'] = '1'    
            except KeyError:
                record['ttl'] = '1'
            
            response = cf_send.zones.dns_records.post(zone_id, data = body)

        add = wrap(add, ['admin', 'something', 'something', optional('text')])

        def rem(self, irc, msg, args, zone_id, record_id):
            """<zone_id> [record_id]
            You get the record id from checking for the record via 'dns get'""" 

            email = conf.supybot.plugins.CfAPI.api.email()
            key = conf.supybot.plugins.CfAPI.api.key()
            cf_send = CloudFlare.CloudFlare(email=email, token=key)
            try:
                response = cf_send.zones.dns_records.delete(zone_id, record_id)
                irc.reply("Done!")
                
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                for x in e:
                    irc.error("api error: %d %s" % (x, x))
        rem = wrap(rem, ['admin', 'something', 'text'])
        def get(self, irc, msg, args, zone_id, params):
            """<zone id> [params]

            Returns the records for 'zone id'
            """
            email = conf.supybot.plugins.CfAPI.api.email()
            key = conf.supybot.plugins.CfAPI.api.key()
            cf_send = CloudFlare.CloudFlare(email=email, token=key)

            # split params into key, values
            # and make sure those that we have
            # are valid keywords for the api

            newparams = dict(self.pattern.findall(params))

            try:
                dns_records = cf_send.zones.dns_records.get(zone_id, params = newparams)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                irc.error('Error: /zones.dns_records.get - %d %s' % (e, e), Raise=True)

            irc.replies(['%(id)s / %(name)s / %(ttl)d / %(type)s / %(content)s ; proxied=%(proxied)s proxiable=%(proxiable)s' % dns_record for dns_record in dns_records],
                prefixNick=False, notice=False, private=False)
        get = wrap(get, ['admin', 'something', 'text'])

    class rr(callbacks.Commands):
        """Helps with managing round robins of sorts, using short
            names to add, and returning the record_id for lookup later"""
        
        default_zone = conf.supybot.plugins.CfAPI.rr.zone()
        pattern = re.compile(r"\b(\w+)\s*:\s*([^\s]+)")
        def add(self, irc, msg, args, name, content, opts):
            """<record>
            
            consists of the type of record (A, AAAA, CNAME, etc.) and
            its IP (0.0.0.0) and Name (irc)"""
            email = conf.supybot.plugins.CfAPI.api.email()
            key = conf.supybot.plugins.CfAPI.api.key()
            cf_send = CloudFlare.CloudFlare(email=email, token=key)
            
            options = opts
            
            options = dict(self.pattern.findall(options))
            record = {'name': name, 'content': content}
            record.update(options)
            
            
            
            # create the record
            cf_send.zones.dns_records.post(self.default_zone, data = record)
            
            # see if the record now exists
            
            body = {'name': name, 'content': content}
            response = cf_send.zones.dns_records.get(zone, data = body)
            irc.reply(response)
        add = wrap(add, ['admin', 'something', 'something', 'text'])

        #def rem(self, irc, msg, args, record_id):
        
        
        def lists(self, irc, msg, args, opts):
            """<key:value> [key:value]...
            
            lists the records for names given inside supposed rr's (round robins)"""
            
            email = conf.supybot.plugins.CfAPI.api.email()
            key = conf.supybot.plugins.CfAPI.api.key()
            cf_send = CloudFlare.CloudFlare(email=email, token=key)
            zone = conf.supybot.plugins.CfAPI.rr.zone()
            
            opts = dict(self.pattern.findall(opts))

            try:
                dns_records = cf_send.zones.dns_records.get(zone, params = opts)
            except CloudFlare.exceptions.CloudFlareAPIError as e:
                irc.error('Error: /zones.dns_records.get - %d %s' % (e, e), Raise=True)

            irc.replies(['%(id)s / %(name)s / %(type)s / %(content)s' % dns_record for dns_record in dns_records],
                prefixNick=False, notice=False, private=False)
            
        lists = wrap(lists, ['admin', 'text'])
        
Class = CfAPI


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
