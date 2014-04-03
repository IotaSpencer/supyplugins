###
# Copyright (c) 2014, Ken Spencer | Iota
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
import xml.etree.ElementTree as ET

# External

try:
    import requests
except ImportError:
    print "Sorry, the requests library is needed with this plugin"

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Yourls')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class Yourls(callbacks.Plugin):
    """This plugins shortens a long url, expands a short url(e-code.in/???), gives stats on them"""
    global params
    params = {}
    threaded = True
    def shorten(self, irc, msg, args, url, keyword, title):
        """<url> [keyword] [title]
        Shorten a url using an optional keyword as the custom end, plus an optional title"""
        params["action"] = "shorturl"
        outformat = self.registryValue("format")
        signature = self.registryValue("signature")
        params["format"] = outformat
        params["signature"] = signature
        params["keyword"] = keyword
        params["title"] = title
        params["url"] = url
        yourlsdomain = self.registryValue("domain")
        apipage = self.registryValue("apipage")
        page = yourlsdomain + apipage
        if params["keyword"] == None:
            del params["keyword"]
        if params["title"] == None:
            del params["title"]
        r = requests.post(page, params=params)
        result = r.text
        irc.reply("The short version of %s is %s"% (url, result), prefixNick = False)
    shorten = wrap(shorten, ["something", optional("something"), optional("something")])
    def expand(self, irc, msg, args, shorturl):
        """<shorturl>
        Expand a short url (You can use only the characters after /)"""
        params["action"] = "expand"
        params["format"] = self.registryValue("format")
        params["shorturl"] = shorturl
        params["signature"] = self.registryValue("signature")        
        yourlsdomain = self.registryValue("domain")
        apipage = self.registryValue("apipage")
        page = yourlsdomain + apipage
        r = requests.post(page, params=params)
        result = r.text
        irc.reply("The long url to %s, is %s"% (shorturl, result), prefixNick=False)
    expand = wrap(expand, ["something"])
    def urlstats(self, irc, msg, args, shorturl, limit):  
        """<shorturl>
        Show stats on the short url given (You can use only the characters after /)"""
        params["action"] = "url-stats"
        params["format"] = "xml"
        params["shorturl"] = shorturl
        params["signature"] = self.registryValue("signature")
        params["limit"] = limit
        if params["limit"] == None:
            params["limit"] = ""
        yourlsdomain = self.registryValue("domain")
        apipage = self.registryValue("apipage")
        page = yourlsdomain + apipage
        r = requests.post(page, params=params)
        result = r.text
        root = ET.fromstring(result)
        stats = []
        for itar in root.findall("link"):
            surl = itar.find("shorturl").text
            rurl = itar.find("url").text
            ip = itar.find("ip").text
            clicks = itar.find("clicks").text
        irc.reply("Here is the stats for %s (Long URL: %s): Submitters IP: %s Clicks: %s"% (surl, rurl, ip, clicks), prefixNick=False)
    urlstats = wrap(urlstats, ["something", optional("something")])
        
Class = Yourls


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
