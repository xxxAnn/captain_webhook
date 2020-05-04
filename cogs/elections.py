from discord.ext import commands
import discord
from Libraries.pirate_lib import read_file, write_file, add_nominee, get_nominee, update_nominations
import json
PRELIM_CHANNEL_ID = 703043049806233620  # 703043049806233620
UPVOTE_EMOJI ="<:voteaye:701929407647842374>"
DOWNVOTE_EMOJI ="<:votenay:701929705074589696>"


class ElectionCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nominate(self, ctx, user: discord.Member, role: discord.Role):
        list_roles = [700732836772053013, 700732374471934053, 701964825227427941, 700733089856356363]
        channel = self.bot.get_channel(703035799138074715)  # 703035799138074715
        if role.id in list_roles:
            if not str(user.id) in read_file("data/elections.Json"):
                add_nominee(user.id, role.id)
            if role.id not in read_file("data/elections.Json")[str(user.id)]["nominee_role_id"]:
                wx = read_file('data/elections.Json')
                wx[str(user.id)]['nominee_role_id'].append(role.id)
                with open("data/elections.Json", 'w') as file_output_object:
                    json.dump(wx, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
            if read_file("data/elections.Json")["message"] is False:
                message = await channel.send("_ _")
                x = read_file('data/elections.Json')
                x["message"] = message.id
                with open("data/elections.Json", 'w') as file_output_object:
                    json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
                file_output_object.close()
            message = await channel.fetch_message(int(read_file("data/elections.Json")["message"]))
            await update_nominations(ctx, message)
        else:
            await ctx.send("Role cannot be nominated")

    @commands.command(aliases=['esp'])
    async def electionstartprelim(self, ctx):
        channel = self.bot.get_channel(PRELIM_CHANNEL_ID)
        election_file = read_file('data/elections.Json')
        for user in election_file.keys():
            if user != "message":
                for role in election_file[user]["nominee_role_id"]:
                    embed = discord.Embed(title="Preliminary Voting")
                    embed.add_field(name="Vote nominee: " + self.bot.get_user(int(user)).display_name + "#" + self.bot.get_user(int(user)).discriminator + " for the following role:", value=ctx.guild.get_role(int(role)).mention)
                    message = await channel.send(embed=embed)
                    await message.add_reaction(UPVOTE_EMOJI)
                    await message.add_reaction(DOWNVOTE_EMOJI)


def setup(bot):
    bot.add_cog(ElectionCog(bot))
