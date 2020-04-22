# python 3.7
import discord  # version 1.3.2
from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from discord.ext.commands import has_permissions
import json
from pirate_lib import get_topic
from pirate_lib import write_file
from pirate_lib import pull_flag
from pirate_lib import read_file
from pirate_lib import append_topic
from config import get_config
import time
epoch = time.time()
config = get_config()
client = Bot(command_prefix=config.prefix, case_insensitive=True)
last_topic = -1

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    '''list = []
    for i in list:
        channel = client.get_channel(i)
        await channel.delete()'''


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel.id == 701922472538144778 and str.lower(message.content).startswith("suggestion:"):
        write_file("suggestions.Json", message.content)
        await message.channel.send("Suggestion saved")




@client.event
async def on_voice_state_update(member, before, after):
    channel = after.channel
    if channel is not None:
        if channel.id == 702169810028724297:
            guild = member.guild
            category = client.get_channel(700665944279875654)
            channel = await guild.create_voice_channel(name="2 People Group", user_limit=2, category=category) # create channel
            role = guild.get_role(700732374471934053)
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True),
                role: discord.PermissionOverwrite(read_messages=True),
                client.user: discord.PermissionOverwrite(manage_permissions=True, read_messages=True, manage_channels=True)
            }
            text_channel = await guild.create_text_channel(name="2 People Group", category=category, position=0, overwrites=overwrite)
            await member.move_to(channel) # move member
            write_file("to_delete.Json", value=text_channel.id, key=str(channel.id)) # adds channel id to the "to_delete" list
        with open('to_delete.Json', 'r') as to_delete:
            to_delete_list = json.load(to_delete)
            if str(channel.id) in to_delete_list.keys():
                text_channel = client.get_channel(to_delete_list[str(channel.id)])
                await text_channel.set_permissions(member, read_messages=True)
    channel = before.channel
    if channel is not None:
        with open('to_delete.Json', 'r') as to_delete:
            to_delete_list = json.load(to_delete)
            if len(channel.members) == 0 and str(channel.id) in to_delete_list.keys(): # checks if channel has no one and if it's in the "to_delete" list
                await channel.delete()
                text_channel = client.get_channel(to_delete_list[str(channel.id)])
                await text_channel.delete()
            elif str(channel.id) in to_delete_list.keys():
                text_channel = client.get_channel(to_delete_list[str(channel.id)])
                await text_channel.set_permissions(member, read_messages=False)


@client.command()
async def topic(ctx):
    global epoch
    global last_topic
    if time.time()-epoch>9:
        epoch = time.time() # resets the epoch time
        embed = discord.Embed(title="Conversation topic", color=0x0d25cc)
        topic_variable = get_topic()
        while topic_variable == last_topic:
            topic_variable = get_topic()
        last_topic = topic_variable
        embed.add_field(name=config.default_topic_message.format(topic_variable), value="Answer or walk the plank!")
        await ctx.send(embed=embed)
    else:
        await ctx.send("Command is on cooldown, please wait {0} seconds".format(str(int(10-(time.time()-epoch)))))


@client.command()
async def test_flags(ctx, *args):
    flag_list = ["--username", "--color", "--country"]
    flags = pull_flag(arg_list=args, flag_list=flag_list)
    for i in flags:
        await ctx.send("{0}: {1}".format(str(i[0]).replace("--", ""), str(i[1])))


@client.command()
async def members(ctx):
    list_members = ctx.guild.members
    list_users = []
    for i in list_members:
        if i.bot is False:
            list_users.append(i)
    await ctx.send("There are {0} sailors on the ship".format(len(list_users)))


@client.command()
async def addtopic(ctx, *topic):
    if ctx.author.id in config.admins:
        topic = " ".join(topic)
        topic = topic.replace("’", "'")
        append_topic(topic)
        await ctx.send("Added successfully")
    else:
        await ctx.send("You do not have permission to do that")


client.run(config.token)


