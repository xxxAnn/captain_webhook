import json
import random


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
