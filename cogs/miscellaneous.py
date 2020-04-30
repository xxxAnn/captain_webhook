import discord
from discord.ext import commands
import time
from Libraries.pirate_lib import read_file, write_file, append_topic, get_topic
from config.config import admin_list
from wiktionaryparser import WiktionaryParser
from Libraries.paginator import Pages
parser = WiktionaryParser()


class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.epoch = time.time()
        self.last_topic = ""

    @commands.command()
    async def members(self, ctx):
        list_members = ctx.guild.members
        list_users = []
        for i in list_members:
            if i.bot is False:
                list_users.append(i)
        await ctx.send("There are {0} sailors on the ship".format(len(list_users)))

    @commands.command()
    async def topic(self, ctx):
        if time.time() - self.epoch > 9:
            self.epoch = time.time()  # resets the epoch time
            embed = discord.Embed(title="Conversation topic", color=0x0d25cc)
            topic_variable = get_topic()
            while topic_variable == self.last_topic:
                topic_variable = get_topic()
            self.last_topic = topic_variable
            embed.add_field(name="{0}".format(topic_variable), value="Answer or walk the plank!")
            await ctx.send(embed=embed)
        else:
            await ctx.send(
                "Command is on cooldown, please wait {0} seconds".format(str(int(10 - (time.time() - self.epoch)))))

    @commands.command()
    async def addtopic(self, ctx, *topic):
        if ctx.author.id in admin_list:
            topic = " ".join(topic)
            topic = topic.replace("’", "'")
            append_topic(topic)
            await ctx.send("Added successfully")
        else:
            await ctx.send("You do not have permission to do that")

    @commands.command(aliases=['def'])
    async def define(self, ctx, original_word):
        word = parser.fetch(original_word)
        definition = word[0]["definitions"][0]["text"]
        pronunciation = word[0]["pronunciations"]["text"]
        sound = word[0]["pronunciations"]["audio"]
        pages = Pages(ctx, entries=definition, per_page=4, custom_title="Definition of " + original_word)
        await pages.paginate()

    @commands.command(aliases=["langdiff", "langdifficulty", "lh", "ld"])
    async def languagedifficulty(self, ctx):
        await ctx.send("How hard a language is depends mostly on the languages you already know and your motivation to learn said language")

    @commands.command()
    async def tag(self, ctx,  *, arg):
        if ctx.author.id in admin_list:
            arg = arg.split('|')
            arg[0] = str.lower(arg[0])
            write_file('data/tags.Json', arg[1], arg[0])
            await ctx.send("Successfully added tag")
        else:
            await ctx.send("You do that silly")

    @commands.Cog.listener()
    async def on_message(self, message):
        help_channel_id = 700754951558660106
        help_logs_channel = self.bot.get_channel(700731099705508010)
        if message.channel.id == help_channel_id:
            content = message.content
            await help_logs_channel.send("Help request from "+ message.author.mention + ": \n"+content + "\n||@here||")
            await message.delete()
        elif str.lower(message.content) in read_file('data/tags.Json'):
            await message.channel.send(str(read_file('data/tags.Json')[str.lower(message.content)]))


def setup(bot):
    bot.add_cog(Miscellaneous(bot))