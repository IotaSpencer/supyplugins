###
# Copyright (c) 2017, Ken Spencer
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
import supybot.world as world
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.httpserver as httpserver
import supybot.ircmsgs as ircmsgs
import supybot.log as log

import json

try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization("MsgServer")
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class ServerCallback(httpserver.SupyHTTPServerCallback):
    name = "MSG Server"
    defaultResponse = "NotImplemented!"

    def doPost(self, handler, path, form):
        if path == "/":
            headers = self.headers
            j = json.loads("%s" % str(form, "utf-8"))
            self.plugin.do_http_msg(handler, headers, j)
            return

instance = None


class MsgServer(callbacks.Plugin):
    """Send Msgs to a self hosted service."""
    threaded = True

    def __init__(self, irc):
        # Some stuff needed by Supybot
        global instance
        self.__parent = super(MsgServer, self)
        instance = self
        callbacks.Plugin.__init__(self, irc)

        # registering the callback
        callback = ServerCallback()  # create an instance of the callback
        callback.plugin = self
        httpserver.hook("msgserver", callback)  # register the callback at `/msgserver`
        for cb in self.cbs:
            cb.plugin = self

    def die(self):
        # unregister the callback
        httpserver.unhook("msgserver")  # unregister the callback hooked at /supystory

        # Stuff for Supybot
        self.__parent.die()

    def info(self, irc, msg, args):
        """takes no arguments
        Returns info on the plugin."""

        author = irc.getCallback("MsgServer").classModule.__author__.__str__()

        irc.reply(author)
    info = wrap(info)

    def send_msg(self, channel, text):
        irc = world.getIrc(self.registryValue('adminNet'))
        irc.queueMsg(ircmsgs.privmsg(channel, text))
        log.info("Sent Message: \"{}\" to '{}'".format(text, channel))

    def do_http_msg(self, handler, headers, msg):
        log.debug("headers: {}".format(headers))
        log.debug("text: {}".format(msg))
        params = msg
        important_fields = {
            'key': params.get('key', None),
            'channel': params.get('channel', None),
            'text': params.get('text', None)
        }

        if important_fields['channel'] is None or important_fields['text'] is None or important_fields['key'] is None:
            missing_fields = list(filter(lambda x: important_fields[x] is None, important_fields.keys()))
            handler.send_response(403)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(bytes(json.dumps({"success": False, "msg": "Missing field(s).", "fields": missing_fields}), "utf-8"))
        elif important_fields['key'] == self.registryValue("sendingKey"):
            self.format_msg(msg)
            handler.send_response(200)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(bytes(json.dumps({"success": True, "msg": "Thanks!"}), "utf-8"))
        else:
            handler.send_response(403)
            handler.send_header("Content-Type", "application/json")
            handler.end_headers()
            handler.wfile.write(bytes(json.dumps({"success": False, "msg": "Invalid sendingKey"}), "utf-8"))

Class = MsgServer
# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
