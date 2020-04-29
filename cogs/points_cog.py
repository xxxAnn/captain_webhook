import discord
from discord.ext import commands
from Libraries.pirate_lib import write_file, read_file
import operator
import time
import datetime


class PointCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['lb', 'top'])
    async def leaderboard(self, ctx, amount:int=10):
        temp_dict = read_file('data/user_data.Json')
        points_dict = {}
        for i in temp_dict.keys():
            if "voice_points" in temp_dict[i]:
                points_dict[i] = temp_dict[i]["voice_points"]+temp_dict[i]["text_points"]
        sorted_list = sorted(points_dict.items(), key=operator.itemgetter(1))
        sorted_list = list(reversed(sorted_list))
        del sorted_list[amount:]
        string = "```pl\n"
        x=0
        for element in sorted_list:
            txt = element[0]
            usa = self.bot.get_user(int(txt))
            if usa is None:
                break
            val = element[1]
            val = f'{val:,}'.format(val=val)
            string = string + "{" + str(x + 1) + "}     #" + usa.display_name + "\n        Points : [" + str(
                val) + "] " + "\n"
            x+=1
        string = string + '```'
        await ctx.send(string)

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.author.id) not in read_file("data/user_data.Json"):
            write_file('data/user_data.Json', {'voice_points': 0, 'text_points': 0, 'cooldown': time.time()}, str(message.author.id))
        user_data = read_file('data/user_data.Json')[str(message.author.id)]
        if time.time() - user_data['cooldown'] > 12:
            user_data['cooldown'] = time.time()
            user_data['text_points'] += 1
            write_file('data/user_data.Json', user_data, str(message.author.id))


def setup(bot):
    bot.add_cog(PointCog(bot))