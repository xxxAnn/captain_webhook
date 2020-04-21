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
    channel = client.get_channel(701954343447953428)
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



