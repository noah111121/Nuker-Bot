# Nuker Bot Changelog

### Latest stable version: v1.7

### Changes planned (will be ticked off when available in (minimum) alpha versions and by default, all changes planned are high priority unless specified):

**Planned for v1.9:** <br>
> - **Fix bug where "volume control" (customisable nuking options) is not server specific and will change for all servers the bot is in.**
> - **Add support for saving volume control (^^^) so upon restart of the bot, it will remember nuking options.**

**Planned for v1.10:** <br>
> - **Add support for a custom amount of "nuke channels".** 
> - **Check if the server is boosted before applying a GIF for the server icon (as well as a default GIF).**
> - **Be able to send (a) message(s) into the nuke channel(s).**

### Updated README.md (extends main/README.md so read that first)

<br><br><br><br>

### v1.8:
> - **Server ID is now logged.**
> - **Show connected servers on startup and logging can now be turned off in the first time setup.**
> - **No longer loads settings from the settings.json file after first time setup.**

### v1.7:
> - **Created first time setup.**
> - **Fixed small bugs.**

### v1.6:
> - **Revamped logging function.**
> - **Token and user id are now entered via inputs and saved, rather than having to open the settings.json file.**
> - **Now sends the error message if unauthorised user attempts to enter a command.**
> - **Fixed the bug that prevented commands from being entered by anyone if the userid was set to false.**
> - **Fixed small bugs.**

### v1.5:
> - **Fixed bug where bot tried to process commands that didn't exist.**

### v1.4:
> - **Switched from .env files to JSON; see the config section in the main README.md.**
> - **Fixed bug whereupon restart of the bot, it would forget any previously created administrator roles.**

### v1.3:
> - **Revamped logging function.**
> - **Fixed bug where the ban function would break due to permission hierarchy setup.**
> - **Added support where you can supply your user ID so all commands can only work for you.**

### v1.2:
> - Fixed the bug where recognised commands would trigger a made-up error.

### v1.1:
> - Support for different configuration options in .env file and in-app commands:
>   - Support for custom prefixes (.env only)
>   - Support for custom statuses (.env only)
> - More configurable nuke operations in the `!skip` command:
>   - Support for changing nicknames
> 
> - Added permission checks to ensure the bot has administrator permissions for all commands.
