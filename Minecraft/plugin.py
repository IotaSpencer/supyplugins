###
# Copyright (c) 2013, Ken Spencer
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
import supybot.conf as conf
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
import sqlite3 as lite
import urllib2 as urllib
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Minecraft')
except:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x:x

class Minecraft(callbacks.Plugin):
    """recipe add, recipe get, recipe search, recipe count, haspaid"""
    threaded = True
    def recipeadd(self, irc, msg, args, item, line1, line2, line3):
        """Item Line1 Line2 Line3
        Add a recipe in, you must be a "TrustedMCer" to add recipes though"""
        dbpath = self.registryValue('DBPath')
        con = lite.connect(dbpath)
        quiet = self.registryValue('quiet', msg.args[0])
        with con:
            cur = con.cursor()
            con.text_factory = str
            cur.execute("INSERT INTO recipes VALUES(?, ?, ?, ?);", (item, 
line1, line2, line3))
            # And now some making sure its in there
            cur.execute("SELECT * FROM recipes WHERE item LIKE ?;", (item,))
            result = cur.fetchall()
            result = str(result).translate(None, '[](),')
            channel = msg.args[0]
            if quiet == True or irc.isChannel(msg.args[0]) == False:
                irc.sendMsg(ircmsgs.privmsg(msg.nick, result))
            elif quiet == False:
                irc.sendMsg(ircmsgs.privmsg(msg.args[0], result))
    recipeadd = wrap(recipeadd, [("checkCapability", "TrustedMCer"), "something", "something", "something", "something"])
    def recipeget(self, irc, msg, args, citem):
        """Item
        Get a crafting recipe from the bot, atm if it doesn't reply, that means there isn't a 
recipe in the bot for it yet. Ask the Owner or a 'TrustedMCer'"""
        dbpath = self.registryValue('DBPath')
        con = lite.connect(dbpath)
        global nick
        nick = msg.nick
        quiet = self.registryValue('quiet', msg.args[0])
        with con:
            #assert nick is str
            cur1 = con.cursor()
            cur2 = con.cursor()
            cur3 = con.cursor()
            cur1 = con.execute("SELECT recipe_line_1 FROM recipes WHERE item LIKE ?;", (citem,))
            cur2 = con.execute("SELECT recipe_line_2 FROM recipes WHERE item LIKE ?;", (citem,))
            cur3 = con.execute("SELECT recipe_line_3 FROM recipes WHERE item LIKE ?;", (citem,)) 
            line1 = cur1.fetchone()
            line2 = cur2.fetchone()
            line3 = cur3.fetchone()
            channel = msg.args[0]
            if line1 == None or line2 == None or line3 == None:
                irc.reply("That recipe does not exist in the database. Please get a TrustedMCer or the owner to add it, make sure to give the recipe :P")
            elif line1 != None or line2 != None or line3 != None:
                if quiet == True or irc.isChannel(msg.args[0]) == False:
                    irc.sendMsg(ircmsgs.notice(msg.nick, "%s" % (line1)))
                    irc.sendMsg(ircmsgs.notice(msg.nick, "%s" % (line2)))
                    irc.sendMsg(ircmsgs.notice(msg.nick, "%s" % (line3)))
                elif quiet == False:
                    irc.reply("%s" % (line1), private=False)
                    irc.reply("%s" % (line2), private=False)
                    irc.reply("%s" % (line3), private=False)
    recipeget = wrap(recipeget, ["text"])
    def recipelist(self, irc, msg, args):
        """
        lists the recipes in the database"""
        dbpath = self.registryValue('DBPath')
        con = lite.connect(dbpath)
        quiet = self.registryValue('quiet', msg.args[0])
        with con:
            cur1 = con.cursor()
            cur1 = con.execute("SELECT COUNT(item) FROM recipes;")
            result = cur1.fetchone()
            if quiet == True or irc.isChannel(msg.args[0]) == False:
                irc.reply("There are %s recipes in the database. =)" % (result), private=True, to=msg.nick)
            elif quiet == False:
                irc.reply("There are %s recipes in the database. =)" % (result))
            cur = con.cursor()
            con.text_factory = str
            cur = con.execute("SELECT item FROM recipes WHERE item LIKE '%';")
            rows = cur.fetchall()
            items = rows
            items = str(items).translate(None, '(),[]')
            if quiet == True or irc.isChannel(msg.args[0]) == False:
                irc.reply("%s" % (items), prefixNick=False, private=True, to=msg.nick)
            elif quiet == False:
                irc.reply("%s" % (items), prefixNick=True)
    recipelist = wrap(recipelist, [("checkCapability", "owner")])
    def recipecount(self, irc, msg, args):
        """
        returns the total number of recipes in the database!"""
        dbpath = self.registryValue('DBPath')
        quiet = self.registryValue('quiet', msg.args[0])
        con = lite.connect(dbpath)
        with con:
            cur = con.cursor()
            cur = con.execute("SELECT COUNT(item) FROM recipes;")
            result = cur.fetchone()
            if quiet == True or irc.isChannel(msg.args[0]) == False:
                irc.reply("There are %s crafting recipes inside the database. =)" % (result), 
private=True, to=msg.nick)
            elif quiet == False:
                irc.reply("There are %s crafting recipes inside the database. =)" % (result), private=False)
    recipecount = wrap(recipecount)
    def recipesearch(self, irc, msg, args, query):
        """Item
        Please include your search, use sqlite wildcards."""
        dbpath = self.registryValue('DBPath')
        con = lite.connect(dbpath)
        quiet = self.registryValue('quiet', msg.args[0])
        with con:
            currcount = con.cursor()
            con.text_factory = str
            currcount = con.execute("SELECT COUNT(item) FROM recipes WHERE item LIKE ?;", (query,))
            count = currcount.fetchone()
            count = str(count).translate(None, '(),')
            if quiet == True or irc.isChannel(msg.args[0]) == False:
                irc.reply("%s gives %s results." % (query, count), prefixNick=False, 
private=True, to=msg.nick)
            elif quiet == False:
                irc.reply("%s gives %s results." % (query, count), private=False)
            currsearch = con.cursor()
            currsearch = con.execute("SELECT item FROM recipes WHERE item LIKE ?", (query,))
            result = currsearch.fetchall()
            result = str(result).translate(None, '[]\(\)\,')
            if count == '0':
                irc.noReply()
            else:
                if quiet == True or irc.isChannel(msg.args[0]) == False:
                    irc.reply("%s gives the following results, %s" % (query, result))
                elif quiet == False:
                    irc.reply("%s gives the following results, %s" % (query, result), private=False)
    recipesearch = wrap(recipesearch, ["something"])
    def haspaid(self, irc, msg, args, user):
        """User
        Use to determine whether not a certain user is premium."""
        quiet = self.registryValue('quiet', msg.args[0])
        req = urllib.Request(url="http://minecraft.net/haspaid.jsp?user=%s" % (user))
        f = urllib.urlopen(req)
        result = f.read()
        if quiet == True or irc.isChannel(msg.args[0]) == False:
            if result == "true":
                irc.reply("%s is a premium account." % (user), prefixNick=False, private=True)
            elif result == "false":
                irc.reply("%s is not a premium account." % (user), prefixNick=False, private=True)
        elif quiet == False:
            if result == "true":
                irc.reply("%s is a premium account." % (user), prefixNick=False)
            elif result == "false":
                irc.reply("%s is not a premium account." % (user), prefixNick=False)

    haspaid = wrap(haspaid, ["something"])
Class = Minecraft


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
