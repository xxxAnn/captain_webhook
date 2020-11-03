from secret import token_const # token_const must be your token
import discord  # version 1.3.2
from discord.ext.commands import Bot
from discord.ext.commands import CommandNotFound
from discord.ext.commands import has_permissions
prefix_var = "p!"
admin_list = [497582475091116042, 331431342438875137, 108792533823320064]
moderator_list = [453380154501234688, 101063847904841728, 108792533823320064, 533775630458683393, 421338370757754880, 666466785771520020, 301912018707808257, 356996895366840321, 147529721893224448]
topic_message = "{0}"
log_channel = 702588387390914651


class bot_config:
    __instance = None
    @staticmethod
    def getInstance():
        if bot_config.__instance == None:
            bot_config(token= token_const, prefix=prefix_var, admins=admin_list, default_topic=topic_message)
        return bot_config.__instance
    def __init__(self, token, prefix, admins, default_topic):
        self.prefix = prefix
        self.logs = log_channel
        self.token = token
        self.guild = None
        self.admins = admins
        self.moderators = moderator_list
        self.default_topic_message = default_topic
        self.client = Bot(command_prefix=self.prefix, case_insensitive=True,chunk_guilds_at_startup=False)
        bot_config.__instance = self
        
        
def get_config():
    return bot_config.getInstance()
