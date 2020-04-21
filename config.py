token_const = "NzAxOTU4NDc3NjUxNzcxNDAz.Xp5POA.yjVjWeOcEIhWHBVfrvYl524RItc"
prefix_var = "p!"
admin_list = [489561787717648394, 497582475091116042, 331431342438875137]
topic_message = "New topic: {0}"

class bot_config:
    def __init__(self, token, prefix, admins, default_topic):
        self.token = token
        self.prefix = prefix
        self.admins = admins
        self.default_topic_message = default_topic
        
        
def get_config():
    return bot_config(token=token_const, prefix=prefix_var, admins=admin_list, default_topic=topic_message)