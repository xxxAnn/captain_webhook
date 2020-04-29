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
    with open('data/topics.Json', 'r') as topic_file:
        topic_list = json.load(topic_file)
    topic_file.close()
    topic_list.append(topic)
    with open('data/topics.Json', 'w') as topic_file_output:
        json.dump(topic_list, topic_file_output)


def write_file(filename, value, key=None):
    with open(filename, 'r') as file_object:
        file_content = json.load(file_object)
    file_object.close()
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


def read_file(filename):
    with open(filename, 'r') as file_object:
        return json.load(file_object)


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

    def __init__(self, vote_list, nominated_for, ctx, user_id: int, user_object):
        print(user_id)
        self.whois = user_object
        print(self.whois)
        self.key = str(user_id)
        self.votes = vote_list
        self.for_role = nominated_for

    def votes_aye(self):
        votes_aye = 0
        for vote in self.votes: votes_aye += (1 if vote["vote"] is True else 0)
        return votes_aye

    def votes_nay(self):
        votes_nay = 0
        for vote in self.votes: votes_aye += (1 if vote["vote"] is False else 0)
        return votes_nay

    def vote(self, voter, vote: bool):
        data = read_file("elections.Json")
        temp_list = {"voter_id": voter.id, "vote": vote}
        data[self.key]["vote"].append(temp_list)
        with open("elections.Json", 'w') as file_output_object:
            json.dump(data, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))

    def votes(self):
        return self.votes_aye() - self.votes_nay()


def get_nominee(ctx, user_id: str, user_object):
    nominees = read_file("data/elections.Json")
    temp_dict = nominees[user_id]
    return Nominee(ctx=ctx, vote_list=temp_dict["votes"], nominated_for=temp_dict["nominee_role_id"], user_id=user_id,
                   user_object=user_object)


def add_nominee(nominee_id: str, role_id: str):
    temp_dict = {"nominee_role_id": [role_id],
                 "votes": [
                 ]}
    x = read_file("data/elections.Json")
    x[nominee_id] = temp_dict
    with open("data/elections.Json", 'w') as file_output_object:
        json.dump(x, file_output_object, indent=4)
