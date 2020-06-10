import discord
from discord.ext import commands
import time
from Libraries.pirate_lib import read_file, write_file, append_topic, get_topic
from config.config import admin_list
from wiktionaryparser import WiktionaryParser
from Libraries.paginator import Pages, PagesFromMessage
from textblob import TextBlob
import json
import time
import operator
from iso639 import languages
from random_word import RandomWords
random_words = RandomWords()
parser = WiktionaryParser()

SUGGESTIONS_CHANNEL = 701922472538144778
IDK_THIS_CHANNEL = 703480588430082110
HELP_CHANNEL = 700754951558660106
HELP_LOGS_CHANNEL = 700731099705508010
PRELIM_VOTING_CHANNEL = 703467261176053811
VOTING_CHANNEL = 703467201683914822
UPVOTE_EMOJI = "<:voteaye:701929407647842374>"
UPVOTE_ID = 701929407647842374
DOWNVOTE_EMOJI = "<:votenay:701929705074589696>"
DOWNVOTE_ID = 701929705074589696
HELP_LIST = ['Correctme: adds the Correctme tag to your nickname', "Define: returns wiktionary's definition of a word", 'Members: returns the amount of non-bot users in the guild', 'Topic: returns a topic pseudo-randomely', 'TopLanguage: returns the top languages by message count']
WORD_OF_THE_DAY_CHANNEL_ID = None
STUDENT_MODE_ROLE_ID = 720369584481501295

