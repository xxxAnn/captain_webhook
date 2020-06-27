import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta
from Libraries.pirate_lib import read_file, write_file, append_topic, get_topic
import time

PRELIM_VOTING_CHANNEL_ID = 701954343447953428 # 703467261176053811
VOTING_CHANNEL_ID = 703467201683914822
SHIP_CREW = 701963261557342299
SAILOR = 702282763570511882
UPVOTE_EMOJI = "<:voteaye:701929407647842374>"
UPVOTE_ID = 701929407647842374
DOWNVOTE_EMOJI = "<:votenay:701929705074589696>"
DOWNVOTE_ID = 701929705074589696

class Voting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.loop_prelim.start()
        self.loop_voting.start()
        guild = self.bot.get_guild(700665943835148330)
        self.ship_crew_role = guild.get_role(SHIP_CREW)
        self.sailor_role = guild.get_role(SAILOR)
        self.voting_channel = guild.get_channel(VOTING_CHANNEL_ID)
        self.prelim_voting_channel = guild.get_channel(PRELIM_VOTING_CHANNEL_ID)

    def cog_unload(self):
        self.loop_prelim.cancel()

    @tasks.loop(hours=168)
    async def loop_prelim(self):
        await self.start_prelims()

    @loop_prelim.before_loop
    async def before_loop_prelim(self):
        print('hey')
        datetime_obj = await self.get_next_weekday(5)
        print(datetime_obj)
        await discord.utils.sleep_until(datetime_obj)
        
    async def get_next_weekday(self, weekday):
        d = datetime.utcnow().replace(hour=0, minute=0, second=0)
        t = timedelta((7 + weekday - d.weekday()) % 7)
        return (d + t)

    async def start_prelims(self):
        await self.voting_channel.set_permissions(self.ship_crew_role, read_messages=False)
        await self.prelim_voting_channel.set_permissions(self.ship_crew_role, read_messages=True, send_messages=False)
        await self.prelim_voting_channel.set_permissions(self.sailor_role, read_messages=True, send_messages=False)
        for i in read_file('data/suggestions.Json'):
            await self.post_suggestion(self.prelim_voting_channel, i['suggestion'], i['jump_url'])
            time.sleep(.3)

    async def post_suggestion(self, channel, suggestion, jump_url = "N/A"):
        embed = discord.Embed(title="Vote")
        embed.add_field(name="Suggestion", value=suggestion[:len(suggestion) if len(suggestion) <= 1024 else 1024], inline=False)
        embed.add_field(name="More Info", value=jump_url, inline=False)
        embed.set_thumbnail(url="https://media.discordapp.net/attachments/700731399019167827/704371197483286679/banner.png")

        message = await channel.send(embed=embed)
        await message.add_reaction(UPVOTE_EMOJI)
        await message.add_reaction(DOWNVOTE_EMOJI)

    @tasks.loop(hours=168)
    async def loop_voting(self):
        await self.start_voting()

    async def start_voting(self):
        await self.voting_channel.set_permissions(self.ship_crew_role, read_messages=True)
        await self.prelim_voting_channel.set_permissions(self.ship_crew_role, read_messages=False, send_messages=False)
        await self.prelim_voting_channel.set_permissions(self.sailor_role, read_messages=False, send_messages=False)
        bot_messages = await self.prelim_voting_channel.history().filter(lambda member: member.author.id == self.bot.user.id).flatten()
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

                await self.post_suggestion(self.voting_channel, message.embeds[0].fields[0].value, message.embeds[0].fields[1].value)

    @loop_voting.before_loop
    async def before_loop_voting(self):
        datetime_obj = await self.get_next_weekday(0)
        await discord.utils.sleep_until(datetime_obj)


def setup(bot):
    bot.add_cog(Voting(bot))
