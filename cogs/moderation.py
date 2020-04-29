import time
from discord.ext import commands
import discord
from config.config import moderator_list, admin_list, log_channel
from Libraries.pirate_lib import write_file, read_file


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def warn(self, ctx, user: discord.Member, *, arg):
        if ctx.author.id in moderator_list or ctx.author.id in admin_list:
            if arg:
                user_id = str(user.id)
                moderator_id = str(ctx.author.id)
                warn_dict = {
                    "user_id": user_id,
                    "reason": arg,
                    "epoch": int(time.time()),
                    "moderator_id": moderator_id,
                    "punishment_type": "warn"
                }
                await user.send("You have been warned for the following reason: {0}".format(arg))
                write_file("data/warns.Json", warn_dict)
                await ctx.send("Successfully warned user")
                embed = discord.Embed(title="WARN {0}#{1}".format(user.display_name, user.discriminator), color=0x0d25cc)
                embed.add_field(name="User".format(user.display_name),
                                value="{0}".format(user.mention))
                embed.add_field(name="Moderator".format(user.display_name),
                                value="{0}".format(ctx.author.mention))
                embed.add_field(name="Reason".format(arg),
                                value="{0}".format(arg))
                embed.add_field(name="Channel".format(user.display_name),
                                value="{0}".format(ctx.channel))
                await ctx.guild.get_channel(log_channel).send(embed=embed)
            else:
                await ctx.send("Missing required argument")
        else:
            await ctx.send("You don't have permission to do that, silly.")

    @commands.command(aliases=['infractions', 'warnings', 'viewwarn'])
    async def viewwarns(self, ctx, *user: discord.User):
        if not user:
            user = ctx.author
        else:
            user = user[0]
        if user == ctx.author or ctx.author.id in config.moderators or ctx.author.id in config.admins:
            warns = read_file('data/warns.Json')
            warn_list = []
            for warn in warns:
                if warn["user_id"] == str(user.id):
                    warn_list.append(warn)
            embed=discord.Embed(title="Warnings", color=0x0d25cc)
            fields = 0
            for i in warn_list:
                embed.add_field(name="Warned at epoch " + str(i["epoch"]), value="Reason: " + str(i["reason"]))
                fields+=1
            if not fields > 0:
                await ctx.send("User was never warned ;) yayy!")
            else:
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Moderation(bot))