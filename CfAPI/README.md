# Cloudflare

Allows access to the Cloudflare(tm) API.

## Setup

To begin with, you'll need to give the plugin your API signature/key and your
account email, these are saved inside your bot and are used by the code to
contact the Cloudflare API.

If you do not have an API key/Cloudflare account, this plugin will not work for
you.

Anyways..

##### Account Email

`config plugins.Cloudflare.api.email your@email.here.com`

##### API Signature

Note: Your API key can be found
[here](https://www.cloudflare.com/a/account/my-account)

Your API key is just like a password, so **do not set this via a channel**, nor
will the bot let you, so **don't try it**. **Please PM** your bot the following.

`config plugins.Cloudflare.api.key YOURKEY HERE`

## Issues

If there any issues pertaining to the plugin, please submit an issue on the
[Issue tracker](https://github.com/IotaSpencer/supyplugins/issues)

This would pertain to errors in the code itself, if you're getting rate limited,
or some other request error, then that is from Cloudflare itself. And is not an
error, but just a limitation of the API or you're being throttled by cloudflare.

#### Legal

This plugin nor the author is affiliated with Cloudflare(tm), this plugin uses
open-source libraries such as
[python-cloudflare](https://github.com/cloudflare/python-cloudflare)
to acheive its desired actions. Cloudflare is liable for damages to your account
by using this plugin. You use this plugin at your own risk.

#### P.S.

The plugin really shouldn't break anything. As it uses cloudflare's own
self-produced library, the only possible bugs may be in what arguments are
passed to the API. Hopefully, the API will reject anything that you throw at it
that isn't valid for it.
