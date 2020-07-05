from discord.ext import commands
import discord
from Libraries.pirate_lib import read_file, write_file, add_nominee, get_nominee, update_nominations
import json
from config.config import admin_list
import re
PRELIM_CHANNEL_ID = 703043049806233620  # 703043049806233620
BALLOT_CHANNEL_ID = 703035799138074715
UPVOTE_EMOJI ="<:voteaye:701929407647842374>"
DOWNVOTE_EMOJI ="<:votenay:701929705074589696>"
UPVOTE_EMOJI_ID = 701929407647842374
DOWNVOTE_EMOJI_ID = 701929705074589696


class ElectionCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.election_contents = read_file("data/elections.Json")

    @commands.command()
    async def nominate(self, ctx, user: discord.Member, role: discord.Role):
        list_roles = [700732836772053013, 700732374471934053, 701964825227427941, 700733089856356363, 724915974943408177]
        channel = self.bot.get_channel(BALLOT_CHANNEL_ID)  # 703035799138074715,
        if role.id in list_roles:
            if not str(user.id) in read_file("data/elections.Json"):
                add_nominee(user.id, role.id)
            if self.role_id_not_in_elections(role.id, user.id):
                self.add_role_id_to_elections(role.id, user.id)
            if read_file("data/elections.Json")["message"] == False:
                message = await channel.send("_ _")
                self.election_contents["message"] = message.id
                self.write_to_file("data/elections.Json", self.election_contents)
            message = await channel.fetch_message(int(read_file("data/elections.Json")["message"]))
            await update_nominations(ctx, message)
        else:
            await ctx.send("Role cannot be nominated")

    def role_id_not_in_elections(self, role_id, user_id):
        for nomination in read_file("data/elections.Json")[str(user_id)]:
            if role_id == nomination['nominee_role_id']:
                return False
        return True

    def add_role_id_to_elections(self, role_id, user_id):
        self.election_contents = read_file("data/elections.Json")
        self.election_contents[str(user_id)].append({ "nominee_role_id": role_id, "votes":[] })
        self.write_to_file("data/elections.Json", self.election_contents)

    @commands.command(aliases=['esp'])
    async def electionstartprelim(self, ctx):
        if ctx.author.id in admin_list:
            channel = self.bot.get_channel(PRELIM_CHANNEL_ID)
            election_file = self.election_contents
            for user in election_file.keys():
                if user != "message":
                    for nomination in election_file[user]:
                        role = nomination['nominee_role_id']

                        embed = discord.Embed(title="Preliminary Voting")
                        embed.add_field(name="Vote nominee: ", value="<@"+str(int(user))+">")
                        embed.add_field(name="Role: ", value=ctx.guild.get_role(int(role)).mention)
                        message = await channel.send(embed=embed)
                        await message.add_reaction(UPVOTE_EMOJI)
                        await message.add_reaction(DOWNVOTE_EMOJI)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.channel.id == PRELIM_CHANNEL_ID and user.id != self.bot.user.id:
            message = reaction.message.embeds[0]
            nominee_id = re.match(r'^.*?(\d+).*$', message.fields[0].value).groups()[0]
            role_id = re.match(r'^.*?(\d+).*$', message.fields[1].value).groups()[0]

            wx = self.election_contents
            nomination_votes = wx[str(nominee_id)][self.find_nomination_index(wx[str(nominee_id)], role_id)]['votes']
            if reaction.emoji.id == UPVOTE_EMOJI_ID:
                vote_index = self.check_for_duplicates(nomination_votes, user.id)
                if vote_index == -1:
                    nomination_votes.append({ 'user_id': user.id, 'vote': 1})
                else:
                    nomination_votes[vote_index]['vote'] = 1

                self.write_to_file("data/elections.Json", wx)

            elif reaction.emoji.id == DOWNVOTE_EMOJI_ID:
                vote_index = self.check_for_duplicates(nomination_votes, user.id)
                if vote_index == -1:
                    nomination_votes.append({ 'user_id': user.id, 'vote': -1})
                else:
                    nomination_votes[vote_index]['vote'] = -1

                self.write_to_file("data/elections.Json", wx)

            await reaction.remove(user)
            await user.send("Your vote has been counted ✅")

    def find_nomination_index(self, nominee, role_id):
        index = 0
        for nomination in nominee:
            if nomination['nominee_role_id'] == int(role_id):
                return index
            index += 1

    def check_for_duplicates(self, votes, user_id):
        index = 0
        for vote in votes:
            if vote['user_id'] == int(user_id):
                return index
        return -1

    def write_to_file(self, file_name, input):
        with open(file_name, 'w') as file_output_object:
            json.dump(input, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))

    @commands.command()
    async def jsonify(self, ctx):
        for user in self.election_contents.keys():
            if user != "message":
                nominee_role_ids = list(map(lambda id: { 'nominee_role_id': id, 'votes': [] }, self.election_contents[user]['nominee_role_id']))
                self.election_contents[user] = nominee_role_ids
                self.write_to_file('data/elections.Json', self.election_contents)


def setup(bot):
    bot.add_cog(ElectionCog(bot))
