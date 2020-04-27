# python 3.7
import discord  # version 1.3.2
from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from discord.ext.commands import has_permissions
import json
import functools
from wiktionaryparser import WiktionaryParser
import PyDictionary
import random
from paginator import Pages
from pirate_lib import get_topic
from pirate_lib import write_file
from pirate_lib import pull_flag
from pirate_lib import read_file
from pirate_lib import get_nominee
from pirate_lib import add_nominee
from pirate_lib import append_topic
from pirate_lib import _resolve_member_id
from pirate_lib import pirate_error
from config import get_config
import time
import argparse
import shlex
import traceback
parser = WiktionaryParser()
epoch = time.time()
config = get_config()
client = Bot(command_prefix=config.prefix, case_insensitive=True)
last_topic = -1
# client.remove_command(help)
list_numbers_banned = []

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    list = [704019374780055643, 704019374310424808]
    # for i in list: await client.get_channel(i).delete()



@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel.id == 701922472538144778 and str.lower(message.content).startswith("suggestion:"):
        write_file("suggestions.Json", message.content)
        await message.channel.send("Suggestion saved.")
        channel = client.get_channel(703480588430082110)
        text = message.content.replace("Suggestion: ", "", 1)
        await channel.send("**Suggestion: **" + text.replace("suggestion: ", "", 1) + "\n")


@client.event
async def on_voice_state_update(member, before, after):
    channel = after.channel
    if channel is not None:
        if channel.id == 702169810028724297:
            guild = member.guild
            category = client.get_channel(700665944279875654)
            channel_number = random.randint(1111, 9999)
            while channel_number in list_numbers_banned:
                channel_number = random.randint(1111, 9999)
            list_numbers_banned.append(channel_number)
            channel = await guild.create_voice_channel(name="Private group {0}".format(channel_number), user_limit=2, category=category) # create channel
            role = guild.get_role(700732374471934053)
            overwrite = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True),
                role: discord.PermissionOverwrite(read_messages=True),
                client.user: discord.PermissionOverwrite(manage_permissions=True, read_messages=True, manage_channels=True)
            }
            text_channel = await guild.create_text_channel(name="private-group-{0}".format(channel_number), category=category, position=0, overwrites=overwrite)
            message = "**__Welcome to your private chat room!__\n Only users who are in the designated voice channel can see this room! Please follow the rules as these rooms are moderated!\n\nYou can use the p!changelimit (p!cl) command to change the amount of members that can join your channel!\nHave fun!! ||{0} ping ;)||**__".format(member.mention)
            await text_channel.send(message)
            await member.move_to(channel) # move member
            write_file("to_delete.Json", value=text_channel.id, key=str(channel.id)) # adds channel id to the "to_delete" list
        with open('to_delete.Json', 'r') as to_delete:
            to_delete_list = json.load(to_delete)
            if str(channel.id) in to_delete_list.keys():
                text_channel = client.get_channel(to_delete_list[str(channel.id)])
                if not ctx.guild.get_role(700732374471934053) in member.roles:
                    await text_channel.set_permissions(member, read_messages=True)
    channel = before.channel
    if channel is not None:
        with open('to_delete.Json', 'r') as to_delete:
            to_delete_list = json.load(to_delete)
            if len(channel.members) == 0 and str(channel.id) in to_delete_list.keys(): # checks if channel has no one and if it's in the "to_delete" list
                await channel.delete()
                text_channel = client.get_channel(to_delete_list[str(channel.id)])
                await text_channel.delete()
            elif str(channel.id) in to_delete_list.keys() and after.channel is not before.channel:
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


@client.command()
async def warn(ctx, user: discord.Member, *, arg):
    if ctx.author.id in config.moderators or ctx.author.id in config.admins:
        if arg:
            user_id = str(user.id)
            moderator_id = str(ctx.author.id)
            warn_dict = {
                "user_id": user_id,
                "reason": arg,
                "epoch": int(time.time()),
                "moderator_id": moderator_id,
                "punishment_type": "warn"
            }
            await user.send("You have been warned for the following reason: {0}".format(arg))
            write_file("warns.Json", warn_dict)
            await ctx.send("Successfully warned user")
            embed = discord.Embed(title="WARN {0}#{1}".format(user.display_name, user.discriminator), color=0x0d25cc)
            embed.add_field(name="User".format(user.display_name),
                            value="{0}".format(user.mention))
            embed.add_field(name="Moderator".format(user.display_name),
                            value="{0}".format(ctx.author.mention))
            embed.add_field(name="Reason".format(arg),
                            value="{0}".format(arg))
            embed.add_field(name="Channel".format(user.display_name),
                            value="{0}".format(ctx.channel))
            await ctx.guild.get_channel(config.logs).send(embed=embed)
        else:
            await ctx.send("Missing required argument")
    else:
        await ctx.send("You don't have permission to do that, silly.")


