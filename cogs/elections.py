from discord.ext import commands
import discord
from Libraries.pirate_lib import read_file, write_file, add_nominee, get_nominee
import json

class ElectionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nominate(self, ctx, user: discord.Member, role: discord.Role):
        list_roles = [700732836772053013, 700732374471934053, 701964825227427941, 700733089856356363]
        channel = self.bot.get_channel(703035799138074715)  # 703035799138074715
        if role.id in list_roles or True:
            w=True
            if str(user.id) in read_file("data/elections.Json"):
                w=False
            if w:
                add_nominee(user.id, role.id)
                if read_file("data/elections.Json")["message"] is False:
                    x = read_file("data/elections.Json")
                    embed = discord.Embed(title="Election ballots")
                    temp = ""
                    for i in x.keys():
                        if i != "message":
                            print(i)
                            nom = get_nominee(ctx, i, ctx.guild.get_member(int(i)))
                            role_list = []
                            for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                            list_names = ""
                            for wxz in role_list:
                                list_names += wxz.name
                            temp+='@'+nom.whois.display_name+' - '+" "+list_names
                    if temp == "":
                        temp = "N/A"
                    embed.add_field(name="Nominations", value=temp)
                    message_id = await channel.send(embed=embed)
                    x["message"] = message_id.id
                    with open("data/elections.Json", 'w') as file_output_object:
                        json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
                    file_output_object.close()
                else:
                    message = await channel.fetch_message(int(read_file("data/elections.Json")["message"]))
                    temp = ""
                    embed = discord.Embed(title="Election ballots")
                    x = read_file("data/elections.Json")
                    for i in x.keys():
                        if i != "message":
                            nom = get_nominee(ctx, i, user_object=ctx.guild.get_member(int(i)))
                            role_list = []
                            for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                            list_names = ""
                            for wxz in role_list:
                                list_names+= " " +wxz.name
                            temp += "\n"+ '@' + nom.whois.display_name + ' - ' + wxz.name
                    if temp == "":
                        temp = "N/A"
                    embed.add_field(name="Nominations", value=temp)
                    await message.edit(embed=embed)
            else:
                print('hey')
                if read_file("data/elections.Json")["message"] is False:
                    message = await channel.send("You shouldn't see this")
                    with open('data/elections.Json', 'r') as file_object:
                        data =read_file('data/elections.Json')
                        data['message'] = channel.id
                        json.dump(data, file_object, sort_keys=True, indent=4, separators=(',', ': '))
                else:
                    message = await channel.fetch_message(int(read_file("data/elections.Json")["message"]))
                if not int(role.id) in read_file("data/elections.Json")[str(user.id)]["nominee_role_id"]:
                    print('scenario3')
                    x = read_file("data/elections.Json")
                    x[str(user.id)]["nominee_role_id"].append(int(role.id))
                    with open("data/elections.Json", 'w') as file_output_object:
                        json.dump(x, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))
                    x=read_file("data/elections.Json")
                    temp=''
                    for i in x.keys():
                        if i != "message":
                            nom = get_nominee(ctx, i, user_object=ctx.guild.get_member(int(i)))
                            role_list = []
                            for role_id in nom.for_role: role_list.append(ctx.guild.get_role(int(role_id)))
                            list_names = ""
                            for wxz in role_list:
                                list_names+=" "+wxz.name
                            temp += "\n"+ '@' + nom.whois.display_name + ' - ' + list_names
                            print(temp)
                    embed=discord.Embed(title="Election ballots")
                    if temp == "":
                        temp = "N/A"
                    embed.add_field(name="Nominations", value=temp)
                    await message.edit(embed=embed)
                else:
                    await ctx.send("User was already nominated")

def setup(bot):
    bot.add_cog(ElectionCog(bot))