import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["admins", admins, "all", "owner"]]

async def admins(client, message, command, messageArray, lang_u):
    if message.author.id == 252378040024301570:
        if len(messageArray) == 0 or messageArray[0] == "":
            adm = "\n".join(f"<@!{id}>" for id in config.ADMINS)
            e = discord.Embed(title="Admins", description=adm, color=discord.Color(0x2F3136))
            await message.channel.send(embed=e)
        elif messageArray[0] == "add":
            config.ADMINS.append(str(messageArray[1]))
        elif messageArray[0] == "remove":
            config.ADMINS.remove(str(messageArray[1]))