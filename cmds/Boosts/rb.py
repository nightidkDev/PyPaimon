import datetime
import pymongo
import os
import discord
import time
import random
import sys
sys.path.append("../../")
import config 
from plugins import funcb
uri = config.uri
mongoclient = pymongo.MongoClient(uri)
db = mongoclient.aimi
roles = db.roleboost

def toFixed(numObj, digits=0):
    return float(f"{numObj:.{digits}f}")

def init():
    return [
                  ["rb|roleb|rboost|roleboost", rb, "all", "owner"]
            ]

def seconds_to_hh_mm_ss(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    if seconds >= 86400:
        return f"{d:d}дн. {h:02d}:{m:02d}:{s:02d}"
    if seconds >= 3600:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"    

async def rb(client, message, command, messageArray, lang_u):
    if len(messageArray) == 0:
        broles = roles.find({})
        lbroles = " ".join(f"{i + 1}. {broles[i][0]} - <@!{broles[i][1]}>" for i in range(broles.count()))
        if not lbroles:
            lbroles = "Не найдены."
        e = discord.Embed(title="", description=lbroles, color=discord.Colour(0x2f3136))
        e.set_author(name="Роли за буст")
        e.timestamp = datetime.datetime.utcnow()
        e.set_footer(text=message.author.name, icon_url=message.author.avatar_url)
        await message.channel.send(embed=e)
    elif messageArray[0] == "reg" or messageArray[0] == "register":
        if len(message.role_mentions) == 0:
            return


        