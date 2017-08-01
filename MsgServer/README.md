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

##### Configuration
To use the plugin, you will have to set a few options before you actually send messages through the bot.

Use the following variables to set plugin options, using the command below.

    config plugins.MsgServer.<variable>

<dl>
  <dt><b>sendingKey</b></dt>
  <dd>sendingKey is the string through which the bot will verify the messages its receiving are from a trusted source.</dd>

  <dt><b>adminNet</b></dt>
  <dd>adminNet is the name of the network that all messages through MsgServer should go to.</dd>
</dl>

##### Basics

A basic use of this plugin is to implement some kind of logging/audit system, where actions are sent to an IRC channel.

Using `curl` you can implement the following.

```sh
curl '<hostname>:<port>/<path>'\
  -X POST\
  -H "Content-Type: application/json"\
  --data '{"key": "KEYHEREPLZ", "action": "ACTION", "params": ["PARAM1", "PARAM2"]}'
```

Or if you use my `send` script, you can just use it, either load a json file or json string into it given specific options, and a request will be sent to the configured url.

<hr>

###### Footnotes

<a id="f1">1</a>[↩](#a1) — If you have a hostname(msgs.host.tld) then you should send to that. Just be sure to make sure all your configs are correct and working before trying to send.