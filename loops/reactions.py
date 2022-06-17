import discord
from discord.ext import commands
from discord_components import *
import datetime
import time
import random
import os
import sys
sys.path.append("../../")
import config

# DataBase
import pymongo
login_url = config.uri2
mongoclient = pymongo.MongoClient(login_url)
db = mongoclient.aimi
reactionsdb = db.reactions

async def reactions(bot):
    for react in reactionsdb.find():
        x = int(time.time())
        if react["time"] <= x:
            guild = bot.get_guild(int(react["guild_id"]))
            channel = guild.get_channel(int(react["channel_id"]))
            try:
                message = await channel.fetch_message(int(react["message_id"]))
                await message.edit(components=[])
            except:
                pass
            reactionsdb.delete_one({ "message_id": react["message_id"], "guild_id": react["guild_id"] })