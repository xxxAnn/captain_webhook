import discord
from discord.ext import commands
import random
import functools
from Libraries.pirate_lib import write_file, read_file


class VoiceCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.to_delete = 'data/to_delete.Json'
        self.list_numbers_banned = []

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = after.channel
        if channel is not None:
            if channel.id == 702169810028724297: # 702169810028724297
                guild = member.guild
                category = self.bot.get_channel(700665944279875654) # 700665944279875654
                channel_number = random.randint(1111, 9999)
                while channel_number in self.list_numbers_banned:
                    channel_number = random.randint(1111, 9999)
                self.list_numbers_banned.append(channel_number)
                channel = await guild.create_voice_channel(name="Private group {0}".format(channel_number), user_limit=2, category=category) # create channel
                # role = guild.get_role(700732374471934053)
                overwrite = {
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    member: discord.PermissionOverwrite(read_messages=True),
                    # role: discord.PermissionOverwrite(read_messages=True),
                    self.bot.user: discord.PermissionOverwrite(manage_permissions=True, read_messages=True, manage_channels=True)
                }
                text_channel = await guild.create_text_channel(name="private-group-{0}".format(channel_number), category=category, position=0, overwrites=overwrite)
                message = "**__Welcome to your private chat room!__\n Only users who are in the designated voice channel can see this room! Please follow the rules as these rooms are moderated!\n\nYou can use the p!changelimit (p!cl) command to change the amount of members that can join your channel!\nHave fun!! ||{0} ping ;)||**".format(member.mention)
                await text_channel.send(message)
                await member.move_to(channel) # move member
                write_file(self.to_delete, value=text_channel.id, key=str(channel.id)) # adds channel id to the "to_delete" list
            to_delete_list = read_file(self.to_delete)
            if str(channel.id) in to_delete_list.keys():
                text_channel = self.bot.get_channel(to_delete_list[str(channel.id)])
                await text_channel.set_permissions(member, read_messages=True)
        channel = before.channel
        if channel is not None:
            to_delete_list = read_file(self.to_delete)
            if len(channel.members) == 0 and str(channel.id) in to_delete_list.keys(): # checks if channel has no one and if it's in the "to_delete" list
                await channel.delete()
                text_channel = self.bot.get_channel(to_delete_list[str(channel.id)])
                await text_channel.delete()
            elif str(channel.id) in to_delete_list.keys() and after.channel is not before.channel:
                text_channel = self.bot.get_channel(to_delete_list[str(channel.id)])
                if not member.guild.get_role(700732374471934053) in member.roles:
                    await text_channel.set_permissions(member, read_messages=False)

    @commands.command(aliases=["cl"])
    async def changelimit(self, ctx, limit: int):
        to_delete = read_file("data/to_delete.Json")
        if 0 > limit > 99:
            await ctx.send("Must provide a number between 0 and 99")
            return
        if ctx.channel.id in to_delete.values():
            vc_channel_id = list(to_delete.keys())[list(to_delete.values()).index(ctx.channel.id)]
            vc_channel = self.bot.get_channel(int(vc_channel_id))
            await vc_channel.edit(user_limit=limit)
            await ctx.send("Successfully changed limit")
        else:
            await ctx.send("Channel is not a private channel")

def setup(bot):
    bot.add_cog(VoiceCog(bot))