# python 3.7
version = '1.11'
import discord  # version 1.3.2
from discord.ext.commands import Bot, CommandNotFound, has_permissions
import json
import functools
from wiktionaryparser import WiktionaryParser
import PyDictionary
import random
from discord.ext import tasks
from Libraries.paginator import Pages
from Libraries.paginator import PagesFromMessage
from Libraries.pirate_lib import get_topic
import operator
from Libraries.pirate_lib import write_file, pull_flag, read_file, get_nominee, add_nominee, append_topic, _resolve_member_id, pirate_error
from config.config import get_config
import time
import argparse
import shlex
import traceback

parser = WiktionaryParser()
epoch = time.time()
config = get_config()
last_topic = -1
list_numbers_banned = []
client = config.client
client.remove_command("help")
initial_extensions = ['cogs.Money', 'cogs.voice_cog', 'cogs.voting', 'cogs.elections', 'cogs.miscellaneous']


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    
    for extension in initial_extensions:
        client.load_extension(extension)


@client.event
async def on_message(message):
    await client.process_commands(message)

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
            await ctx.send(isinstance_dict[key] + "\n" + str(error))
        print(error)


client.run(config.token)
