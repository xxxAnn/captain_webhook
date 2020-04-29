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

def setup(bot):
    bot.add_cog(Miscellaneous(bot))