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

import supybot.conf as conf
import supybot.registry as registry
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Yourls')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Yourls', True)
    oformat = something(_("""
        What format do you want most of your messages to come back as?
        (Really only 'simple' is able to be used.
        """), default="simple")
    domain = something(_("""What domain/website is the yourls instance on (ports need to be included if applicable"""))
    apipage = something(_("What is the path of your api"), default="/yourls-api.php")
    signature = something(_("What is your 'secret' signature from your.instance/admin/tools.php"))
    conf.supybot.plugins.Yourls.format.setValue(oformat)
    conf.supybot.plugins.Yourls.domain.setValue(domain)
    conf.supybot.plugins.Yourls.apipage.setValue(apipage)
    conf.supybot.plugins.Yourls.signature.setValue(signature)

Yourls = conf.registerPlugin('Yourls')
# This is where your configuration variables (if any) should go.  For example:
# conf.registerGlobalValue(Yourls, 'someConfigVariableName',
#     registry.Boolean(False, _("""Help for someConfigVariableName.""")))
conf.registerGlobalValue(Yourls, "format",
    registry.String("simple", ("""What output format do you want the request to come back as (json, jsonp, xml, simple)""")))
conf.registerGlobalValue(Yourls, "domain",
    registry.String("", ("""Domain Name that your yourls instance is running on""")))
conf.registerGlobalValue(Yourls, "apipage",
    registry.String("/yourls-api.php", ("""What page is your api at => /page.php""")))
conf.registerGlobalValue(Yourls, "signature",
    registry.String("", ("""Your ''secret'' signature/token for authing with yourls""")))
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
