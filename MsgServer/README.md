# MsgServer

This plugin allows the sending of logs or notifications through the bot to IRC, through the use of JSON.

#### Dependencies

**Note**: This plugin is for use on Limnoria or Rasserthen(ElectroCode/IotaSpencer's Fork of Limnoria) due to the use of the internal httpserver that is not yet merged into base supybot.



MsgServer requires the following python libraries/packages:

* yamlordereddictloader
* attrdict

## Usage

Before anything, please check your options for the following,

* supybot.servers.http.port
* supybot.servers.http.hosts4
* supybot.servers.http.hosts6

You will need to know these as this is where you need to send your messages.<sup id="a1">[1](#f1)</sup>

To use the plugin, you will have to set a few options before you actually send messages through the bot.

First,


Footnotes:

<a id="f1">1</a>[↩](#a1)