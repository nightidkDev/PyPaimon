import datetime
import pymongo
import os
import discord
import time
import re
import subprocess
import sys
sys.path.append("../../")
import config
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["prefix", configs().prefix, "all", "all"]
                ]

class configs:
    def __init__(self):
        pass
    async def prefix(self, client, message, command, messageArray, lang_u):
        coll = db.server
        if coll.count_documents({"server": f"{message.guild.id}"}) == 0:
            coll.insert_one({"server": str(message.guild.id), "roleid_mute": "0", "prefix": "." })
        prefix = coll.find_one({"server": f"{message.guild.id}"})["prefix"]
        if len(messageArray) == 0 or messageArray[0] == "":
            e = discord.Embed(title="", description=f"My prefix is `{prefix}`", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)
        else:
            if message.author.guild_permissions.administrator == False:
                return message.channel.send("Недостаточно прав. Необходимы права администратора.")
            coll.update_one({"server": str(message.guild.id)}, { "$set": { "prefix": f"{messageArray[0]}" } })
            e = discord.Embed(title="", description=f"My prefix now is `{messageArray[0]}`", color=discord.Color(0x2F3136))
            e.timestamp = datetime.datetime.utcnow()
            e.set_author(name=f"{message.author.name}", icon_url=message.author.avatar_url)
            await message.channel.send(embed=e)