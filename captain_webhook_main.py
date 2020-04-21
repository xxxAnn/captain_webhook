# python 3.7
import discord  # version 1.3.2
from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from discord.ext.commands import has_permissions
import json
from pirate_lib import get_topic
from pirate_lib import append_topic
from config import get_config
import time
epoch = time.time()
print("hey")
config = get_config()
client = Bot(command_prefix=config.prefix, case_insensitive=True)


@client.event
async def on_ready():
    print(client)
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel.id == 701922472538144778 and str.lower(message.content).startswith("suggestion:"):
        with open('suggestions.Json', 'r') as suggestions:
            suggestion_list = json.load(suggestions)
        suggestions.close()
        suggestion_list.append(message.content)
        with open('suggestions.Json', 'w') as suggestion_output:
            json.dump(suggestion_list, suggestion_output)
        await message.channel.send("Suggestion saved")




@client.event
async def on_voice_state_update(member, before, after):
    channel = after.channel
    if channel is not None:
        if channel.id == 702169810028724297:
            guild = member.guild
            category = client.get_channel(700665944279875654)
            channel = await guild.create_voice_channel(name="2 People Group", user_limit=2, category=category)
            await member.move_to(channel)
            with open('to_delete.Json', 'r') as to_delete:
                to_delete_list = json.load(to_delete)
            to_delete.close()
            to_delete_list.append(channel.id)
            with open('to_delete.Json', 'w') as to_delete_output:
                json.dump(to_delete_list, to_delete_output)
    channel = before.channel
    if channel is not None:
        with open('to_delete.Json', 'r') as to_delete:
            to_delete_list = json.load(to_delete)
            print(str(channel.id) + str(to_delete_list))
            if len(channel.members) == 0 and channel.id in to_delete_list:
                print("hey there")
                await channel.delete()


@client.command()
async def topic(ctx, epoch=epoch):
    if time.time()-epoch>179:
        epoch = time.time()
        await ctx.send(config.default_topic_message.format(get_topic()))
    else:
        await ctx.send("Command is on cooldown, please wait {0} seconds".format(str(int(180-(time.time()-epoch)))))


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



