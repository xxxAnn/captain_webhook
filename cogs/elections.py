from discord.ext import commands
import discord
from Libraries.pirate_lib import read_file, write_file, add_nominee, get_nominee, update_nominations
import json


class ElectionCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nominate(self, ctx, user: discord.Member, role: discord.Role):
        list_roles = [700732836772053013, 700732374471934053, 701964825227427941, 700733089856356363]
        channel = self.bot.get_channel(703035799138074715)  # 703035799138074715
        if role.id in list_roles or True:
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


def setup(bot):
    bot.add_cog(ElectionCog(bot))
