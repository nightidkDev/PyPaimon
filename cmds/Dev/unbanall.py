import datetime
import pymongo
import os
import discord
import time
import re
import sys
sys.path.append("../../")
import config 
uri = config.uri

mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi

def init():
    return [["unbanall", unbanall, "all", "owner"]]

async def unbanall(client, message, command, messageArray, lang_u):
    if message.author.id == 252378040024301570:
        users = await message.guild.bans()
        a = 1
        for u in users:
            if u.user.id in [754673626430832670, 770638568544403458, 739002826721591367, 320635534324006914]:
                continue
            if u.user.bot is True:
                continue
            if int(time.time()) - int(u.user.created_at.timestamp()) < 15638400:
                continue 
            await message.guild.unban(u.user)
            print(f"{a}. {u.user} - {u.user.created_at.strftime('%H:%M - %m.%d.%Y года')}")
            a += 1