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

from supybot import conf, registry

try:
    from supybot.i18n import PluginInternationalization
                             
    _ = PluginInternationalization('MCStatus')
except ImportError:
    # Placeholder that allows to run the plugin on a bot without the
    # i18n module.
    _ = lambda x:x


def configure(advanced):
    from supybot.questions import expect, anything, something, yn

    conf.registerPlugin('MCStatus', True)


MCStatus = conf.registerPlugin('MCStatus')


conf.registerGlobalValue(MCStatus, 'statusURL',
    registry.String('http://status.mojang.com/check', _("""This is the URL
    of the Mojang JSON status API. You shouldn't change this unless you
    know what you are doing.""")))

conf.registerChannelValue(MCStatus, 'prefix',
    registry.String('', _("""This text is prepended to the mcstatus command's
    output.""")))

conf.registerChannelValue(MCStatus, 'suffix',
    registry.String('', _("""This text is appended to the mcstatus command's
    output.""")))

conf.registerChannelValue(MCStatus, 'separator',
    registry.StringSurroundedBySpaces('|', _("""This text is inserted between
    service-status pairs, surrounded by spaces until I find a better way.""")))


conf.registerGroup(MCStatus, 'service')


conf.registerChannelValue(MCStatus.service, 'prefix',
    registry.String('', _("""This text is prepended to each service's
                             name.""")))

conf.registerChannelValue(MCStatus.service, 'suffix',
    registry.StringWithSpaceOnRight(':', _("""This text is appended to each
    service's name, followed by a space until I find a better way.""")))


conf.registerGroup(MCStatus, 'status')


conf.registerChannelValue(MCStatus.status, 'online',
    registry.NormalizedString('\x0309ONLINE\x03', _("""This text is displayed when a
    service is online""")))

conf.registerChannelValue(MCStatus.status, 'offline',
    registry.NormalizedString('\x0304OFFLINE\x03', _("""This text is displayed when a
    service is offline.""")))

# vim: ts=4 sw=4 sts=4 et tw=79