class Miscellaneous(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.epoch = time.time()
        self.last_topic = ""
        self.version = '1.0.3'
        self.changelog = "**__1.03__**:\n・Added student mode function (implemented)\n・Added changelog"

    @commands.command()
    async def changelog(self, ctx):
        await ctx.send(self.changelog)

    @commands.command()
    async def members(self, ctx):
        list_members = ctx.guild.members
        list_users = []
        for i in list_members:
            if i.bot is False:
                list_users.append(i)
        await ctx.send("There are {0} sailors on the ship".format(len(list_users)))

    @commands.command(aliases=['stmd'])
    async def studentmode(self, ctx):
        role = ctx.guild.get_role(STUDENT_MODE_ROLE_ID)
        if role in ctx.author.roles:
            await ctx.author.remove_roles(role)
            await ctx.send("Remove Student Mode")
        else:
            await ctx.author.add_roles(role)
            await ctx.send("Added Student Mode")
    @commands.command(aliases=['ver'])
    async def version(self, ctx):
        await ctx.send('version {0}'.format(self.version))

    @commands.command()
    async def topic(self, ctx):
        if time.time() - self.epoch > 299:
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

    async def get_word_of_the_day(self):
        word_of_the_day = random_words.get_random_word(hasDictionaryDef="true", includePartOfSpeech="noun,verb,adjective", minCorpusCount=1, maxCorpusCount=10, minDictionaryCount=1, maxDictionaryCount=10, minLength=5)
        return word_of_the_day

    @commands.command(aliases=['def'])
    async def define(self, ctx, *original_word):
        word = "_".join(original_word)
        if str.lower(word) == "pepely":
            definition = ["timidly or shyly \n *He pepely looked around the corner* - Coal", "Rapidly peeking at someone or something \n *I pepely peaked in the locker-room* - Law", "doing something and making it the shittiest work ever \n *Dmitri never gets it right; whatever he does, he does it pepely, indeed.* - Neo"]
            pages = Pages(ctx, entries=definition, per_page=4, custom_title="Definition of " + " ".join(original_word))
            await pages.paginate()
            return
        if str.lower(word) == "breadly":
            definition = ["to do as a personified piece of bread would. \n *I love putting my hands in wheat, you know, massaging it, breadly*. - Panto", "cook something like how you bake bread \n *Ma' man always cooks da meat breadly.* - Neo"]
            pages = Pages(ctx, entries=definition, per_page=4, custom_title="Definition of " + " ".join(original_word))
            await pages.paginate()
            return
        word = parser.fetch(word)
        pronunciation = word[0]["pronunciations"]["text"]
        definition = word[0]["definitions"][0]["text"]
        definition.pop(0)
        if not definition:
            await ctx.send('Word was not found, try changing the capitalization and check your spelling!')
            return
        sound = word[0]["pronunciations"]["audio"]
        pages = Pages(ctx, entries=definition, per_page=4, custom_title="Definition of " + " ".join(original_word))
        await pages.paginate()

    @commands.command(aliases=['evv'])
    async def evaluatevalue(self, ctx, *, arg):
        if ctx.message.author.id in admin_list:
            arg="".join(arg)
            x=eval(arg)
            await ctx.send(x)
            try:
                z = await x
                await ctx.send(z)
            except:
                pass

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
        await self.handle_help(message)
        await self.handle_tags(message)
        await self.handle_language(message)
        await self.handle_kyando(message)
        await self.handle_suggestion(message)
        if self.bot.user in message.mentions:
            pages = PagesFromMessage(self.bot, message, entries=HELP_LIST, per_page=10, custom_title="Here's the list of commands:")
            await pages.paginate()

    async def handle_help(self, message):
        help_logs_channel = self.bot.get_channel(HELP_LOGS_CHANNEL)
        if message.channel.id == HELP_CHANNEL:
            content = message.content
            await help_logs_channel.send("Help request from "+ message.author.mention + ": \n"+content + "\n||@here||")
            await message.delete()

    async def handle_tags(self, message):
        if str.lower(message.content) in read_file('data/tags.Json'):
            await message.channel.send(str(read_file('data/tags.Json')[str.lower(message.content)]))

    async def handle_language(self, message):
        if len(message.content)>3:
            lang = TextBlob(message.content)
            language = lang.detect_language()
            if language:
                if language not in read_file('data/languages.Json'):
                    write_file('data/languages.Json', 1, language)
                else:
                    x = read_file('data/languages.Json')
                    x[language]+=1
                    with open("data/languages.Json", 'w') as file_output_object:
                        json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '),
                                  skipkeys=True)

    async def handle_kyando(self, message):
        if "kyando" in str.lower(message.content):
            await self.bot.get_user(331431342438875137).send("You were mentioned in: "+ message.jump_url)

    async def handle_suggestion(self, message):
        if message.channel.id == SUGGESTIONS_CHANNEL and str.lower(message.content).startswith("suggestion: "):
            write_file("data/suggestions.Json", { "suggestion": message.content[len("suggestion: "):], "jump_url": message.jump_url })
            await message.channel.send("Suggestion saved.")
            channel = self.bot.get_channel(IDK_THIS_CHANNEL)
            text = message.content.replace("Suggestion: ", "", 1)
            await channel.send("**Suggestion: **" + text.replace("suggestion: ", "", 1) + "\n")

    @commands.command(aliases=['tl'])
    async def toplanguage(self, ctx, amount:int=10):
        x = read_file('data/languages.Json')
        temp = ""
        sorted_list = sorted(x.items(), key=operator.itemgetter(1))
        sorted_list = list(reversed(sorted_list))
        del sorted_list[amount:]
        for i in sorted_list:
            try:
                language = languages.get(alpha2=i[0])
                text = language.name
            except:
                text = i[0]
            temp+=text+": "+str(i[1]) + "\n"
        await ctx.send(temp)

    @commands.command(aliases=['cm'])
    async def correctme(self, ctx):
        if "✍" in ctx.author.display_name:
            await ctx.author.edit(nick=ctx.author.display_name.replace("✍", ""))
            await ctx.send("Removed correct me tag")
        else:
            await ctx.author.edit(nick=ctx.author.display_name+" ✍")
            await ctx.send("Added correct me tag")

    @commands.command(aliases=['sp'])
    async def startprelim(self, ctx):
        if ctx.author.id in admin_list:
            channel = self.bot.get_channel(PRELIM_VOTING_CHANNEL)

            for i in read_file('data/suggestions.Json'):
                await self.post_suggestion(channel, i['suggestion'], i['jump_url'])
                time.sleep(.3)

    @commands.command(aliases=['ptv'])
    async def prelimtovote(self, ctx):
        if ctx.author.id in admin_list:
            prelim_voting_channel = self.bot.get_channel(PRELIM_VOTING_CHANNEL)
            voting_channel = self.bot.get_channel(VOTING_CHANNEL)
            bot_messages = await prelim_voting_channel.history().filter(lambda member: member.author.id == self.bot.user.id).flatten()
            bot_messages.reverse()

            for message in bot_messages:
                num_upvotes = 0
                num_downvotes = 0

                for reaction in map(lambda reaction: (reaction.emoji.id, reaction.count), message.reactions):
                    if reaction[0] == UPVOTE_ID:
                        num_upvotes = num_upvotes + reaction[1]
                    elif reaction[0] == DOWNVOTE_ID:
                        num_downvotes = num_downvotes + reaction[1]

                if num_upvotes > num_downvotes:
                    # extract suggestion and jump_url from previous embed

                    await self.post_suggestion(self.bot.get_channel(VOTING_CHANNEL), message.embeds[0].fields[0].value, message.embeds[0].fields[1].value)

    @commands.command(aliases=['help', '?'])
    async def help_command(self, ctx):
        pages = Pages(ctx, entries=HELP_LIST, per_page=10, custom_title="Help")
        await pages.paginate()

    async def post_suggestion(self, channel, suggestion, jump_url = "N/A"):
        embed = discord.Embed(title="Vote")
        embed.add_field(name="Suggestion", value=suggestion[:len(suggestion) if len(suggestion) <= 1024 else 1024], inline=False)
        embed.add_field(name="More Info", value=jump_url, inline=False)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/700731399019167827/704371197483286679/banner.png")

        message = await channel.send(embed=embed)
        await message.add_reaction(UPVOTE_EMOJI)
        await message.add_reaction(DOWNVOTE_EMOJI)


def setup(bot):
    bot.add_cog(Miscellaneous(bot))
