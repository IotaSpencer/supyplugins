##
# MCStatus - check the Mojang servers' status with a command
#
# Copyright (c) 2012-2013, nyuszika7h <nyuszika7h@cadoth.net>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##

# Standard library imports
import json
import requests
# Supybot imports
from supybot import callbacks
from supybot.commands import *

try:
    from supybot.i18n import PluginInternationalization

    _ = PluginInternationalization('Utrace')
except ImportError:
    # Placeholder that allows to run the plugin on a bot without the
    # i18n module.
    _ = lambda x:x


class MCStatus(callbacks.Plugin):
    """
    This plugin provides a command to check the status of the Mojang
    servers. The output format is customizable via configuration
    variables.
    """

    def mcstatus(self, irc, msg, args):
        """takes no arguments

        Shows the status of the Mojang servers.
        """

        status_url = self.registryValue('statusURL')

        prefix = self.registryValue('prefix')
        suffix = self.registryValue('suffix')

        separator = self.registryValue('separator')

        svprefix = self.registryValue('service.prefix')
        svsuffix = self.registryValue('service.suffix')

        stonline = self.registryValue('status.online')
        stoffline = self.registryValue('status.offline')


        json_data = requests.post(status_url)
        json_data = json_data.json
        data = json.loads(json_data)

        services = []

        for pair in data:
            service = list(pair.keys())[0].split('.')[0].title()
            if service == 'Minecraft': service = 'Website'

            status = list(pair.values())[0]

            services.append('%s%s%s%s' % (svprefix, service, svsuffix,
                                          stonline if status == 'green' else \
                                          stoffline))

        irc.reply('%s%s%s' % (prefix, separator.join(services), suffix))

    mcstatus = wrap(mcstatus)


Class = MCStatus

# vim: ts=4 sw=4 sts=4 et tw=79
