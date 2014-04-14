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

"""
This plugin provides a command to check the status of the Mojang
servers. The output format is customizable via configuration variables.
"""

import supybot
from supybot import world

__version__ = '1.1.0'

__author__ = supybot.Author('nyuszika7h', 'nyuszika7h',
                            'nyuszika7h@cadoth.net')

__contributors__ = {}

__url__ = 'https://github.com/nyuszika7h/Supybot-plugins/tree/master/MCStatus'

from . import config, plugin
from imp import reload

# In case we're being reloaded.
reload(config)
reload(plugin)

if world.testing:
    import test

Class = plugin.Class
configure = config.configure

# vim: ts=4 sw=4 sts=4 et tw=79
