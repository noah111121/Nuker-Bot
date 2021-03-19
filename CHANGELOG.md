# Nuker Bot Changelog

### Latest stable version: v1.4
**Latest pre-release version: N/A**

### Changes planned (will be ticked off when available in (minimum) alpha versions and by default, all changes planned are high priority unless specified):

> - **Add support for a custom amount of "nuke channels"**
> - **Check if the server is boosted before applying a GIF for the server icon (as well as a default GIF)**
> - **[Low Priority] Be able to send (a) message(s) into the nuke channel(s)**

### Updated README.md (extends main/README.md so read that first)

<br><br><br><br>

### v1.3 => v1.5:

> - **Fixed bug where bot tried to process commands that didn't exist.**

### v1.3 => v1.4:

> - **Switched from .env files to JSON; see the config section in the main README.md.**
> - **Fixed bug whereupon restart of the bot, it would forget any previously created administrator roles.**

### v1.2 => v1.3:

> - **Revamped logging function.**
> - **Fixed bug where the ban function would break due to permission hierarchy setup.**
> - **Added support where you can supply your user ID so all commands can only work for you.**

### v1.1 => v1.2:
**Features:**
> - Fixed the bug where recognised commands would trigger a made-up error.

### v1.0 => v1.1:
> - Support for different configuration options in .env file and in-app commands:
>   - Support for custom prefixes (.env only)
>   - Support for custom statuses (.env only)
> - More configurable nuke operations in the `!skip` command:
>   - Support for changing nicknames
> 
> - Added permission checks to ensure the bot has administrator permissions for all commands.
