import datetime
import discord
from discord.ext import commands
import pymongo
import config
import json
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
clans = db.clans
users = db.prof_ec_users



class BannerCounter(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return
        if message.guild.id != 604083589570625555:
            return
        with open("./banner_info.json") as f:
            config2 = json.load(f)
        config2["banner_counter_messages"] += 1
        with open("./banner_info.json", "w") as f:
            json.dump(config2, f)

def setup(bot):
    bot.add_cog(BannerCounter(bot))