@client.command(aliases=['infractions', 'warnings', 'viewwarn'])
async def viewwarns(ctx, *user: discord.User):
    if not user:
        user = ctx.author
    else:
        user = user[0]
    if user == ctx.author or ctx.author.id in config.moderators or ctx.author.id in config.admins:
        warns = read_file('warns.Json')
        warn_list = []
        for warn in warns:
            if warn["user_id"] == str(user.id):
                warn_list.append(warn)
        embed=discord.Embed(title="Warnings", color=0x0d25cc)
        fields = 0
        for i in warn_list:
            embed.add_field(name="Warned at epoch " + str(i["epoch"]), value="Reason: " + str(i["reason"]))
            fields+=1
        if not fields > 0:
            await ctx.send("User was never warned ;) yayy!")
        else:
            await ctx.send(embed=embed)


@client.command(aliases=['def'])
async def define(ctx, original_word):
    word = parser.fetch(original_word)
    definition = word[0]["definitions"][0]["text"]
    pronunciation = word[0]["pronunciations"]["text"]
    sound = word[0]["pronunciations"]["audio"]
    pages = Pages(ctx, entries=definition, per_page=4, custom_title="Definition of " + original_word)
    await pages.paginate()


@client.command(aliases=["cl"])
async def changelimit(ctx, limit: int):
    to_delete = read_file("to_delete.Json")
    if 0 > limit > 99:
        await ctx.send("Must provide a number between 0 and 99")
        return
    if ctx.channel.id in to_delete.values():
        vc_channel_id = list(to_delete.keys())[list(to_delete.values()).index(ctx.channel.id)]
        vc_channel = client.get_channel(int(vc_channel_id))
        await vc_channel.edit(user_limit=limit)
        await ctx.send("Successfully changed limit")
    else:
        await ctx.send("Channel is not a private channel")


@client.command()
async def nominate(ctx, user: discord.Member, role: discord.Role):
    list_roles = [700732836772053013, 700732374471934053, 701964825227427941, 700733089856356363]
    if role.id in list_roles:
        w=True
        channel = client.get_channel(703035799138074715)  # 703035799138074715
        if str(user.id) in read_file("elections.Json"):
            w=False
        if w:
            add_nominee(user.id, role.id)
            if read_file("elections.Json")["message"] is False:
                x = read_file("elections.Json")
                embed = discord.Embed(title="Election ballots")
                temp = ""
                for i in x.keys():
                    if i != "message":
                        print(i)
                        nom = get_nominee(ctx, i, ctx.guild.get_member(int(i)))
                        role_list = []
                        for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                        list_names = ""
                        for wxz in role_list:
                            list_names += wxz.name
                        temp+='@'+nom.whois.display_name+' - '+" "+list_names
                if temp == "":
                    temp = "N/A"
                embed.add_field(name="Nominations", value=temp)
                message_id = await channel.send(embed=embed)
                x["message"] = message_id.id
                with open("elections.Json", 'w') as file_output_object:
                    json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
                file_output_object.close()
            else:
                message = await channel.fetch_message(int(read_file("elections.Json")["message"]))
                temp = ""
                embed = discord.Embed(title="Election ballots")
                x = read_file("elections.Json")
                for i in x.keys():
                    if i != "message":
                        nom = get_nominee(ctx, i, user_object=ctx.guild.get_member(int(i)))
                        role_list = []
                        for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                        list_names = ""
                        for wxz in role_list:
                            list_names+= " " +wxz.name
                        temp += "\n"+ '@' + nom.whois.display_name + ' - ' + wxz.name
                if temp == "":
                    temp = "N/A"
                embed.add_field(name="Nominations", value=temp)
                await message.edit(embed=embed)
    else:
        message = await channel.fetch_message(int(read_file("elections.Json")["message"]))
        if not int(role.id) in read_file("elections.Json")[str(user.id)]["nominee_role_id"]:
            x = read_file("elections.Json")
            print(x[str(user.id)])
            x[str(user.id)]["nominee_role_id"].append(int(role.id))
            with open("elections.Json", 'w') as file_output_object:
                json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
            x=read_file("elections.Json")
            temp=''
            for i in x.keys():
                if i != "message":
                    nom = get_nominee(ctx, i, user_object=ctx.guild.get_member(int(i)))
                    role_list = []
                    for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                    list_names = ""
                    for wxz in role_list:
                        list_names+=" "+wxz.name
                    temp += "\n"+ '@' + nom.whois.display_name + ' - ' + list_names
                    print(temp)
            embed=discord.Embed(title="Election ballots")
            if temp == "":
                temp = "N/A"
            embed.add_field(name="Nominations", value=temp)
            await message.edit(embed=embed)
        else:
            await ctx.send("User was already nominated")


'''@client.command()
async def help(ctx):
    pages = Pages(ctx, entries=help_list, per_page=6, custom_title="p!help")'''

@client.event
async def on_command_error(ctx, error):
    discord_error = discord.ext.commands.errors
    isinstance_dict = {
        discord_error.MissingPermissions: "Missing permissions to perform that action!",
        discord_error.CommandInvokeError: "There was an error executing that command!",
        discord_error.BadArgument: "One or more arguments are invalid",
    }
    for key in isinstance_dict.keys():
        if isinstance(error, key):
            await ctx.send(isinstance_dict[key])
        print(error)


client.run(config.token)



