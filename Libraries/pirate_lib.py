import json
import random
import requests
import discord


class pirate_error(Exception):

    def __init__(self, *args):
        if args:
            self.txt = args[0]
        else:
            self.txt = None

    def __str__(self):
        if self.txt:
            return "Yarrr Pirate!! Something went wrong: {0}".format(self.txt)
        else:
            return "Yarrr Pirate!! Something unexpected happened"


def get_topic():
    with open('data/topics.Json', 'r') as topic_file:
        topic_list = json.load(topic_file)
        return random.choice(topic_list)


def append_topic(topic):
    topic_list = read_file('data/topics.Json')
    topic_list.append(topic)
    with open('data/topics.Json', 'w') as topic_file_output:
        json.dump(topic_list, topic_file_output)


def write_file(filename, value, key=None):
    file_content = read_file(filename)
    if isinstance(file_content, dict):
        file_content[key] = value
    elif isinstance(file_content, list):
        file_content.append(value)
    else:
        raise pirate_error(
            "The data found in that file cannot be read"
        )
    with open(filename, 'w') as file_output_object:
        json.dump(file_content, file_output_object, sort_keys=True, indent=4, separators=(',', ': '), skipkeys=True)

# Creates the file if it is not already there
def read_file(filename):
    with open(filename, 'r') as file_object:
        return json.loads(file_object.read() or '{}')


def pull_flag(arg_list, flag_list):
    flag_dict = []
    custom_arg_list = []
    output_list = []
    for arg in arg_list:
        if str.lower(arg) in flag_list:
            flag_dict.append(arg)
        else:
            custom_arg_list.append(arg)
    count = 0
    for i in custom_arg_list:
        try:
            output_list.append((flag_dict[count], custom_arg_list[count]))
        except:
            raise pirate_error("Missing Required Argument Exception")
        count + 1
    if len(output_list) == 0:
        return None
    return output_list


def _resolve_member_id(ctx, input):
    match = re.match('<@!?([0-9]+)>', id)

    if match is not None:
        user_id = int(match.groups(1))
        return user_id

    return input


class Nominee:

    def __init__(self, ctx, list, user_id: int, user_object):
        self.whois = user_object
        self.key = str(user_id)
        self.roles = list


def get_nominee(ctx, user_id: str, user_object):
    nominees = read_file("data/elections.Json")
    temp_dict = nominees[user_id]
    return Nominee(ctx=ctx, list=temp_dict, user_id=user_id,
                   user_object=user_object)


def add_nominee(nominee_id: str, role_id: str):
    temp_dict = [{
        "nominee_role_id": role_id,
        "votes": []
    }]
    x = read_file("data/elections.Json")
    x[nominee_id] = temp_dict
    with open("data/elections.Json", 'w') as file_output_object:
        json.dump(x, file_output_object, indent=4)


async def update_nominations(ctx, message):
    x = read_file('data/elections.Json')
    temp = ""
    for i in x.keys():
        embed = discord.Embed(title="Election ballots")
        if i != "message":
            nom = get_nominee(ctx, i, ctx.guild.get_member(int(i)))
            role_list = []
            for role_id in nom.roles: role_list.append(ctx.guild.get_role(int(role_id['nominee_role_id'])))
            list_names = ""
            for wxz in role_list:
                list_names += wxz.name + " "
            temp += '@' + nom.whois.display_name + ' - ' + " " + list_names + "\n"
    if temp == "":
        temp = "N/A"
    embed.add_field(name="Nominations", value=temp)
    await message.edit(message="_ _", embed=embed)
    await ctx.send("Succesfully nominated user")
