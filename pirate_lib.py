import json
import random


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
    with open('topics.Json', 'r') as topic_file:
        topic_list = json.load(topic_file)
        return random.choice(topic_list)


def append_topic(topic):
    with open('topics.Json', 'r') as topic_file:
        topic_list = json.load(topic_file)
    topic_file.close()
    topic_list.append(topic)
    with open('topics.Json', 'w') as topic_file_output:
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
        json.dump(file_content, file_output_object, sort_keys=True, indent=4, separators=(',', ': '))


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
        count+1
    if len(output_list) == 0:
        return None
    return output_list


def _resolve_member_id(ctx, input):
    match = re.match('<@!?([0-9]+)>', id)

    if match is not None:
        user_id = int(match.groups(1))
        return user_id

    return input



